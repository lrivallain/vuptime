param Location string = 'westeurope'
param VMName string = 'TempVM'
param CustomLocation_externalid string = '/subscriptions/<<<TOBEREPLACED>>>/resourceGroups/<<<TOBEREPLACED>>>/providers/Microsoft.ExtendedLocation/customLocations/<<<TOBEREPLACED>>>'
param ResourcePools_externalid string = '/subscriptions/<<<TOBEREPLACED>>>/resourceGroups/<<<TOBEREPLACED>>>/providers/Microsoft.ConnectedVMwarevSphere/ResourcePools/<<<TOBEREPLACED>>>'
param VirtualNetworks_externalid string = '/subscriptions/<<<TOBEREPLACED>>>/resourceGroups/<<<TOBEREPLACED>>>/providers/Microsoft.ConnectedVMwarevSphere/VirtualNetworks/<<<TOBEREPLACED>>>'
param VirtualMachineTemplates__externalid string = '/subscriptions/<<<TOBEREPLACED>>>/resourceGroups/<<<TOBEREPLACED>>>/providers/Microsoft.ConnectedVMwarevSphere/VirtualMachineTemplates/<<<TOBEREPLACED>>>'
param VCenters_externalid string = '/subscriptions/<<<TOBEREPLACED>>>/resourceGroups/<<<TOBEREPLACED>>>/providers/Microsoft.ConnectedVMwarevSphere/VCenters/<<<TOBEREPLACED>>>'

resource VMwVirtualMachines_resource 'Microsoft.ConnectedVMwarevSphere/VirtualMachines@2020-10-01-preview' = {
  name: VMName
  location: Location
  extendedLocation: {
    type: 'CustomLocation'
    name: CustomLocation_externalid
  }
  tags: {
    demo: 'insiders'
    Environment: 'testing'
  }
  kind: 'VMware'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    resourcePoolId: ResourcePools_externalid
    templateId: VirtualMachineTemplates__externalid
    vCenterId: VCenters_externalid
    placementProfile: {
      resourcePoolId: ResourcePools_externalid
    }
    networkProfile: {
      networkInterfaces: [
        {
          name: 'nic1'
          networkId: VirtualNetworks_externalid
          nicType: 'vmxnet3'
          deviceKey: 4000
          powerOnBoot: 'enabled'
          ipSettings: {
            allocationMethod: 'dynamic'
          }
        }
      ]
    }
    storageProfile: {
      disks: [
        {
          name: 'Root'
          diskSizeGB: 11
          deviceKey: 2000
          controllerKey: 1000
          unitNumber: 0
          diskType: 'flat'
        }
      ]
    }
    osProfile: {
      computerName: VMName
      osType: 'Linux'
    }
    hardwareProfile: {
      memorySizeMB: 1024
      numCPUs: 2
      numCoresPerSocket: 1
    }
    firmwareType: 'bios'
    guestAgentProfile: {}
  }
}
