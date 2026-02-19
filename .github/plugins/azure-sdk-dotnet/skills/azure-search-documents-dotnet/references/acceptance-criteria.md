# Azure Search Documents SDK Acceptance Criteria (.NET)

**SDK**: `Azure.Search.Documents`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/search/Azure.Search.Documents
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Using Statements

### 1.1 ✅ CORRECT: Core Search Imports
```csharp
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;
```

### 1.2 ✅ CORRECT: With Identity
```csharp
using Azure.Identity;
using Azure.Search.Documents;
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong namespace
```csharp
// WRONG - Azure.Search.Documents not Microsoft.Azure.Search
using Microsoft.Azure.Search;
```

---

## 2. Authentication

### 2.1 ✅ CORRECT: DefaultAzureCredential (Preferred)
```csharp
using Azure.Identity;
using Azure.Search.Documents;

var credential = new DefaultAzureCredential();
var client = new SearchClient(
    new Uri(Environment.GetEnvironmentVariable("SEARCH_ENDPOINT")),
    Environment.GetEnvironmentVariable("SEARCH_INDEX_NAME"),
    credential);
```

### 2.2 ✅ CORRECT: API Key Authentication
```csharp
using Azure;
using Azure.Search.Documents;

var credential = new AzureKeyCredential(
    Environment.GetEnvironmentVariable("SEARCH_API_KEY"));
var client = new SearchClient(
    new Uri(Environment.GetEnvironmentVariable("SEARCH_ENDPOINT")),
    Environment.GetEnvironmentVariable("SEARCH_INDEX_NAME"),
    credential);
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded API key
```csharp
// WRONG - never hardcode API keys
var credential = new AzureKeyCredential("my-api-key-12345");
```

---

## 3. Client Selection

### 3.1 ✅ CORRECT: SearchClient for Queries
```csharp
var searchClient = new SearchClient(endpoint, indexName, credential);
var results = await searchClient.SearchAsync<Hotel>("luxury");
```

### 3.2 ✅ CORRECT: SearchIndexClient for Index Management
```csharp
var indexClient = new SearchIndexClient(endpoint, credential);
await indexClient.CreateOrUpdateIndexAsync(index);
```

### 3.3 ✅ CORRECT: SearchIndexerClient for Indexers
```csharp
var indexerClient = new SearchIndexerClient(endpoint, credential);
await indexerClient.CreateOrUpdateIndexerAsync(indexer);
```

---

## 4. Index Creation

### 4.1 ✅ CORRECT: Using FieldBuilder (Recommended)
```csharp
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;

public class Hotel
{
    [SimpleField(IsKey = true, IsFilterable = true)]
    public string HotelId { get; set; }

    [SearchableField(IsSortable = true)]
    public string HotelName { get; set; }

    [SearchableField(AnalyzerName = LexicalAnalyzerName.EnLucene)]
    public string Description { get; set; }

    [SimpleField(IsFilterable = true, IsSortable = true, IsFacetable = true)]
    public double? Rating { get; set; }

    [VectorSearchField(VectorSearchDimensions = 1536, VectorSearchProfileName = "vector-profile")]
    public ReadOnlyMemory<float>? DescriptionVector { get; set; }
}

var indexClient = new SearchIndexClient(endpoint, credential);
var fieldBuilder = new FieldBuilder();
var fields = fieldBuilder.Build(typeof(Hotel));

var index = new SearchIndex("hotels")
{
    Fields = fields,
    VectorSearch = new VectorSearch
    {
        Profiles = { new VectorSearchProfile("vector-profile", "hnsw-algo") },
        Algorithms = { new HnswAlgorithmConfiguration("hnsw-algo") }
    }
};

await indexClient.CreateOrUpdateIndexAsync(index);
```

### 4.2 ✅ CORRECT: Manual Field Definition
```csharp
var index = new SearchIndex("hotels")
{
    Fields =
    {
        new SimpleField("hotelId", SearchFieldDataType.String) { IsKey = true, IsFilterable = true },
        new SearchableField("hotelName") { IsSortable = true },
        new SearchableField("description") { AnalyzerName = LexicalAnalyzerName.EnLucene },
        new SimpleField("rating", SearchFieldDataType.Double) { IsFilterable = true, IsSortable = true },
        new SearchField("descriptionVector", SearchFieldDataType.Collection(SearchFieldDataType.Single))
        {
            VectorSearchDimensions = 1536,
            VectorSearchProfileName = "vector-profile"
        }
    }
};
```

### 4.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not using CreateOrUpdateIndexAsync
```csharp
// WRONG - use CreateOrUpdateIndexAsync for idempotent operations
await indexClient.CreateIndexAsync(index);
```

---

## 5. Document Operations

### 5.1 ✅ CORRECT: Upload Documents
```csharp
var searchClient = new SearchClient(endpoint, indexName, credential);
var hotels = new[] { new Hotel { HotelId = "1", HotelName = "Hotel A" } };
await searchClient.UploadDocumentsAsync(hotels);
```

### 5.2 ✅ CORRECT: Merge or Upload (Upsert)
```csharp
await searchClient.MergeOrUploadDocumentsAsync(hotels);
```

### 5.3 ✅ CORRECT: Batch Operations
```csharp
var batch = IndexDocumentsBatch.Create(
    IndexDocumentsAction.Upload(hotel1),
    IndexDocumentsAction.Merge(hotel2),
    IndexDocumentsAction.Delete(hotel3));
await searchClient.IndexDocumentsAsync(batch);
```

### 5.4 ✅ CORRECT: Delete Documents
```csharp
await searchClient.DeleteDocumentsAsync("hotelId", new[] { "1", "2" });
```

---

## 6. Search Patterns

### 6.1 ✅ CORRECT: Basic Search with Options
```csharp
var options = new SearchOptions
{
    Filter = "rating ge 4",
    OrderBy = { "rating desc" },
    Select = { "hotelId", "hotelName", "rating" },
    Size = 10,
    Skip = 0,
    IncludeTotalCount = true
};

SearchResults<Hotel> results = await searchClient.SearchAsync<Hotel>("luxury", options);

Console.WriteLine($"Total: {results.TotalCount}");
await foreach (SearchResult<Hotel> result in results.GetResultsAsync())
{
    Console.WriteLine($"{result.Document.HotelName} (Score: {result.Score})");
}
```

### 6.2 ✅ CORRECT: Faceted Search
```csharp
var options = new SearchOptions
{
    Facets = { "rating,count:5", "category" }
};

var results = await searchClient.SearchAsync<Hotel>("*", options);

foreach (var facet in results.Value.Facets["rating"])
{
    Console.WriteLine($"Rating {facet.Value}: {facet.Count}");
}
```

### 6.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not using Select to limit fields
```csharp
// WRONG - always use Select to return only needed fields for efficiency
var options = new SearchOptions();
var results = await searchClient.SearchAsync<Hotel>("luxury", options);
```

---

## 7. Vector Search

### 7.1 ✅ CORRECT: Pure Vector Search
```csharp
using Azure.Search.Documents.Models;

var vectorQuery = new VectorizedQuery(embedding)
{
    KNearestNeighborsCount = 5,
    Fields = { "descriptionVector" }
};

var options = new SearchOptions
{
    VectorSearch = new VectorSearchOptions
    {
        Queries = { vectorQuery }
    }
};

var results = await searchClient.SearchAsync<Hotel>(null, options);
```

### 7.2 ✅ CORRECT: Hybrid Search (Vector + Keyword)
```csharp
var vectorQuery = new VectorizedQuery(embedding)
{
    KNearestNeighborsCount = 5,
    Fields = { "descriptionVector" }
};

var options = new SearchOptions
{
    VectorSearch = new VectorSearchOptions
    {
        Queries = { vectorQuery }
    }
};

var results = await searchClient.SearchAsync<Hotel>("luxury beachfront", options);
```

---

## 8. Semantic Search

### 8.1 ✅ CORRECT: Semantic Search with Captions and Answers
```csharp
var options = new SearchOptions
{
    QueryType = SearchQueryType.Semantic,
    SemanticSearch = new SemanticSearchOptions
    {
        SemanticConfigurationName = "my-semantic-config",
        QueryCaption = new QueryCaption(QueryCaptionType.Extractive),
        QueryAnswer = new QueryAnswer(QueryAnswerType.Extractive)
    }
};

var results = await searchClient.SearchAsync<Hotel>("best hotel for families", options);

foreach (var answer in results.Value.SemanticSearch.Answers)
{
    Console.WriteLine($"Answer: {answer.Text} (Score: {answer.Score})");
}

await foreach (var result in results.Value.GetResultsAsync())
{
    var caption = result.SemanticSearch?.Captions?.FirstOrDefault();
    Console.WriteLine($"Caption: {caption?.Text}");
}
```

---

## 9. Hybrid Search (Vector + Keyword + Semantic)

### 9.1 ✅ CORRECT: Full Hybrid Search
```csharp
var vectorQuery = new VectorizedQuery(embedding)
{
    KNearestNeighborsCount = 5,
    Fields = { "descriptionVector" }
};

var options = new SearchOptions
{
    QueryType = SearchQueryType.Semantic,
    SemanticSearch = new SemanticSearchOptions
    {
        SemanticConfigurationName = "my-semantic-config"
    },
    VectorSearch = new VectorSearchOptions
    {
        Queries = { vectorQuery }
    }
};

var results = await searchClient.SearchAsync<Hotel>("luxury beachfront", options);
```

---

## 10. Error Handling

### 10.1 ✅ CORRECT: Handling Request Failures
```csharp
using Azure;

try
{
    var results = await searchClient.SearchAsync<Hotel>("query");
}
catch (RequestFailedException ex) when (ex.Status == 404)
{
    Console.WriteLine("Index not found");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Search error: {ex.Status} - {ex.ErrorCode}: {ex.Message}");
}
```

### 10.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Generic exception handling
```csharp
// WRONG - use specific RequestFailedException
try
{
    var results = await searchClient.SearchAsync<Hotel>("query");
}
catch (Exception ex)
{
    Console.WriteLine(ex.Message);
}
```

---

## Field Attributes Reference

| Attribute | Purpose |
|-----------|---------|
| `SimpleField` | Non-searchable field (filters, sorting, facets) |
| `SearchableField` | Full-text searchable field |
| `VectorSearchField` | Vector embedding field |
| `IsKey = true` | Document key (required, one per index) |
| `IsFilterable = true` | Enable $filter expressions |
| `IsSortable = true` | Enable $orderby |
| `IsFacetable = true` | Enable faceted navigation |
| `IsHidden = true` | Exclude from results |
| `AnalyzerName` | Specify text analyzer |
