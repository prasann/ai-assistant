param location string = resourceGroup().location
param cosmosDbAccountName string
param databaseName string
param containerName string
param containerPartitionKey string = '/partitionKey'
param containerThroughput int = 400
param acaPrincipalId string
param roleDefinitionId string

resource cosmosDbAccount 'Microsoft.DocumentDB/databaseAccounts@2021-03-15' = {
  name: cosmosDbAccountName
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: location
        failoverPriority: 0
      }
    ]
  }
}

resource database 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2021-03-15' = {
  parent: cosmosDbAccount
  name: databaseName
  properties: {
    resource: {
      id: databaseName
    }
  }
}

resource container 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2021-03-15' = {
  parent: database
  name: containerName
  properties: {
    resource: {
      id: containerName
      partitionKey: {
        paths: [
          containerPartitionKey
        ]
        kind: 'Hash'
      }
      defaultTtl: -1
    }
    options: {
      throughput: containerThroughput
    }
  }
}

resource assignment 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2024-05-15' = {
  name: guid(roleDefinitionId, acaPrincipalId, cosmosDbAccount.id)
  parent: cosmosDbAccount
  properties: {
    principalId: acaPrincipalId
    roleDefinitionId: roleDefinitionId
    scope: cosmosDbAccount.id
  }
}

output cosmosDbAccountId string = cosmosDbAccount.id
output databaseId string = database.id
output containerId string = container.id
