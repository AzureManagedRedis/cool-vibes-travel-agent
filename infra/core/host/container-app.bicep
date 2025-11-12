param name string
param location string = resourceGroup().location
param tags object = {}

@description('Name of the container apps environment')
param containerAppsEnvironmentId string

@description('CPU cores allocated to a single container instance')
param containerCpuCoreCount string = '1.0'

@description('Memory allocated to a single container instance')
param containerMemory string = '2.0Gi'

@description('Maximum number of replicas')
param containerMaxReplicas int = 10

@description('Minimum number of replicas')
param containerMinReplicas int = 1

@description('Container registry name')
param containerRegistryName string = ''

@description('Environment variables')
param env array = []

@description('The name of the user-assigned identity')
param identityName string = ''

@description('The name of the container image')
param imageName string = ''

@description('Ingress enabled')
param ingressEnabled bool = true

@description('Secrets array')
param secrets array = []

@description('The protocol used by ingress')
@allowed(['http', 'http2'])
param ingressTransport string = 'http'

@description('Target port for the container')
param targetPort int = 8000

@description('Expose the app externally')
param external bool = true

resource userIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = if (!empty(identityName)) {
  name: identityName
}

resource app 'Microsoft.App/containerApps@2023-05-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: !empty(identityName) ? 'UserAssigned' : 'SystemAssigned'
    userAssignedIdentities: !empty(identityName) ? { '${userIdentity.id}': {} } : null
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: ingressEnabled ? {
        external: external
        targetPort: targetPort
        transport: ingressTransport
        // Removed CORS policy - can add back after initial deployment
      } : null
      registries: !empty(containerRegistryName) ? [
        {
          server: '${containerRegistryName}.azurecr.io'
          identity: !empty(identityName) ? userIdentity.id : 'system'
        }
      ] : []
      secrets: secrets
    }
    template: {
      containers: [
        {
          image: !empty(imageName) ? imageName : 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          name: 'main'
          env: env
          resources: {
            cpu: json(containerCpuCoreCount)
            memory: containerMemory
          }
        }
      ]
      scale: {
        minReplicas: containerMinReplicas
        maxReplicas: containerMaxReplicas
        rules: [
          {
            name: 'http-rule'
            http: {
              metadata: {
                concurrentRequests: '100'
              }
            }
          }
        ]
      }
    }
  }
}

output name string = app.name
output uri string = ingressEnabled ? 'https://${app.properties.configuration.ingress.fqdn}' : ''
output imageName string = imageName
