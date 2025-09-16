= Example Cloud-Init CRD configuration files for Harvester/SUSE Virtualization =

These files automate the configuration of a Harvester/SUSE Virtualization cluster nodes.
More details here: https://documentation.suse.com/cloudnative/virtualization/v1.5/en/installation-setup/config/cloudinitcrd.html

So far I have developed/used these:
* add-disks-harvester.yaml: this configures multipathd for all nodes, with a specific vendor/product filter, and also adds a fstab entry for the first dm-0 drive.
* cloudinit-setproxy.yaml: this sets the global HTTP proxy for Harvester. Useful if you're trying to download stuff from the internet, like a CSI driver, and the server is behind a proxy.
* cloudinit-specific-wwn-enable-multipathd.yaml: this does the same as the first one, but maps out specific WWNs to each node. This is useful if multiple LUNs are being presented to a group of machines, and you only want to enable an individual one per node. It uses the hostname label to select the proper nodes.
* setting-proxy.yaml: this is a local "setting" object that can be applied to change the HTTP proxy configuration locally (i.e. for a single node).


