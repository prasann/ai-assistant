param location string = resourceGroup().location
param cosmosDbAccountName string
param databaseName string
param containerName string
param containerPartitionKey string = '/partitionKey'
param containerThroughput int = 400
// param identityName string

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

// resource userIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = if (!empty(identityName)) {
//   name: identityName
// }

// resource cosmosDbRoleAssignment 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
//   name: guid(cosmosDbAccount.id, userIdentity.id, 'CosmosDB Account Reader Role')
//   properties: {
//     principalId: userIdentity.properties.principalId
//     roleDefinitionId: 'b4b9c4c1-4b9f-4e3c-8f8b-1b5f8c1c4b9f' // Cosmos DB Account Reader Role
//   }
// }


output cosmosDbAccountId string = cosmosDbAccount.id
output databaseId string = database.id
output containerId string = container.id
