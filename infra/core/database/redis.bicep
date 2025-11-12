param name string
param location string = resourceGroup().location
param tags object = {}

@description('The SKU for Azure Managed Redis')
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
param sku string = 'Balanced_B1'

@description('Enable RediSearch module')
param enableRediSearch bool = false

@description('Enable RedisJSON module')
param enableRedisJson bool = false

@description('Log Analytics workspace resource ID for diagnostics')
param logAnalyticsWorkspaceId string = ''

// Build modules array - RediSearch and RedisJSON are optional
var modules = concat(
  enableRediSearch ? [{ name: 'RediSearch' }] : [],
  enableRedisJson ? [{ name: 'RedisJSON' }] : []
)

resource redisEnterprise 'Microsoft.Cache/redisEnterprise@2025-04-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: sku
  }
  properties: {
    minimumTlsVersion: '1.2'
  }
}

resource database 'Microsoft.Cache/redisEnterprise/databases@2025-04-01' = {
  parent: redisEnterprise
  name: 'default'
  properties: {
    port: 10000
    clusteringPolicy: 'EnterpriseCluster'
    evictionPolicy: 'NoEviction'
    modules: modules
  }
}

// Diagnostic Settings for Azure Managed Redis
resource redisEnterpriseDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (logAnalyticsWorkspaceId != '') {
  name: '${name}-diagnostics'
  scope: redisEnterprise
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}


output id string = redisEnterprise.id
output name string = redisEnterprise.name
output hostName string = redisEnterprise.properties.hostName
output sslPort string = '10000'
output databaseId string = database.id
output enabledModules array = modules
@secure()
output primaryKey string = database.listKeys().primaryKey
@secure()
output connectionString string = 'rediss://:${database.listKeys().primaryKey}@${redisEnterprise.properties.hostName}:10000'
