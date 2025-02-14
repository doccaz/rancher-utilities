#!/bin/bash
#
# Downloads all offline bundles needed for an air-gap install of RKE2
# Erico Mendonca <erico.mendonca@suse.com>
# Feb 2025
#
VERSION="v1.31.4"
RELEASE="rke2r1"
ARCH="amd64"
BASE_FILES="rke2-images.linux-${ARCH}.tar.zst rke2.linux-${ARCH}.tar.gz rke2-images-core.linux-${ARCH}.tar.zst sha256sum-${ARCH}.txt"
CNI_FILES="rke2-images-calico.linux-${ARCH}.tar.zst rke2-images-canal.linux-${ARCH}.tar.zst rke2-images-cilium.linux-${ARCH}.tar.zst rke2-images-flannel.linux-${ARCH}.tar.zst rke2-images-multus.linux-${ARCH}.tar.zst"
EXTRA_FILES="rke2-images-traefik.linux-${ARCH}.tar.zst rke2-images-harvester.linux-${ARCH}.tar.zst rke2-images-vsphere.linux-${ARCH}.tar.zst"
OUTDIR="offline-bundle"
SAVEPATH="${OUTDIR}/rke2-artifacts"
ARCHIVE="rke2-${VERSION}-${RELEASE}-offline.tgz"

rm -rf ${OUTDIR}
mkdir -p ${SAVEPATH} && cd ${SAVEPATH}
for f in ${BASE_FILES} ${CNI_FILES} ${EXTRA_FILES}; do
	echo "* downloading ${f}..."
	curl -OL https://github.com/rancher/rke2/releases/download/${VERSION}%2B${RELEASE}/${f}
	if [ $? != 0 ]; then
		echo "*** ERROR downloading file ${f}"
		exit 1
	fi
done

cd ..
echo "* downloading main install script"
curl -sfL https://get.rke2.io --output install.sh

if [ ! -f ./install.sh ]; then
	echo "*** ERROR Main installation script not found"
	exit 1
fi

cat > install_offline.sh <<'EOF'
#!/bin/bash

echo "starting offline install for RKE2..."
INSTALL_RKE2_ARTIFACT_PATH=$(realpath ./rke2-artifacts) sh install.sh
EOF

chmod +x install_offline.sh

echo "* compressing everything into a neat bundle"
cd ..
tar cvzf ${ARCHIVE} ${OUTDIR}/ 

echo "--> Transfer the file ${ARCHIVE} to the host, decompress it and run install_offline.sh to install RKE2."
echo "* Done."

