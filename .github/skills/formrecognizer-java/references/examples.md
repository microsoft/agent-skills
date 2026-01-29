# Azure Document Intelligence (Form Recognizer) Java SDK - Examples

Comprehensive code examples for the Azure AI Document Intelligence SDK for Java.

## Table of Contents

- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Prebuilt Models](#prebuilt-models)
- [Layout Analysis](#layout-analysis)
- [Receipt Analysis](#receipt-analysis)
- [Invoice Analysis](#invoice-analysis)
- [ID Document Analysis](#id-document-analysis)
- [Custom Models](#custom-models)
- [Document Classification](#document-classification)
- [Model Management](#model-management)
- [Async Patterns](#async-patterns)
- [Error Handling](#error-handling)
- [Complete Application Example](#complete-application-example)

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-ai-formrecognizer</artifactId>
    <version>4.2.0-beta.1</version>
</dependency>

<!-- For DefaultAzureCredential -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
    <version>1.14.2</version>
</dependency>
```

## Client Creation

### With API Key

```java
import com.azure.ai.formrecognizer.documentanalysis.DocumentAnalysisClient;
import com.azure.ai.formrecognizer.documentanalysis.DocumentAnalysisClientBuilder;
import com.azure.core.credential.AzureKeyCredential;

String endpoint = System.getenv("FORM_RECOGNIZER_ENDPOINT");
String key = System.getenv("FORM_RECOGNIZER_KEY");

DocumentAnalysisClient client = new DocumentAnalysisClientBuilder()
    .credential(new AzureKeyCredential(key))
    .endpoint(endpoint)
    .buildClient();
```

### With DefaultAzureCredential (Recommended)

```java
import com.azure.identity.DefaultAzureCredentialBuilder;

DocumentAnalysisClient client = new DocumentAnalysisClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### Async Client

```java
import com.azure.ai.formrecognizer.documentanalysis.DocumentAnalysisAsyncClient;

DocumentAnalysisAsyncClient asyncClient = new DocumentAnalysisClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncClient();
```

### Administration Client

```java
import com.azure.ai.formrecognizer.documentanalysis.administration.DocumentModelAdministrationClient;
import com.azure.ai.formrecognizer.documentanalysis.administration.DocumentModelAdministrationClientBuilder;

DocumentModelAdministrationClient adminClient = new DocumentModelAdministrationClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

## Prebuilt Models

| Model ID | Purpose |
|----------|---------|
| `prebuilt-layout` | Extract text, tables, selection marks |
| `prebuilt-document` | General document with key-value pairs |
| `prebuilt-receipt` | Receipt data extraction |
| `prebuilt-invoice` | Invoice field extraction |
| `prebuilt-businessCard` | Business card parsing |
| `prebuilt-idDocument` | ID document (passport, license) |
| `prebuilt-tax.us.w2` | US W2 tax forms |

## Layout Analysis

### Extract Layout from File

```java
import com.azure.ai.formrecognizer.documentanalysis.models.*;
import com.azure.core.util.BinaryData;
import com.azure.core.util.polling.SyncPoller;
import java.io.File;

File document = new File("document.pdf");
BinaryData documentData = BinaryData.fromFile(document.toPath());

SyncPoller<OperationResult, AnalyzeResult> poller = 
    client.beginAnalyzeDocument("prebuilt-layout", documentData);

AnalyzeResult result = poller.getFinalResult();

// Process pages
for (DocumentPage page : result.getPages()) {
    System.out.printf("Page %d: %.2f x %.2f %s%n",
        page.getPageNumber(),
        page.getWidth(),
        page.getHeight(),
        page.getUnit());
    
    // Extract lines
    for (DocumentLine line : page.getLines()) {
        System.out.println("Line: " + line.getContent());
    }
    
    // Extract words with confidence
    for (DocumentWord word : page.getWords()) {
        System.out.printf("Word: '%s' (confidence: %.2f)%n",
            word.getContent(),
            word.getConfidence());
    }
    
    // Selection marks (checkboxes)
    for (DocumentSelectionMark mark : page.getSelectionMarks()) {
        System.out.printf("Checkbox: %s (confidence: %.2f)%n",
            mark.getSelectionMarkState(),
            mark.getConfidence());
    }
}

// Process tables
for (DocumentTable table : result.getTables()) {
    System.out.printf("Table: %d rows x %d columns%n",
        table.getRowCount(),
        table.getColumnCount());
    
    for (DocumentTableCell cell : table.getCells()) {
        System.out.printf("Cell[%d,%d]: %s%n",
            cell.getRowIndex(),
            cell.getColumnIndex(),
            cell.getContent());
    }
}
```

### Extract Layout from URL

```java
String documentUrl = "https://example.com/document.pdf";

SyncPoller<OperationResult, AnalyzeResult> poller = 
    client.beginAnalyzeDocumentFromUrl("prebuilt-layout", documentUrl);

AnalyzeResult result = poller.getFinalResult();
```

## Receipt Analysis

```java
String receiptUrl = "https://example.com/receipt.jpg";

SyncPoller<OperationResult, AnalyzeResult> poller = 
    client.beginAnalyzeDocumentFromUrl("prebuilt-receipt", receiptUrl);

AnalyzeResult result = poller.getFinalResult();

for (AnalyzedDocument doc : result.getDocuments()) {
    Map<String, DocumentField> fields = doc.getFields();
    
    // Merchant name
    DocumentField merchantName = fields.get("MerchantName");
    if (merchantName != null && merchantName.getType() == DocumentFieldType.STRING) {
        System.out.printf("Merchant: %s (confidence: %.2f)%n",
            merchantName.getValueAsString(),
            merchantName.getConfidence());
    }
    
    // Transaction date
    DocumentField transactionDate = fields.get("TransactionDate");
    if (transactionDate != null && transactionDate.getType() == DocumentFieldType.DATE) {
        System.out.printf("Date: %s%n", transactionDate.getValueAsDate());
    }
    
    // Total amount
    DocumentField total = fields.get("Total");
    if (total != null && total.getType() == DocumentFieldType.DOUBLE) {
        System.out.printf("Total: $%.2f%n", total.getValueAsDouble());
    }
    
    // Line items
    DocumentField items = fields.get("Items");
    if (items != null && items.getType() == DocumentFieldType.LIST) {
        System.out.println("Items:");
        for (DocumentField item : items.getValueAsList()) {
            Map<String, DocumentField> itemFields = item.getValueAsMap();
            
            DocumentField name = itemFields.get("Name");
            DocumentField price = itemFields.get("Price");
            DocumentField quantity = itemFields.get("Quantity");
            
            System.out.printf("  - %s x%s: $%.2f%n",
                name != null ? name.getValueAsString() : "Unknown",
                quantity != null ? quantity.getValueAsDouble().intValue() : 1,
                price != null ? price.getValueAsDouble() : 0.0);
        }
    }
}
```

## Invoice Analysis

```java
String invoiceUrl = "https://example.com/invoice.pdf";

SyncPoller<OperationResult, AnalyzeResult> poller = 
    client.beginAnalyzeDocumentFromUrl("prebuilt-invoice", invoiceUrl);

AnalyzeResult result = poller.getFinalResult();

for (AnalyzedDocument invoice : result.getDocuments()) {
    Map<String, DocumentField> fields = invoice.getFields();
    
    // Vendor information
    DocumentField vendorName = fields.get("VendorName");
    DocumentField vendorAddress = fields.get("VendorAddress");
    
    System.out.println("=== Vendor ===");
    if (vendorName != null) {
        System.out.println("Name: " + vendorName.getValueAsString());
    }
    if (vendorAddress != null) {
        System.out.println("Address: " + vendorAddress.getContent());
    }
    
    // Customer information
    DocumentField customerName = fields.get("CustomerName");
    DocumentField customerAddress = fields.get("CustomerAddress");
    
    System.out.println("=== Customer ===");
    if (customerName != null) {
        System.out.println("Name: " + customerName.getValueAsString());
    }
    
    // Invoice details
    DocumentField invoiceId = fields.get("InvoiceId");
    DocumentField invoiceDate = fields.get("InvoiceDate");
    DocumentField dueDate = fields.get("DueDate");
    
    System.out.println("=== Invoice Details ===");
    if (invoiceId != null) {
        System.out.println("Invoice ID: " + invoiceId.getValueAsString());
    }
    if (invoiceDate != null) {
        System.out.println("Invoice Date: " + invoiceDate.getValueAsDate());
    }
    if (dueDate != null) {
        System.out.println("Due Date: " + dueDate.getValueAsDate());
    }
    
    // Amounts
    DocumentField subTotal = fields.get("SubTotal");
    DocumentField totalTax = fields.get("TotalTax");
    DocumentField invoiceTotal = fields.get("InvoiceTotal");
    DocumentField amountDue = fields.get("AmountDue");
    
    System.out.println("=== Amounts ===");
    if (subTotal != null) {
        System.out.printf("Subtotal: $%.2f%n", subTotal.getValueAsDouble());
    }
    if (totalTax != null) {
        System.out.printf("Tax: $%.2f%n", totalTax.getValueAsDouble());
    }
    if (invoiceTotal != null) {
        System.out.printf("Total: $%.2f%n", invoiceTotal.getValueAsDouble());
    }
    
    // Line items
    DocumentField items = fields.get("Items");
    if (items != null && items.getType() == DocumentFieldType.LIST) {
        System.out.println("=== Line Items ===");
        for (DocumentField item : items.getValueAsList()) {
            Map<String, DocumentField> itemFields = item.getValueAsMap();
            
            String description = getStringValue(itemFields.get("Description"));
            Double quantity = getDoubleValue(itemFields.get("Quantity"));
            Double unitPrice = getDoubleValue(itemFields.get("UnitPrice"));
            Double amount = getDoubleValue(itemFields.get("Amount"));
            
            System.out.printf("  %s | Qty: %.0f | Unit: $%.2f | Amount: $%.2f%n",
                description, quantity, unitPrice, amount);
        }
    }
}

// Helper methods
private static String getStringValue(DocumentField field) {
    return field != null ? field.getValueAsString() : "";
}

private static Double getDoubleValue(DocumentField field) {
    return field != null ? field.getValueAsDouble() : 0.0;
}
```

## ID Document Analysis

```java
String idDocumentUrl = "https://example.com/drivers-license.jpg";

SyncPoller<OperationResult, AnalyzeResult> poller = 
    client.beginAnalyzeDocumentFromUrl("prebuilt-idDocument", idDocumentUrl);

AnalyzeResult result = poller.getFinalResult();

for (AnalyzedDocument idDoc : result.getDocuments()) {
    Map<String, DocumentField> fields = idDoc.getFields();
    
    // Document type
    System.out.println("Document Type: " + idDoc.getDocType());
    
    // Personal information
    DocumentField firstName = fields.get("FirstName");
    DocumentField lastName = fields.get("LastName");
    DocumentField dateOfBirth = fields.get("DateOfBirth");
    DocumentField sex = fields.get("Sex");
    
    System.out.println("=== Personal Information ===");
    if (firstName != null) System.out.println("First Name: " + firstName.getValueAsString());
    if (lastName != null) System.out.println("Last Name: " + lastName.getValueAsString());
    if (dateOfBirth != null) System.out.println("DOB: " + dateOfBirth.getValueAsDate());
    if (sex != null) System.out.println("Sex: " + sex.getValueAsString());
    
    // Document information
    DocumentField documentNumber = fields.get("DocumentNumber");
    DocumentField expirationDate = fields.get("DateOfExpiration");
    DocumentField address = fields.get("Address");
    DocumentField region = fields.get("Region");
    DocumentField country = fields.get("CountryRegion");
    
    System.out.println("=== Document Information ===");
    if (documentNumber != null) System.out.println("Document #: " + documentNumber.getValueAsString());
    if (expirationDate != null) System.out.println("Expires: " + expirationDate.getValueAsDate());
    if (address != null) System.out.println("Address: " + address.getContent());
    if (region != null) System.out.println("Region: " + region.getValueAsString());
    if (country != null) System.out.println("Country: " + country.getValueAsString());
}
```

## Custom Models

### Build Custom Model

```java
import com.azure.ai.formrecognizer.documentanalysis.administration.models.*;
import com.azure.core.util.Context;

String blobContainerUrl = "https://storage.blob.core.windows.net/training-data?sasToken";
String prefix = "invoices/";

SyncPoller<OperationResult, DocumentModelDetails> poller = adminClient.beginBuildDocumentModel(
    blobContainerUrl,
    DocumentModelBuildMode.TEMPLATE,
    prefix,
    new BuildDocumentModelOptions()
        .setModelId("my-custom-invoice-model")
        .setDescription("Custom model for company invoices"),
    Context.NONE);

DocumentModelDetails model = poller.getFinalResult();

System.out.println("Model ID: " + model.getModelId());
System.out.println("Description: " + model.getDescription());
System.out.println("Created: " + model.getCreatedOn());

// Show document types and fields
model.getDocumentTypes().forEach((docType, details) -> {
    System.out.println("\nDocument type: " + docType);
    details.getFieldSchema().forEach((field, schema) -> {
        System.out.printf("  Field: %s (%s)%n", field, schema.getType());
    });
});
```

### Analyze with Custom Model

```java
String documentUrl = "https://example.com/new-invoice.pdf";

SyncPoller<OperationResult, AnalyzeResult> poller = 
    client.beginAnalyzeDocumentFromUrl("my-custom-invoice-model", documentUrl);

AnalyzeResult result = poller.getFinalResult();

for (AnalyzedDocument doc : result.getDocuments()) {
    System.out.printf("Document type: %s (confidence: %.2f)%n",
        doc.getDocType(),
        doc.getConfidence());
    
    doc.getFields().forEach((name, field) -> {
        System.out.printf("Field '%s': %s (confidence: %.2f)%n",
            name,
            field.getContent(),
            field.getConfidence());
    });
}
```

### Compose Multiple Models

```java
import java.util.Arrays;
import java.util.List;

List<String> modelIds = Arrays.asList(
    "invoice-model-2023",
    "invoice-model-2024",
    "receipt-model"
);

SyncPoller<OperationResult, DocumentModelDetails> poller = 
    adminClient.beginComposeDocumentModel(
        modelIds,
        new ComposeDocumentModelOptions()
            .setModelId("composed-financial-model")
            .setDescription("Composed model for invoices and receipts"));

DocumentModelDetails composedModel = poller.getFinalResult();
System.out.println("Composed model ID: " + composedModel.getModelId());
```

## Document Classification

### Build Classifier

```java
import java.util.HashMap;
import java.util.Map;

String containerUrl = "https://storage.blob.core.windows.net/training-data?sasToken";

Map<String, ClassifierDocumentTypeDetails> docTypes = new HashMap<>();

docTypes.put("invoice", new ClassifierDocumentTypeDetails()
    .setAzureBlobSource(new AzureBlobContentSource(containerUrl)
        .setPrefix("invoices/")));

docTypes.put("receipt", new ClassifierDocumentTypeDetails()
    .setAzureBlobSource(new AzureBlobContentSource(containerUrl)
        .setPrefix("receipts/")));

docTypes.put("purchase-order", new ClassifierDocumentTypeDetails()
    .setAzureBlobSource(new AzureBlobContentSource(containerUrl)
        .setPrefix("purchase-orders/")));

SyncPoller<OperationResult, DocumentClassifierDetails> poller = 
    adminClient.beginBuildDocumentClassifier(
        docTypes,
        new BuildDocumentClassifierOptions()
            .setClassifierId("financial-doc-classifier")
            .setDescription("Classifier for financial documents"));

DocumentClassifierDetails classifier = poller.getFinalResult();
System.out.println("Classifier ID: " + classifier.getClassifierId());
System.out.println("Document types: " + classifier.getDocumentTypes().keySet());
```

### Classify Document

```java
String documentUrl = "https://example.com/unknown-document.pdf";

SyncPoller<OperationResult, AnalyzeResult> poller = 
    client.beginClassifyDocumentFromUrl("financial-doc-classifier", documentUrl, Context.NONE);

AnalyzeResult result = poller.getFinalResult();

for (AnalyzedDocument doc : result.getDocuments()) {
    System.out.printf("Classified as: %s (confidence: %.2f)%n",
        doc.getDocType(),
        doc.getConfidence());
    
    // Get bounding regions for the classified content
    if (doc.getBoundingRegions() != null) {
        for (BoundingRegion region : doc.getBoundingRegions()) {
            System.out.printf("  Page %d%n", region.getPageNumber());
        }
    }
}
```

## Model Management

### List Models

```java
import com.azure.core.http.rest.PagedIterable;

PagedIterable<DocumentModelSummary> models = adminClient.listDocumentModels();

System.out.println("Available models:");
for (DocumentModelSummary summary : models) {
    System.out.printf("  %s - Created: %s%n",
        summary.getModelId(),
        summary.getCreatedOn());
}
```

### Get Model Details

```java
DocumentModelDetails model = adminClient.getDocumentModel("my-custom-model");

System.out.println("Model ID: " + model.getModelId());
System.out.println("Description: " + model.getDescription());
System.out.println("Created: " + model.getCreatedOn());
System.out.println("Expiration: " + model.getExpiresOn());
```

### Delete Model

```java
adminClient.deleteDocumentModel("old-model-id");
System.out.println("Model deleted successfully");
```

### Check Resource Limits

```java
ResourceDetails resources = adminClient.getResourceDetails();

System.out.println("=== Resource Limits ===");
System.out.printf("Custom models: %d / %d%n",
    resources.getCustomDocumentModelCount(),
    resources.getCustomDocumentModelLimit());
```

### List Classifiers

```java
PagedIterable<DocumentClassifierDetails> classifiers = adminClient.listDocumentClassifiers();

for (DocumentClassifierDetails classifier : classifiers) {
    System.out.printf("Classifier: %s, Types: %s%n",
        classifier.getClassifierId(),
        classifier.getDocumentTypes().keySet());
}
```

## Async Patterns

### Async Document Analysis

```java
import reactor.core.publisher.Mono;

DocumentAnalysisAsyncClient asyncClient = new DocumentAnalysisClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncClient();

String documentUrl = "https://example.com/document.pdf";

asyncClient.beginAnalyzeDocumentFromUrl("prebuilt-invoice", documentUrl)
    .flatMap(poller -> poller.getFinalResult())
    .subscribe(
        result -> {
            System.out.println("Analysis complete!");
            for (AnalyzedDocument doc : result.getDocuments()) {
                System.out.println("Document type: " + doc.getDocType());
            }
        },
        error -> System.err.println("Error: " + error.getMessage()),
        () -> System.out.println("Done")
    );

// Block for demo purposes
Thread.sleep(30000);
```

### Parallel Analysis

```java
import reactor.core.publisher.Flux;
import java.util.Arrays;
import java.util.List;

List<String> documentUrls = Arrays.asList(
    "https://example.com/invoice1.pdf",
    "https://example.com/invoice2.pdf",
    "https://example.com/invoice3.pdf"
);

Flux.fromIterable(documentUrls)
    .flatMap(url -> asyncClient.beginAnalyzeDocumentFromUrl("prebuilt-invoice", url)
        .flatMap(poller -> poller.getFinalResult())
        .map(result -> new DocumentResult(url, result)))
    .subscribe(
        docResult -> System.out.printf("Processed: %s - %d documents%n",
            docResult.url, docResult.result.getDocuments().size()),
        error -> System.err.println("Error: " + error.getMessage())
    );

// Helper class
class DocumentResult {
    String url;
    AnalyzeResult result;
    
    DocumentResult(String url, AnalyzeResult result) {
        this.url = url;
        this.result = result;
    }
}
```

## Error Handling

```java
import com.azure.core.exception.HttpResponseException;

try {
    SyncPoller<OperationResult, AnalyzeResult> poller = 
        client.beginAnalyzeDocumentFromUrl("prebuilt-receipt", "invalid-url");
    poller.getFinalResult();
} catch (HttpResponseException e) {
    System.err.println("HTTP Status: " + e.getResponse().getStatusCode());
    System.err.println("Error Message: " + e.getMessage());
    
    // Handle specific errors
    int statusCode = e.getResponse().getStatusCode();
    if (statusCode == 400) {
        System.err.println("Bad request - check document URL or format");
    } else if (statusCode == 401) {
        System.err.println("Unauthorized - check credentials");
    } else if (statusCode == 404) {
        System.err.println("Model not found");
    } else if (statusCode == 429) {
        System.err.println("Rate limited - retry with backoff");
    }
} catch (Exception e) {
    System.err.println("Unexpected error: " + e.getMessage());
}
```

## Complete Application Example

```java
import com.azure.ai.formrecognizer.documentanalysis.DocumentAnalysisClient;
import com.azure.ai.formrecognizer.documentanalysis.DocumentAnalysisClientBuilder;
import com.azure.ai.formrecognizer.documentanalysis.models.*;
import com.azure.core.util.polling.SyncPoller;
import com.azure.identity.DefaultAzureCredentialBuilder;

import java.util.Map;

public class InvoiceProcessor {
    
    private final DocumentAnalysisClient client;
    
    public InvoiceProcessor() {
        this.client = new DocumentAnalysisClientBuilder()
            .endpoint(System.getenv("FORM_RECOGNIZER_ENDPOINT"))
            .credential(new DefaultAzureCredentialBuilder().build())
            .buildClient();
    }
    
    public InvoiceData processInvoice(String invoiceUrl) {
        SyncPoller<OperationResult, AnalyzeResult> poller = 
            client.beginAnalyzeDocumentFromUrl("prebuilt-invoice", invoiceUrl);
        
        AnalyzeResult result = poller.getFinalResult();
        
        if (result.getDocuments().isEmpty()) {
            throw new RuntimeException("No invoice found in document");
        }
        
        AnalyzedDocument invoice = result.getDocuments().get(0);
        Map<String, DocumentField> fields = invoice.getFields();
        
        return new InvoiceData(
            getStringField(fields, "InvoiceId"),
            getStringField(fields, "VendorName"),
            getStringField(fields, "CustomerName"),
            getDateField(fields, "InvoiceDate"),
            getDateField(fields, "DueDate"),
            getDoubleField(fields, "SubTotal"),
            getDoubleField(fields, "TotalTax"),
            getDoubleField(fields, "InvoiceTotal"),
            invoice.getConfidence()
        );
    }
    
    private String getStringField(Map<String, DocumentField> fields, String name) {
        DocumentField field = fields.get(name);
        return field != null ? field.getValueAsString() : null;
    }
    
    private java.time.LocalDate getDateField(Map<String, DocumentField> fields, String name) {
        DocumentField field = fields.get(name);
        return field != null ? field.getValueAsDate() : null;
    }
    
    private Double getDoubleField(Map<String, DocumentField> fields, String name) {
        DocumentField field = fields.get(name);
        return field != null ? field.getValueAsDouble() : null;
    }
    
    // Data class for invoice
    public static class InvoiceData {
        public final String invoiceId;
        public final String vendorName;
        public final String customerName;
        public final java.time.LocalDate invoiceDate;
        public final java.time.LocalDate dueDate;
        public final Double subTotal;
        public final Double tax;
        public final Double total;
        public final double confidence;
        
        public InvoiceData(String invoiceId, String vendorName, String customerName,
                          java.time.LocalDate invoiceDate, java.time.LocalDate dueDate,
                          Double subTotal, Double tax, Double total, double confidence) {
            this.invoiceId = invoiceId;
            this.vendorName = vendorName;
            this.customerName = customerName;
            this.invoiceDate = invoiceDate;
            this.dueDate = dueDate;
            this.subTotal = subTotal;
            this.tax = tax;
            this.total = total;
            this.confidence = confidence;
        }
        
        @Override
        public String toString() {
            return String.format(
                "Invoice %s from %s to %s: $%.2f (confidence: %.2f)",
                invoiceId, vendorName, customerName, total, confidence
            );
        }
    }
    
    public static void main(String[] args) {
        InvoiceProcessor processor = new InvoiceProcessor();
        
        String invoiceUrl = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-invoice.pdf";
        
        try {
            InvoiceData invoice = processor.processInvoice(invoiceUrl);
            System.out.println(invoice);
        } catch (Exception e) {
            System.err.println("Failed to process invoice: " + e.getMessage());
        }
    }
}
```

## Environment Variables

```bash
FORM_RECOGNIZER_ENDPOINT=https://<resource>.cognitiveservices.azure.com/
FORM_RECOGNIZER_KEY=<your-api-key>

# For DefaultAzureCredential
AZURE_CLIENT_ID=<service-principal-client-id>
AZURE_CLIENT_SECRET=<service-principal-secret>
AZURE_TENANT_ID=<tenant-id>
```

## Best Practices

1. **Use DefaultAzureCredential** — Prefer managed identity over API keys in production
2. **Choose the right model** — Use prebuilt models when possible; custom models for specialized documents
3. **Handle polling properly** — Use `getFinalResult()` for synchronous waits
4. **Check confidence scores** — Validate extracted data based on confidence thresholds
5. **Process in batches** — Use async client for parallel processing of multiple documents
6. **Implement retry logic** — Handle rate limiting (429) with exponential backoff
7. **Clean up resources** — Delete unused custom models to stay within limits
8. **Use classification first** — For mixed document types, classify before extraction
