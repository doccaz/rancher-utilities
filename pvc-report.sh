#!/bin/bash

# This script lists PVCs and their associated owners (Deployments or StatefulSets).

echo "NAMESPACE | PVC_NAME | PVC_SIZE | OWNER_KIND | OWNER_NAME"
echo "--- | --- | --- | --- | ---"

# Get all pods that have a PVC
kubectl get pods --all-namespaces -o json | \
jq -c '.items[] | select(.spec.volumes[].persistentVolumeClaim.claimName != null)' | \
while read -r pod_json; do
  # Extract basic pod info
  pod_name=$(echo "$pod_json" | jq -r '.metadata.name')
  namespace=$(echo "$pod_json" | jq -r '.metadata.namespace')
  owner_kind=$(echo "$pod_json" | jq -r '.metadata.ownerReferences[0].kind')
  owner_name=$(echo "$pod_json" | jq -r '.metadata.ownerReferences[0].name')

  # If the owner is a ReplicaSet, get the parent Deployment
  if [ "$owner_kind" == "ReplicaSet" ]; then
    owner_name=$(kubectl get replicaset -n "$namespace" "$owner_name" -o json | jq -r '.metadata.ownerReferences[0].name')
    owner_kind="Deployment"
  fi

  # Extract PVC info for the current pod
  echo "$pod_json" | \
  jq -c '.spec.volumes[] | select(.persistentVolumeClaim.claimName != null)' | \
  while read -r volume_json; do
    pvc_name=$(echo "$volume_json" | jq -r '.persistentVolumeClaim.claimName')
    
    # Get the size of the PVC
    pvc_size=$(kubectl get pvc -n "$namespace" "$pvc_name" -o json | jq -r '.status.capacity.storage')
    
    echo "$namespace | $pvc_name | $pvc_size | $owner_kind | $owner_name"
  done
done | sort -u

