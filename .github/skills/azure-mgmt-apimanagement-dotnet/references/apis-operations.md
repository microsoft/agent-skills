# APIs and Operations

Patterns for managing APIs, operations, and schemas.

## Create API from OpenAPI

```csharp
var apiData = new ApiCreateOrUpdateContent
{
    DisplayName = "Pet Store API",
    Path = "petstore",
    Protocols = { ApiOperationInvokableProtocol.Https },
    // Import from OpenAPI spec
    Format = ContentFormat.OpenApiJson,
    Value = File.ReadAllText("petstore-openapi.json"),
    // Or from URL
    // Format = ContentFormat.OpenApiJsonLink,
    // Value = "https://petstore.swagger.io/v2/swagger.json"
};

var api = await service.GetApis()
    .CreateOrUpdateAsync(WaitUntil.Completed, "petstore-api", apiData);
```

## Create API Manually

```csharp
var apiData = new ApiCreateOrUpdateContent
{
    DisplayName = "Custom API",
    Path = "custom",
    Protocols = { ApiOperationInvokableProtocol.Https },
    ServiceUri = new Uri("https://backend.contoso.com"),
    SubscriptionKeyParameterNames = new SubscriptionKeyParameterNamesContract
    {
        Header = "X-API-Key",
        Query = "api-key"
    }
};

var api = await service.GetApis()
    .CreateOrUpdateAsync(WaitUntil.Completed, "custom-api", apiData);
```

## List APIs

```csharp
await foreach (var api in service.GetApis())
{
    Console.WriteLine($"{api.Data.DisplayName}: {api.Data.Path}");
}
```

## Create Operation

```csharp
var operationData = new ApiOperationData
{
    DisplayName = "Get Users",
    Method = "GET",
    UrlTemplate = "/users",
    Description = "Retrieves all users",
    Responses =
    {
        new ResponseContract(200)
        {
            Description = "Success",
            Representations =
            {
                new RepresentationContract("application/json")
            }
        }
    }
};

var operation = await api.Value.GetApiOperations()
    .CreateOrUpdateAsync(WaitUntil.Completed, "get-users", operationData);
```

## Operation with Parameters

```csharp
var operationData = new ApiOperationData
{
    DisplayName = "Get User by ID",
    Method = "GET",
    UrlTemplate = "/users/{userId}",
    TemplateParameters =
    {
        new ParameterContract("userId")
        {
            Description = "User identifier",
            ParameterContractType = "string",
            IsRequired = true
        }
    },
    Request = new RequestContract
    {
        QueryParameters =
        {
            new ParameterContract("include")
            {
                Description = "Related data to include",
                ParameterContractType = "string",
                IsRequired = false
            }
        }
    }
};
```

## API Versioning

```csharp
// Create version set
var versionSetData = new ApiVersionSetData
{
    DisplayName = "My API Versions",
    VersioningScheme = VersioningScheme.Segment // or Header, Query
};

var versionSet = await service.GetApiVersionSets()
    .CreateOrUpdateAsync(WaitUntil.Completed, "my-api-versions", versionSetData);

// Create versioned API
var apiV1Data = new ApiCreateOrUpdateContent
{
    DisplayName = "My API v1",
    Path = "myapi",
    ApiVersion = "v1",
    ApiVersionSetId = versionSet.Value.Id,
    Protocols = { ApiOperationInvokableProtocol.Https }
};

var apiV2Data = new ApiCreateOrUpdateContent
{
    DisplayName = "My API v2",
    Path = "myapi",
    ApiVersion = "v2",
    ApiVersionSetId = versionSet.Value.Id,
    Protocols = { ApiOperationInvokableProtocol.Https }
};
```

## API Revisions

```csharp
// Create revision
var revisionData = new ApiCreateOrUpdateContent
{
    SourceApiId = api.Value.Id,
    Path = api.Value.Data.Path,
    ApiRevisionDescription = "Added new endpoint"
};

var revision = await service.GetApis()
    .CreateOrUpdateAsync(WaitUntil.Completed, "my-api;rev=2", revisionData);

// Make revision current
await revision.Value.UpdateAsync(WaitUntil.Completed, 
    new ApiCreateOrUpdateContent { IsCurrent = true });
```

## Delete API

```csharp
await api.Value.DeleteAsync(WaitUntil.Completed);
```
