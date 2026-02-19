# Azure Document Intelligence (Form Recognizer) SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-ai-formrecognizer`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/formrecognizer/azure-ai-formrecognizer
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Document Analysis Clients
```java
import com.azure.ai.formrecognizer.documentanalysis.DocumentAnalysisClient;
import com.azure.ai.formrecognizer.documentanalysis.DocumentAnalysisClientBuilder;
import com.azure.ai.formrecognizer.documentanalysis.DocumentAnalysisAsyncClient;
```

#### ✅ CORRECT: Administration Clients
```java
import com.azure.ai.formrecognizer.documentanalysis.administration.DocumentModelAdministrationClient;
import com.azure.ai.formrecognizer.documentanalysis.administration.DocumentModelAdministrationClientBuilder;
```

#### ✅ CORRECT: Authentication
```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.core.credential.AzureKeyCredential;
```

### 1.2 Model Imports

#### ✅ CORRECT: Analysis Models
```java
import com.azure.ai.formrecognizer.documentanalysis.models.AnalyzeResult;
import com.azure.ai.formrecognizer.documentanalysis.models.AnalyzedDocument;
import com.azure.ai.formrecognizer.documentanalysis.models.DocumentPage;
import com.azure.ai.formrecognizer.documentanalysis.models.DocumentLine;
import com.azure.ai.formrecognizer.documentanalysis.models.DocumentTable;
import com.azure.ai.formrecognizer.documentanalysis.models.DocumentTableCell;
import com.azure.ai.formrecognizer.documentanalysis.models.DocumentField;
import com.azure.ai.formrecognizer.documentanalysis.models.DocumentFieldType;
import com.azure.ai.formrecognizer.documentanalysis.models.OperationResult;
```

#### ✅ CORRECT: Administration Models
```java
import com.azure.ai.formrecognizer.documentanalysis.administration.models.DocumentModelDetails;
import com.azure.ai.formrecognizer.documentanalysis.administration.models.DocumentModelSummary;
import com.azure.ai.formrecognizer.documentanalysis.administration.models.DocumentModelBuildMode;
import com.azure.ai.formrecognizer.documentanalysis.administration.models.BuildDocumentModelOptions;
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong import paths
```java
// WRONG - Using old SDK paths
import com.azure.ai.formrecognizer.FormRecognizerClient;

// WRONG - Models not in main package
import com.azure.ai.formrecognizer.documentanalysis.AnalyzeResult;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Builder with AzureKeyCredential
```java
String endpoint = System.getenv("FORM_RECOGNIZER_ENDPOINT");
String key = System.getenv("FORM_RECOGNIZER_KEY");

DocumentAnalysisClient client = new DocumentAnalysisClientBuilder()
    .credential(new AzureKeyCredential(key))
    .endpoint(endpoint)
    .buildClient();
```

### 2.2 ✅ CORRECT: Builder with DefaultAzureCredential
```java
DocumentAnalysisClient client = new DocumentAnalysisClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### 2.3 ✅ CORRECT: Administration Client
```java
DocumentModelAdministrationClient adminClient = new DocumentModelAdministrationClientBuilder()
    .credential(new AzureKeyCredential(key))
    .endpoint(endpoint)
    .buildClient();
```

### 2.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials
```java
// WRONG - hardcoded values
DocumentAnalysisClient client = new DocumentAnalysisClientBuilder()
    .endpoint("https://myresource.cognitiveservices.azure.com")
    .credential(new AzureKeyCredential("hardcoded-key"))
    .buildClient();
```

---

## 3. Document Analysis Patterns

### 3.1 ✅ CORRECT: Analyze Layout
```java
import com.azure.core.util.BinaryData;
import com.azure.core.util.polling.SyncPoller;

File document = new File("document.pdf");
BinaryData documentData = BinaryData.fromFile(document.toPath());

SyncPoller<OperationResult, AnalyzeResult> poller = 
    client.beginAnalyzeDocument("prebuilt-layout", documentData);

AnalyzeResult result = poller.getFinalResult();

for (DocumentPage page : result.getPages()) {
    System.out.printf("Page %d: %.2f x %.2f%n",
        page.getPageNumber(),
        page.getWidth(),
        page.getHeight());
}
```

### 3.2 ✅ CORRECT: Analyze from URL
```java
String documentUrl = "https://example.com/invoice.pdf";

SyncPoller<OperationResult, AnalyzeResult> poller = 
    client.beginAnalyzeDocumentFromUrl("prebuilt-invoice", documentUrl);

AnalyzeResult result = poller.getFinalResult();
```

### 3.3 ✅ CORRECT: Extract Fields from Receipt
```java
SyncPoller<OperationResult, AnalyzeResult> poller = 
    client.beginAnalyzeDocumentFromUrl("prebuilt-receipt", receiptUrl);

AnalyzeResult result = poller.getFinalResult();

for (AnalyzedDocument doc : result.getDocuments()) {
    Map<String, DocumentField> fields = doc.getFields();
    
    DocumentField merchantName = fields.get("MerchantName");
    if (merchantName != null && merchantName.getType() == DocumentFieldType.STRING) {
        System.out.printf("Merchant: %s%n", merchantName.getValueAsString());
    }
}
```

### 3.4 ✅ CORRECT: Process Tables
```java
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

---

## 4. Custom Model Patterns

### 4.1 ✅ CORRECT: Build Custom Model
```java
String blobContainerUrl = System.getenv("TRAINING_DATA_URL");

SyncPoller<OperationResult, DocumentModelDetails> poller = adminClient.beginBuildDocumentModel(
    blobContainerUrl,
    DocumentModelBuildMode.TEMPLATE,
    null,  // prefix
    new BuildDocumentModelOptions()
        .setModelId("my-custom-model")
        .setDescription("Custom invoice model"),
    Context.NONE);

DocumentModelDetails model = poller.getFinalResult();
System.out.println("Model ID: " + model.getModelId());
```

### 4.2 ✅ CORRECT: List Models
```java
PagedIterable<DocumentModelSummary> models = adminClient.listDocumentModels();
for (DocumentModelSummary summary : models) {
    System.out.printf("Model: %s, Created: %s%n",
        summary.getModelId(),
        summary.getCreatedOn());
}
```

### 4.3 ✅ CORRECT: Delete Model
```java
adminClient.deleteDocumentModel("model-id");
```

---

## 5. Error Handling

### 5.1 ✅ CORRECT: HTTP Exception Handling
```java
import com.azure.core.exception.HttpResponseException;

try {
    client.beginAnalyzeDocumentFromUrl("prebuilt-receipt", "invalid-url");
} catch (HttpResponseException e) {
    System.out.println("Status: " + e.getResponse().getStatusCode());
    System.out.println("Error: " + e.getMessage());
}
```

---

## 6. Prebuilt Models Reference

| Model ID | Purpose |
|----------|---------|
| `prebuilt-layout` | Extract text, tables, selection marks |
| `prebuilt-document` | General document with key-value pairs |
| `prebuilt-receipt` | Receipt data extraction |
| `prebuilt-invoice` | Invoice field extraction |
| `prebuilt-businessCard` | Business card parsing |
| `prebuilt-idDocument` | ID document (passport, license) |

---

## 7. Best Practices Checklist

- [ ] Use `DefaultAzureCredentialBuilder` for production authentication
- [ ] Use environment variables for endpoint and key configuration
- [ ] Use `SyncPoller` for long-running analysis operations
- [ ] Check `DocumentFieldType` before accessing field values
- [ ] Handle null fields gracefully
- [ ] Use appropriate prebuilt models for document types
- [ ] Handle `HttpResponseException` appropriately
