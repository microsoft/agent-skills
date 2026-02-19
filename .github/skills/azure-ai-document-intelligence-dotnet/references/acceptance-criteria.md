# Azure Document Intelligence SDK Acceptance Criteria (.NET)

**SDK**: `Azure.AI.DocumentIntelligence`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/documentintelligence/Azure.AI.DocumentIntelligence
**NuGet Package**: https://www.nuget.org/packages/Azure.AI.DocumentIntelligence
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Imports

### 1.1 ✅ CORRECT: Client Imports
```csharp
using Azure.AI.DocumentIntelligence;
using Azure.Identity;
using Azure;
```

### 1.2 ✅ CORRECT: Model Imports (all in main namespace)
```csharp
using Azure.AI.DocumentIntelligence;
// AnalyzeResult, DocumentPage, DocumentField, etc. are in main namespace
```

### 1.3 ❌ INCORRECT: Wrong import paths
```csharp
// WRONG - using old Form Recognizer namespace
using Azure.AI.FormRecognizer;
using Azure.AI.FormRecognizer.DocumentAnalysis;

// WRONG - DocumentIntelligenceClient doesn't have sub-namespaces for models
using Azure.AI.DocumentIntelligence.Models;
```

---

## 2. Authentication

### 2.1 ✅ CORRECT: DefaultAzureCredential (Recommended)
```csharp
string endpoint = Environment.GetEnvironmentVariable("DOCUMENT_INTELLIGENCE_ENDPOINT")
    ?? throw new InvalidOperationException("DOCUMENT_INTELLIGENCE_ENDPOINT not set");

var client = new DocumentIntelligenceClient(new Uri(endpoint), new DefaultAzureCredential());
```

### 2.2 ✅ CORRECT: API Key Credential
```csharp
string endpoint = Environment.GetEnvironmentVariable("DOCUMENT_INTELLIGENCE_ENDPOINT")
    ?? throw new InvalidOperationException("DOCUMENT_INTELLIGENCE_ENDPOINT not set");
string apiKey = Environment.GetEnvironmentVariable("DOCUMENT_INTELLIGENCE_API_KEY")
    ?? throw new InvalidOperationException("DOCUMENT_INTELLIGENCE_API_KEY not set");

var client = new DocumentIntelligenceClient(new Uri(endpoint), new AzureKeyCredential(apiKey));
```

### 2.3 ❌ INCORRECT: Hardcoded credentials
```csharp
// WRONG - hardcoded endpoint and key
var client = new DocumentIntelligenceClient(
    new Uri("https://my-resource.cognitiveservices.azure.com"),
    new AzureKeyCredential("my-api-key"));
```

---

## 3. Document Analysis with Prebuilt Models

### 3.1 ✅ CORRECT: Analyze Layout from URI
```csharp
Uri documentUri = new Uri("https://example.com/document.pdf");

Operation<AnalyzeResult> operation = await client.AnalyzeDocumentAsync(
    WaitUntil.Completed,
    "prebuilt-layout",
    documentUri);

AnalyzeResult result = operation.Value;

foreach (DocumentPage page in result.Pages)
{
    Console.WriteLine($"Page {page.PageNumber} has {page.Lines.Count} lines and {page.Words.Count} words");
}
```

### 3.2 ✅ CORRECT: Analyze Invoice from URI
```csharp
Uri invoiceUri = new Uri("https://example.com/invoice.pdf");

Operation<AnalyzeResult> operation = await client.AnalyzeDocumentAsync(
    WaitUntil.Completed,
    "prebuilt-invoice",
    invoiceUri);

AnalyzeResult result = operation.Value;

for (int i = 0; i < result.Documents.Count; i++)
{
    AnalyzedDocument document = result.Documents[i];
    
    if (document.Fields.TryGetValue("VendorName", out DocumentField vendorField)
        && vendorField.FieldType == DocumentFieldType.String)
    {
        Console.WriteLine($"Vendor: {vendorField.ValueString}");
    }
    
    if (document.Fields.TryGetValue("InvoiceTotal", out DocumentField totalField)
        && totalField.FieldType == DocumentFieldType.Currency)
    {
        CurrencyValue total = totalField.ValueCurrency;
        Console.WriteLine($"Total: {total.CurrencySymbol}{total.Amount}");
    }
}
```

### 3.3 ✅ CORRECT: Analyze from Binary Data (File)
```csharp
string filePath = "path/to/document.pdf";
byte[] fileBytes = await File.ReadAllBytesAsync(filePath);

Operation<AnalyzeResult> operation = await client.AnalyzeDocumentAsync(
    WaitUntil.Completed,
    "prebuilt-layout",
    BinaryData.FromBytes(fileBytes));

AnalyzeResult result = operation.Value;
```

### 3.4 ❌ INCORRECT: Using old API patterns
```csharp
// WRONG - using old Form Recognizer method names
var operation = await client.StartAnalyzeDocumentFromUriAsync("prebuilt-invoice", uri);

// WRONG - using deprecated model IDs
var operation = await client.AnalyzeDocumentAsync(WaitUntil.Completed, "prebuilt-invoices", uri);
```

---

## 4. Prebuilt Model IDs

### 4.1 ✅ CORRECT: Prebuilt Model IDs
```csharp
// Layout - extract text, tables, selection marks
"prebuilt-layout"

// Read - extract text and language
"prebuilt-read"

// Invoice
"prebuilt-invoice"

// Receipt
"prebuilt-receipt"

// ID Document
"prebuilt-idDocument"

// Business Card
"prebuilt-businessCard"

// W2 Tax Form
"prebuilt-tax.us.w2"

// Health Insurance Card
"prebuilt-healthInsuranceCard.us"
```

### 4.2 ❌ INCORRECT: Wrong model IDs
```csharp
// WRONG - plural form
"prebuilt-invoices"
"prebuilt-receipts"

// WRONG - old naming convention
"prebuilt-document"
```

---

## 5. Extracting Document Content

### 5.1 ✅ CORRECT: Extract Lines and Words
```csharp
foreach (DocumentPage page in result.Pages)
{
    Console.WriteLine($"Page {page.PageNumber}:");
    
    for (int i = 0; i < page.Lines.Count; i++)
    {
        DocumentLine line = page.Lines[i];
        Console.WriteLine($"  Line {i}: '{line.Content}'");
        
        // Get bounding polygon
        Console.Write("    Bounding polygon:");
        for (int j = 0; j < line.Polygon.Count; j += 2)
        {
            Console.Write($" ({line.Polygon[j]}, {line.Polygon[j + 1]})");
        }
        Console.WriteLine();
    }
    
    foreach (DocumentWord word in page.Words)
    {
        Console.WriteLine($"  Word: '{word.Content}' (confidence: {word.Confidence})");
    }
}
```

### 5.2 ✅ CORRECT: Extract Tables
```csharp
for (int i = 0; i < result.Tables.Count; i++)
{
    DocumentTable table = result.Tables[i];
    Console.WriteLine($"Table {i} has {table.RowCount} rows and {table.ColumnCount} columns");
    
    foreach (DocumentTableCell cell in table.Cells)
    {
        Console.WriteLine($"  Cell ({cell.RowIndex}, {cell.ColumnIndex}): '{cell.Content}'");
        Console.WriteLine($"    Kind: {cell.Kind}");
    }
}
```

### 5.3 ✅ CORRECT: Extract Selection Marks
```csharp
foreach (DocumentPage page in result.Pages)
{
    for (int i = 0; i < page.SelectionMarks.Count; i++)
    {
        DocumentSelectionMark mark = page.SelectionMarks[i];
        Console.WriteLine($"Selection Mark {i}: {mark.State}");
        Console.WriteLine($"  Confidence: {mark.Confidence}");
    }
}
```

### 5.4 ✅ CORRECT: Extract Paragraphs
```csharp
for (int i = 0; i < result.Paragraphs.Count; i++)
{
    DocumentParagraph paragraph = result.Paragraphs[i];
    Console.WriteLine($"Paragraph {i}: {paragraph.Content}");
    
    if (paragraph.Role != null)
    {
        Console.WriteLine($"  Role: {paragraph.Role}");
    }
}
```

---

## 6. Field Extraction

### 6.1 ✅ CORRECT: Extract Typed Fields
```csharp
AnalyzedDocument document = result.Documents[0];

// String field
if (document.Fields.TryGetValue("CustomerName", out DocumentField nameField)
    && nameField.FieldType == DocumentFieldType.String)
{
    string customerName = nameField.ValueString;
    Console.WriteLine($"Customer: {customerName} (confidence: {nameField.Confidence})");
}

// Date field
if (document.Fields.TryGetValue("InvoiceDate", out DocumentField dateField)
    && dateField.FieldType == DocumentFieldType.Date)
{
    DateTimeOffset invoiceDate = dateField.ValueDate.Value;
    Console.WriteLine($"Date: {invoiceDate:d}");
}

// Currency field
if (document.Fields.TryGetValue("SubTotal", out DocumentField subtotalField)
    && subtotalField.FieldType == DocumentFieldType.Currency)
{
    CurrencyValue subtotal = subtotalField.ValueCurrency;
    Console.WriteLine($"Subtotal: {subtotal.CurrencySymbol}{subtotal.Amount}");
}
```

### 6.2 ✅ CORRECT: Extract List Fields (Line Items)
```csharp
if (document.Fields.TryGetValue("Items", out DocumentField itemsField)
    && itemsField.FieldType == DocumentFieldType.List)
{
    foreach (DocumentField itemField in itemsField.ValueList)
    {
        if (itemField.FieldType == DocumentFieldType.Dictionary)
        {
            IReadOnlyDictionary<string, DocumentField> item = itemField.ValueDictionary;
            
            if (item.TryGetValue("Description", out DocumentField descField))
            {
                Console.WriteLine($"  Description: {descField.ValueString}");
            }
            
            if (item.TryGetValue("Amount", out DocumentField amountField)
                && amountField.FieldType == DocumentFieldType.Currency)
            {
                Console.WriteLine($"  Amount: {amountField.ValueCurrency.Amount}");
            }
        }
    }
}
```

### 6.3 ❌ INCORRECT: Not checking field type
```csharp
// WRONG - accessing value without checking type
string value = document.Fields["CustomerName"].ValueString; // May throw if not string type
```

---

## 7. Custom Models

### 7.1 ✅ CORRECT: Build Custom Model
```csharp
var adminClient = new DocumentIntelligenceAdministrationClient(
    new Uri(endpoint), new DefaultAzureCredential());

var buildOptions = new BuildDocumentModelContent("custom-model-id", DocumentBuildMode.Template)
{
    AzureBlobSource = new AzureBlobContentSource(
        new Uri("https://storageaccount.blob.core.windows.net/training-data?sasToken"))
};

Operation<DocumentModelDetails> operation = await adminClient.BuildDocumentModelAsync(
    WaitUntil.Completed,
    buildOptions);

DocumentModelDetails model = operation.Value;
Console.WriteLine($"Model ID: {model.ModelId}");
Console.WriteLine($"Created: {model.CreatedOn}");
```

### 7.2 ✅ CORRECT: Analyze with Custom Model
```csharp
Operation<AnalyzeResult> operation = await client.AnalyzeDocumentAsync(
    WaitUntil.Completed,
    "custom-model-id",
    documentUri);

AnalyzeResult result = operation.Value;

foreach (AnalyzedDocument document in result.Documents)
{
    Console.WriteLine($"Document type: {document.DocumentType}");
    
    foreach (var field in document.Fields)
    {
        Console.WriteLine($"Field '{field.Key}': {field.Value.Content}");
    }
}
```

### 7.3 ✅ CORRECT: List Models
```csharp
var adminClient = new DocumentIntelligenceAdministrationClient(
    new Uri(endpoint), new DefaultAzureCredential());

AsyncPageable<DocumentModelDetails> models = adminClient.GetModelsAsync();

await foreach (DocumentModelDetails model in models)
{
    Console.WriteLine($"Model: {model.ModelId}, Created: {model.CreatedOn}");
}
```

### 7.4 ✅ CORRECT: Delete Model
```csharp
await adminClient.DeleteModelAsync("custom-model-id");
```

---

## 8. Document Classification

### 8.1 ✅ CORRECT: Build Classifier
```csharp
var buildOptions = new BuildDocumentClassifierContent("my-classifier")
{
    DocumentTypes =
    {
        ["invoice"] = new ClassifierDocumentTypeDetails()
        {
            AzureBlobSource = new AzureBlobContentSource(new Uri("https://storage.blob.core.windows.net/invoices?sas"))
        },
        ["receipt"] = new ClassifierDocumentTypeDetails()
        {
            AzureBlobSource = new AzureBlobContentSource(new Uri("https://storage.blob.core.windows.net/receipts?sas"))
        }
    }
};

Operation<DocumentClassifierDetails> operation = await adminClient.BuildClassifierAsync(
    WaitUntil.Completed,
    buildOptions);

DocumentClassifierDetails classifier = operation.Value;
Console.WriteLine($"Classifier ID: {classifier.ClassifierId}");
```

### 8.2 ✅ CORRECT: Classify Document
```csharp
Operation<AnalyzeResult> operation = await client.ClassifyDocumentAsync(
    WaitUntil.Completed,
    "my-classifier",
    documentUri);

AnalyzeResult result = operation.Value;

foreach (AnalyzedDocument document in result.Documents)
{
    Console.WriteLine($"Document type: {document.DocumentType}");
    Console.WriteLine($"Confidence: {document.Confidence}");
}
```

---

## 9. Async Patterns

### 9.1 ✅ CORRECT: Async Analysis
```csharp
// Full async with WaitUntil.Completed
Operation<AnalyzeResult> operation = await client.AnalyzeDocumentAsync(
    WaitUntil.Completed,
    "prebuilt-invoice",
    documentUri);

AnalyzeResult result = operation.Value;
```

### 9.2 ✅ CORRECT: Polling for Long-Running Operations
```csharp
// Start operation without waiting
Operation<AnalyzeResult> operation = await client.AnalyzeDocumentAsync(
    WaitUntil.Started,
    "prebuilt-layout",
    documentUri);

Console.WriteLine($"Operation ID: {operation.Id}");

// Poll for completion
await operation.WaitForCompletionAsync();

AnalyzeResult result = operation.Value;
```

### 9.3 ❌ INCORRECT: Blocking on async
```csharp
// WRONG - using .Result instead of await
var result = client.AnalyzeDocumentAsync(WaitUntil.Completed, "prebuilt-layout", uri).Result;

// WRONG - using .Wait()
operation.WaitForCompletionAsync().Wait();
```

---

## 10. Error Handling

### 10.1 ✅ CORRECT: Handle RequestFailedException
```csharp
try
{
    Operation<AnalyzeResult> operation = await client.AnalyzeDocumentAsync(
        WaitUntil.Completed,
        "prebuilt-invoice",
        documentUri);
}
catch (RequestFailedException ex) when (ex.Status == 400)
{
    Console.WriteLine($"Invalid request: {ex.Message}");
}
catch (RequestFailedException ex) when (ex.Status == 404)
{
    Console.WriteLine($"Model not found: {ex.Message}");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Service error ({ex.Status}): {ex.Message}");
}
```

### 10.2 ❌ INCORRECT: Swallowing exceptions
```csharp
// WRONG - empty catch
try
{
    var operation = await client.AnalyzeDocumentAsync(...);
}
catch { }
```

---

## 11. Best Practices

### 11.1 ✅ CORRECT: Reuse Client Instance
```csharp
public class DocumentAnalysisService
{
    private readonly DocumentIntelligenceClient _client;
    
    public DocumentAnalysisService(string endpoint)
    {
        _client = new DocumentIntelligenceClient(
            new Uri(endpoint),
            new DefaultAzureCredential());
    }
    
    public async Task<AnalyzeResult> AnalyzeInvoiceAsync(Uri documentUri)
    {
        var operation = await _client.AnalyzeDocumentAsync(
            WaitUntil.Completed,
            "prebuilt-invoice",
            documentUri);
        return operation.Value;
    }
}
```

### 11.2 ✅ CORRECT: Check Document Confidence
```csharp
foreach (AnalyzedDocument document in result.Documents)
{
    if (document.Confidence < 0.8)
    {
        Console.WriteLine($"Low confidence ({document.Confidence:P}) - manual review recommended");
    }
}
```

### 11.3 ❌ INCORRECT: Creating client per request
```csharp
// WRONG - wasteful to create client for each analysis
public async Task<AnalyzeResult> AnalyzeDocument(Uri uri)
{
    var client = new DocumentIntelligenceClient(new Uri(endpoint), new DefaultAzureCredential());
    // ...
}
```
