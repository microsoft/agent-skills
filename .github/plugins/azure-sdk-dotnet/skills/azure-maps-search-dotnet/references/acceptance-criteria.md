# Azure Maps Search SDK Acceptance Criteria (.NET)

**SDK**: `Azure.Maps.Search`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/maps/Azure.Maps.Search
**NuGet Package**: https://www.nuget.org/packages/Azure.Maps.Search
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Imports

### 1.1 ✅ CORRECT: Client Imports
```csharp
using Azure.Maps.Search;
using Azure.Maps.Search.Models;
using Azure;
using Azure.Core.GeoJson;
```

### 1.2 ✅ CORRECT: Authentication Imports
```csharp
using Azure.Identity;
using Azure.Core;
using Azure.ResourceManager;
using Azure.ResourceManager.Maps;
using Azure.ResourceManager.Maps.Models;
```

### 1.3 ❌ INCORRECT: Wrong import paths
```csharp
// WRONG - old package namespace
using Microsoft.Azure.Maps;

// WRONG - no sub-namespaces for client
using Azure.Maps.Search.Client;
```

---

## 2. Authentication

### 2.1 ✅ CORRECT: Shared Key Authentication (Subscription Key)
```csharp
AzureKeyCredential credential = new AzureKeyCredential(
    Environment.GetEnvironmentVariable("AZURE_MAPS_SUBSCRIPTION_KEY")
    ?? throw new InvalidOperationException("AZURE_MAPS_SUBSCRIPTION_KEY not set"));

MapsSearchClient client = new MapsSearchClient(credential);
```

### 2.2 ✅ CORRECT: Microsoft Entra ID Authentication
```csharp
DefaultAzureCredential credential = new DefaultAzureCredential();
string clientId = Environment.GetEnvironmentVariable("AZURE_MAPS_CLIENT_ID")
    ?? throw new InvalidOperationException("AZURE_MAPS_CLIENT_ID not set");

MapsSearchClient client = new MapsSearchClient(credential, clientId);
```

### 2.3 ✅ CORRECT: SAS Token Authentication
```csharp
// Get SAS token from Azure Resource Manager
TokenCredential cred = new DefaultAzureCredential();
ArmClient armClient = new ArmClient(cred);

string subscriptionId = "your-subscription-id";
string resourceGroupName = "your-resource-group";
string accountName = "your-maps-account";

ResourceIdentifier mapsAccountResourceId = MapsAccountResource.CreateResourceIdentifier(
    subscriptionId, resourceGroupName, accountName);
MapsAccountResource mapsAccount = armClient.GetMapsAccountResource(mapsAccountResourceId);

string principalId = "your-managed-identity-object-id";
DateTime now = DateTime.Now;
string start = now.ToString("O");
string expiry = now.AddDays(1).ToString("O");

MapsAccountSasContent sasContent = new MapsAccountSasContent(
    MapsSigningKey.PrimaryKey, principalId, 500, start, expiry);
Response<MapsAccountSasToken> sas = mapsAccount.GetSas(sasContent);

AzureSasCredential sasCredential = new AzureSasCredential(sas.Value.AccountSasToken);
MapsSearchClient client = new MapsSearchClient(sasCredential);
```

### 2.4 ❌ INCORRECT: Hardcoded credentials
```csharp
// WRONG - hardcoded subscription key
MapsSearchClient client = new MapsSearchClient(
    new AzureKeyCredential("your-hardcoded-key"));
```

---

## 3. Geocoding (Address to Coordinates)

### 3.1 ✅ CORRECT: Basic Geocoding
```csharp
Response<GeocodingResponse> result = client.GetGeocoding("1 Microsoft Way, Redmond, WA 98052");

for (int i = 0; i < result.Value.Features.Count; i++)
{
    Console.WriteLine($"Coordinate: {string.Join(",", result.Value.Features[i].Geometry.Coordinates)}");
}
```

### 3.2 ✅ CORRECT: Geocoding with Options
```csharp
var options = new GetGeocodingOptions
{
    Query = "Space Needle",
    Top = 5
};

Response<GeocodingResponse> result = client.GetGeocoding(options);

foreach (var feature in result.Value.Features)
{
    var coords = feature.Geometry.Coordinates;
    Console.WriteLine($"Name: {feature.Properties.Address.FormattedAddress}");
    Console.WriteLine($"Coordinates: {coords[0]}, {coords[1]}");
}
```

### 3.3 ❌ INCORRECT: Using old method names
```csharp
// WRONG - old method names from previous SDK versions
var result = client.SearchAddress("1 Microsoft Way");
var result = client.FuzzySearch("Space Needle");
```

---

## 4. Batch Geocoding

### 4.1 ✅ CORRECT: Geocoding Batch Request
```csharp
List<GeocodingQuery> queries = new List<GeocodingQuery>
{
    new GeocodingQuery()
    {
        Query = "15171 NE 24th St, Redmond, WA 98052, United States"
    },
    new GeocodingQuery()
    {
        AddressLine = "400 Broad St",
        Locality = "Seattle",
        AdminDistrict = "WA"
    },
};

Response<GeocodingBatchResponse> results = client.GetGeocodingBatch(queries);

for (var i = 0; i < results.Value.BatchItems.Count; i++)
{
    foreach (var feature in results.Value.BatchItems[i].Features)
    {
        Console.WriteLine($"Coordinates: {string.Join(",", feature.Geometry.Coordinates)}");
    }
}
```

### 4.2 ❌ INCORRECT: Not using batch for multiple queries
```csharp
// WRONG - inefficient, should use batch
foreach (var address in addresses)
{
    var result = client.GetGeocoding(address);
    // Process result
}
```

---

## 5. Reverse Geocoding (Coordinates to Address)

### 5.1 ✅ CORRECT: Basic Reverse Geocoding
```csharp
GeoPosition coordinates = new GeoPosition(-122.138685, 47.6305637);

Response<GeocodingResponse> result = client.GetReverseGeocoding(coordinates);

for (int i = 0; i < result.Value.Features.Count; i++)
{
    Console.WriteLine(result.Value.Features[i].Properties.Address.FormattedAddress);
}
```

### 5.2 ✅ CORRECT: Reverse Geocoding with Result Types
```csharp
var options = new GetReverseGeocodingOptions
{
    Coordinates = new GeoPosition(-122.349309, 47.620498),
    ResultTypes = new List<ReverseGeocodingResultTypeEnum>
    {
        ReverseGeocodingResultTypeEnum.Address,
        ReverseGeocodingResultTypeEnum.Neighborhood
    }
};

Response<GeocodingResponse> result = client.GetReverseGeocoding(options);
```

### 5.3 ❌ INCORRECT: Swapped coordinate order
```csharp
// WRONG - GeoPosition is (longitude, latitude), not (latitude, longitude)
GeoPosition coordinates = new GeoPosition(47.6305637, -122.138685);
```

---

## 6. Batch Reverse Geocoding

### 6.1 ✅ CORRECT: Reverse Geocoding Batch
```csharp
List<ReverseGeocodingQuery> items = new List<ReverseGeocodingQuery>
{
    new ReverseGeocodingQuery()
    {
        Coordinates = new GeoPosition(-122.349309, 47.620498)
    },
    new ReverseGeocodingQuery()
    {
        Coordinates = new GeoPosition(-122.138679, 47.630356),
        ResultTypes = new List<ReverseGeocodingResultTypeEnum>
        {
            ReverseGeocodingResultTypeEnum.Address,
            ReverseGeocodingResultTypeEnum.Neighborhood
        }
    },
};

Response<GeocodingBatchResponse> result = client.GetReverseGeocodingBatch(items);

for (var i = 0; i < result.Value.BatchItems.Count; i++)
{
    var feature = result.Value.BatchItems[i].Features[0];
    Console.WriteLine($"Address: {feature.Properties.Address.AddressLine}");
    Console.WriteLine($"Neighborhood: {feature.Properties.Address.Neighborhood}");
}
```

---

## 7. Get Polygon (Boundary Data)

### 7.1 ✅ CORRECT: Get Polygon for Location
```csharp
GetPolygonOptions options = new GetPolygonOptions()
{
    Coordinates = new GeoPosition(-122.204141, 47.61256),
    ResultType = BoundaryResultTypeEnum.Locality,
    Resolution = ResolutionEnum.Small,
};

Response<Boundary> result = client.GetPolygon(options);

Console.WriteLine($"Copyright: {result.Value.Properties?.Copyright}");
Console.WriteLine($"Polygon count: {result.Value.Geometry.Count}");

// Access polygon coordinates
if (result.Value.Geometry[0] is GeoPolygon polygon)
{
    foreach (var coordinate in polygon.Coordinates[0])
    {
        Console.WriteLine($"{coordinate.Latitude:N5}, {coordinate.Longitude:N5}");
    }
}
```

### 7.2 ✅ CORRECT: Different Boundary Types
```csharp
// Get country boundary
var countryOptions = new GetPolygonOptions()
{
    Coordinates = new GeoPosition(-122.204141, 47.61256),
    ResultType = BoundaryResultTypeEnum.CountryRegion,
    Resolution = ResolutionEnum.Large,
};

// Get administrative district boundary
var adminOptions = new GetPolygonOptions()
{
    Coordinates = new GeoPosition(-122.204141, 47.61256),
    ResultType = BoundaryResultTypeEnum.AdminDistrict,
    Resolution = ResolutionEnum.Medium,
};
```

---

## 8. Async Operations

### 8.1 ✅ CORRECT: Async Geocoding
```csharp
Response<GeocodingResponse> result = await client.GetGeocodingAsync("1 Microsoft Way, Redmond, WA");

foreach (var feature in result.Value.Features)
{
    Console.WriteLine($"Address: {feature.Properties.Address.FormattedAddress}");
}
```

### 8.2 ✅ CORRECT: Async Batch Operations
```csharp
List<GeocodingQuery> queries = new List<GeocodingQuery>
{
    new GeocodingQuery { Query = "Space Needle, Seattle" },
    new GeocodingQuery { Query = "Pike Place Market, Seattle" },
};

Response<GeocodingBatchResponse> results = await client.GetGeocodingBatchAsync(queries);
```

### 8.3 ❌ INCORRECT: Blocking on async
```csharp
// WRONG - using .Result instead of await
var result = client.GetGeocodingAsync("address").Result;

// WRONG - using .Wait()
client.GetGeocodingAsync("address").Wait();
```

---

## 9. Error Handling

### 9.1 ✅ CORRECT: Handle RequestFailedException
```csharp
try
{
    Response<GeocodingResponse> result = await client.GetGeocodingAsync("invalid address query");
    // Process results
}
catch (RequestFailedException ex) when (ex.Status == 400)
{
    Console.WriteLine($"Invalid request: {ex.Message}");
}
catch (RequestFailedException ex) when (ex.Status == 401)
{
    Console.WriteLine($"Authentication failed: {ex.Message}");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Maps API error ({ex.Status}): {ex.Message}");
}
```

### 9.2 ✅ CORRECT: Handle Empty Results
```csharp
Response<GeocodingResponse> result = await client.GetGeocodingAsync("nonexistent place xyz123");

if (result.Value.Features.Count == 0)
{
    Console.WriteLine("No results found for the query.");
}
else
{
    // Process results
}
```

### 9.3 ❌ INCORRECT: Swallowing exceptions
```csharp
// WRONG - empty catch block
try
{
    var result = await client.GetGeocodingAsync(query);
}
catch { }
```

---

## 10. Best Practices

### 10.1 ✅ CORRECT: Reuse Client Instance
```csharp
public class MapsService
{
    private readonly MapsSearchClient _client;
    
    public MapsService()
    {
        var credential = new AzureKeyCredential(
            Environment.GetEnvironmentVariable("AZURE_MAPS_SUBSCRIPTION_KEY")
            ?? throw new InvalidOperationException("AZURE_MAPS_SUBSCRIPTION_KEY not set"));
        _client = new MapsSearchClient(credential);
    }
    
    public async Task<GeocodingResponse> GeocodeAddressAsync(string address)
    {
        var result = await _client.GetGeocodingAsync(address);
        return result.Value;
    }
    
    public async Task<GeocodingResponse> ReverseGeocodeAsync(double longitude, double latitude)
    {
        var result = await _client.GetReverseGeocodingAsync(new GeoPosition(longitude, latitude));
        return result.Value;
    }
}
```

### 10.2 ✅ CORRECT: Use Batch for Multiple Queries
```csharp
// Efficient - batch multiple queries
public async Task<List<GeoPosition>> GeocodeMultipleAsync(List<string> addresses)
{
    var queries = addresses.Select(a => new GeocodingQuery { Query = a }).ToList();
    var results = await _client.GetGeocodingBatchAsync(queries);
    
    return results.Value.BatchItems
        .SelectMany(item => item.Features)
        .Select(f => new GeoPosition(f.Geometry.Coordinates[0], f.Geometry.Coordinates[1]))
        .ToList();
}
```

### 10.3 ❌ INCORRECT: Creating client per request
```csharp
// WRONG - wasteful to create client for each request
public async Task<GeocodingResponse> GeocodeAsync(string address)
{
    var client = new MapsSearchClient(new AzureKeyCredential(key));
    var result = await client.GetGeocodingAsync(address);
    return result.Value;
}
```

---

## 11. Coordinate System Notes

### 11.1 ✅ CORRECT: GeoPosition Order
```csharp
// GeoPosition uses (longitude, latitude) order
// This is consistent with GeoJSON standard
GeoPosition seattle = new GeoPosition(-122.3321, 47.6062);  // longitude, latitude

// When accessing coordinates from response
var coords = feature.Geometry.Coordinates;
double longitude = coords[0];
double latitude = coords[1];
```

### 11.2 ❌ INCORRECT: Latitude/Longitude Order Confusion
```csharp
// WRONG - reversed order (latitude, longitude)
GeoPosition seattle = new GeoPosition(47.6062, -122.3321);
```

---

## 12. Address Components

### 12.1 ✅ CORRECT: Access Address Parts
```csharp
Response<GeocodingResponse> result = await client.GetGeocodingAsync("1 Microsoft Way, Redmond, WA");

foreach (var feature in result.Value.Features)
{
    var address = feature.Properties.Address;
    
    Console.WriteLine($"Street: {address.AddressLine}");
    Console.WriteLine($"City: {address.Locality}");
    Console.WriteLine($"State: {address.AdminDistrict}");
    Console.WriteLine($"Postal Code: {address.PostalCode}");
    Console.WriteLine($"Country: {address.CountryRegion?.Name}");
    Console.WriteLine($"Formatted: {address.FormattedAddress}");
}
```

### 12.2 ✅ CORRECT: Structured Address Query
```csharp
var query = new GeocodingQuery
{
    AddressLine = "400 Broad St",
    Locality = "Seattle",
    AdminDistrict = "WA",
    CountryRegion = "US"
};

var queries = new List<GeocodingQuery> { query };
Response<GeocodingBatchResponse> result = await client.GetGeocodingBatchAsync(queries);
```
