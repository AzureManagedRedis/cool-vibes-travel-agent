@description('Container Registry resource ID')
param containerRegistryId string

@description('Principal ID of the managed identity that needs ACR pull access')
param principalId string

// Reference the existing container registry
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' existing = {
  name: split(containerRegistryId, '/')[8]
}

// Grant AcrPull role to the Container App's managed identity
resource acrPullRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(containerRegistry.id, principalId, 'AcrPull')
  scope: containerRegistry
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d') // AcrPull role
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

output roleAssignmentId string = acrPullRole.id
