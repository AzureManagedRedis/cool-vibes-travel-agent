targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

// Optional parameters
@description('Azure OpenAI SKU')
param openAiSkuName string = 'S0'

@description('Azure OpenAI Model Name')
param openAiModelName string = 'gpt-4o'

@description('Azure OpenAI Model Version')
param openAiModelVersion string = '2024-11-20'

@description('Azure OpenAI Model Capacity')
param openAiModelCapacity int = 10

@description('Azure OpenAI Embedding Model Name')
param openAiEmbeddingModelName string = 'text-embedding-ada-002'

@description('Azure OpenAI Embedding Model Version')
param openAiEmbeddingModelVersion string = '2'

@description('Azure OpenAI Embedding Model Capacity')
param openAiEmbeddingModelCapacity int = 10

@description('Azure Managed Redis SKU')
@allowed([
  'Balanced_B0'
  'Balanced_B1'
  'Balanced_B3'
  'Balanced_B5'
  'Balanced_B10'
  'Balanced_B20'
  'Balanced_B50'
  'ComputeOptimized_X5'
  'ComputeOptimized_X10'
  'ComputeOptimized_X20'
  'ComputeOptimized_X50'
  'MemoryOptimized_M10'
  'MemoryOptimized_M20'
  'MemoryOptimized_M50'
])
param redisSku string = 'Balanced_B1'

@description('Container CPU cores')
param containerCpuCoreCount string = '1.0'

@description('Container memory in GB')
param containerMemory string = '2.0Gi'

@description('Container max replicas')
param containerMaxReplicas int = 10

@description('Container min replicas')
param containerMinReplicas int = 1

// Tags to apply to all resources
var tags = {
  'azd-env-name': environmentName
  'app-name': 'cool-vibes-travel-agent'
}

// Generate a unique token to be used in naming resources
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))

// Organize resources in a resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: 'rg-${environmentName}'
  location: location
  tags: tags
}

// Log Analytics workspace for monitoring
module logAnalytics './core/monitor/loganalytics.bicep' = {
  name: 'loganalytics'
  scope: rg
  params: {
    name: 'log-${resourceToken}'
    location: location
    tags: tags
  }
}

// Application Insights for application monitoring
module applicationInsights './core/monitor/applicationinsights.bicep' = {
  name: 'applicationinsights'
  scope: rg
  params: {
    name: 'appi-${resourceToken}'
    location: location
    tags: tags
    logAnalyticsWorkspaceId: logAnalytics.outputs.id
  }
}

// Container Apps Environment
module containerAppsEnvironment './core/host/container-apps-environment.bicep' = {
  name: 'container-apps-environment'
  scope: rg
  params: {
    name: 'cae-${resourceToken}'
    location: location
    tags: tags
    logAnalyticsWorkspaceId: logAnalytics.outputs.id
  }
}

// Azure OpenAI Service
module openAi './core/ai/cognitiveservices.bicep' = {
  name: 'openai'
  scope: rg
  params: {
    name: 'oai-${resourceToken}'
    location: location
    tags: tags
    sku: {
      name: openAiSkuName
    }
    deployments: [
      {
        name: openAiModelName
        model: {
          format: 'OpenAI'
          name: openAiModelName
          version: openAiModelVersion
        }
        sku: {
          name: 'Standard'
          capacity: openAiModelCapacity
        }
      }
      {
        name: openAiEmbeddingModelName
        model: {
          format: 'OpenAI'
          name: openAiEmbeddingModelName
          version: openAiEmbeddingModelVersion
        }
        sku: {
          name: 'Standard'
          capacity: openAiEmbeddingModelCapacity
        }
      }
    ]
  }
}

// Azure Managed Redis (Cache for Redis Enterprise)
module redis './core/database/redis.bicep' = {
  name: 'redis'
  scope: rg
  params: {
    name: 'redis-${resourceToken}'
    location: location
    tags: tags
    sku: redisSku
    logAnalyticsWorkspaceId: logAnalytics.outputs.id
  }
}

// Container registry
module containerRegistry './core/host/container-registry.bicep' = {
  name: 'container-registry'
  scope: rg
  params: {
    name: 'cr${resourceToken}'
    location: location
    tags: tags
  }
}

// The application container
module app './core/host/container-app.bicep' = {
  name: 'app'
  scope: rg
  params: {
    name: 'ca-${resourceToken}'
    location: location
    tags: union(tags, { 'azd-service-name': 'web' })
    containerAppsEnvironmentId: containerAppsEnvironment.outputs.id
    containerRegistryName: containerRegistry.outputs.name
    containerCpuCoreCount: containerCpuCoreCount
    containerMemory: containerMemory
    containerMaxReplicas: containerMaxReplicas
    containerMinReplicas: containerMinReplicas
    env: [
      {
        name: 'REDIS_URL'
        value: redis.outputs.connectionString
      }
      {
        name: 'AZURE_OPENAI_ENDPOINT'
        value: openAi.outputs.endpoint
      }
      {
        name: 'AZURE_OPENAI_API_KEY'
        secretRef: 'openai-api-key'
      }
      {
        name: 'AZURE_OPENAI_API_VERSION'
        value: 'preview'
      }
      {
        name: 'AZURE_OPENAI_DEPLOYMENT_NAME'
        value: openAiModelName
      }
      {
        name: 'AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME'
        value: openAiEmbeddingModelName
      }
      {
        name: 'AZURE_OPENAI_EMBEDDING_API_VERSION'
        value: '2024-02-15-preview'
      }
      {
        name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
        value: applicationInsights.outputs.connectionString
      }
    ]
    secrets: [
      {
        name: 'openai-api-key'
        value: openAi.outputs.key
      }
    ]
    targetPort: 8000
  }
}

// Grant Container App managed identity access to pull from ACR
module acrAccess './core/security/acr-access.bicep' = {
  name: 'acr-access'
  scope: rg
  params: {
    containerRegistryId: containerRegistry.outputs.id
    principalId: app.outputs.identityPrincipalId
  }
}

// Outputs for azd
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = rg.name

output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.loginServer
output AZURE_CONTAINER_REGISTRY_NAME string = containerRegistry.outputs.name

output AZURE_OPENAI_ENDPOINT string = openAi.outputs.endpoint
output AZURE_OPENAI_DEPLOYMENT_NAME string = openAiModelName

output REDIS_HOST string = redis.outputs.hostName
output REDIS_PORT string = redis.outputs.sslPort

output APPLICATIONINSIGHTS_CONNECTION_STRING string = applicationInsights.outputs.connectionString

output SERVICE_WEB_IDENTITY_PRINCIPAL_ID string = app.outputs.identityPrincipalId
output SERVICE_WEB_NAME string = app.outputs.name
output SERVICE_WEB_URI string = app.outputs.uri
output SERVICE_WEB_IMAGE_NAME string = app.outputs.imageName
