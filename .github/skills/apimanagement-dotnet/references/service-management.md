# Service Management

Detailed patterns for managing API Management service instances.

## Get Existing Service

```csharp
// By resource group
var service = await resourceGroup.Value
    .GetApiManagementServiceAsync("my-apim-service");

// By resource ID
var serviceId = ApiManagementServiceResource.CreateResourceIdentifier(
    subscriptionId, "my-resource-group", "my-apim-service");
var service = armClient.GetApiManagementServiceResource(serviceId);
service = await service.GetAsync();
```

## List Services

```csharp
// In resource group
await foreach (var service in resourceGroup.Value.GetApiManagementServices())
{
    Console.WriteLine($"{service.Data.Name}: {service.Data.Location}");
}

// In subscription
await foreach (var service in subscription.GetApiManagementServicesAsync())
{
    Console.WriteLine($"{service.Data.Name}: {service.Data.ResourceGroupName}");
}
```

## Update Service

```csharp
var patch = new ApiManagementServicePatch
{
    PublisherName = "Updated Publisher",
    Tags = { ["environment"] = "production" }
};

var operation = await service.UpdateAsync(WaitUntil.Completed, patch);
```

## Delete Service

```csharp
await service.DeleteAsync(WaitUntil.Completed);
```

## SKU Configuration

```csharp
// Developer (for testing)
var devSku = new ApiManagementServiceSkuProperties(
    ApiManagementServiceSkuType.Developer, capacity: 1);

// Standard with multiple units
var standardSku = new ApiManagementServiceSkuProperties(
    ApiManagementServiceSkuType.Standard, capacity: 2);

// Premium with availability zones
var premiumData = new ApiManagementServiceData(
    location: AzureLocation.EastUS,
    sku: new ApiManagementServiceSkuProperties(
        ApiManagementServiceSkuType.Premium, capacity: 3),
    publisherEmail: "admin@contoso.com",
    publisherName: "Contoso")
{
    Zones = { "1", "2", "3" }
};
```

## Virtual Network Integration

```csharp
var serviceData = new ApiManagementServiceData(
    location: AzureLocation.EastUS,
    sku: new ApiManagementServiceSkuProperties(
        ApiManagementServiceSkuType.Premium, capacity: 1),
    publisherEmail: "admin@contoso.com",
    publisherName: "Contoso")
{
    VirtualNetworkType = VirtualNetworkType.External,
    VirtualNetworkConfiguration = new VirtualNetworkConfiguration
    {
        SubnetResourceId = new ResourceIdentifier(
            "/subscriptions/.../subnets/apim-subnet")
    }
};
```

## Custom Domains

```csharp
var serviceData = new ApiManagementServiceData(...)
{
    HostnameConfigurations =
    {
        new HostnameConfiguration(HostnameType.Proxy)
        {
            HostName = "api.contoso.com",
            CertificateSource = CertificateSource.KeyVault,
            KeyVaultSecretUri = new Uri("https://myvault.vault.azure.net/secrets/api-cert")
        },
        new HostnameConfiguration(HostnameType.DeveloperPortal)
        {
            HostName = "developer.contoso.com",
            CertificateSource = CertificateSource.KeyVault,
            KeyVaultSecretUri = new Uri("https://myvault.vault.azure.net/secrets/portal-cert")
        }
    }
};
```

## Managed Identity

```csharp
var serviceData = new ApiManagementServiceData(...)
{
    Identity = new ManagedServiceIdentity(ManagedServiceIdentityType.SystemAssigned)
};

// Or user-assigned
var serviceData = new ApiManagementServiceData(...)
{
    Identity = new ManagedServiceIdentity(ManagedServiceIdentityType.UserAssigned)
    {
        UserAssignedIdentities =
        {
            [new ResourceIdentifier("/subscriptions/.../userAssignedIdentities/my-identity")] = 
                new UserAssignedIdentity()
        }
    }
};
```

## Get Service Information

```csharp
// Get gateway URL
Console.WriteLine($"Gateway: {service.Data.GatewayUri}");

// Get portal URL
Console.WriteLine($"Portal: {service.Data.DeveloperPortalUri}");

// Get management API URL
Console.WriteLine($"Management: {service.Data.ManagementApiUri}");

// Get provisioning state
Console.WriteLine($"State: {service.Data.ProvisioningState}");
```
