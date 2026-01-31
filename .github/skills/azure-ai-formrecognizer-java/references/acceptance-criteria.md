# Azure Document Intelligence (Form Recognizer) SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-ai-formrecognizer`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/formrecognizer/azure-ai-formrecognizer
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Azure SDK Client Imports
```java
import com.azure.ai.formrecognizer.documentanalysis.DocumentAnalysisClient;
import com.azure.ai.formrecognizer.documentanalysis.DocumentAnalysisClientBuilder;
import com.azure.ai.formrecognizer.documentanalysis.administration.DocumentModelAdministrationClient;
import com.azure.ai.formrecognizer.documentanalysis.administration.DocumentModelAdministrationClientBuilder;
import com.azure.core.credential.AzureKeyCredential;
```

#### ❌ INCORRECT: Non-existent or Wrong Package
```java
import com.azure.formrecognizer.DocumentAnalysisClient;  // Wrong package path
import com.azure.ai.formrecognizer.FormRecognizerClient;  // Old API (v2)
```

### 1.2 Model Imports
#### ✅ CORRECT: Model Classes from Models Package
```java
import com.azure.ai.formrecognizer.documentanalysis.models.AnalyzeResult;
import com.azure.ai.formrecognizer.documentanalysis.models.DocumentPage;
import com.azure.ai.formrecognizer.documentanalysis.models.DocumentTable;
import com.azure.ai.formrecognizer.documentanalysis.models.AnalyzedDocument;
import com.azure.ai.formrecognizer.documentanalysis.models.DocumentField;
```

#### ❌ INCORRECT: Wrong Model Package
```java
import com.azure.ai.formrecognizer.documentanalysis.AnalyzeResult;  // Missing models subpackage
import com.azure.ai.formrecognizer.models.RecognizedForm;  // Old API
```

---

## 2. Client Creation Patterns

### 2.1 DocumentAnalysisClient
#### ✅ CORRECT: Using DocumentAnalysisClientBuilder
```java
DocumentAnalysisClient client = new DocumentAnalysisClientBuilder()
    .credential(new AzureKeyCredential("{key}"))
    .endpoint("{endpoint}")
    .buildClient();
```

#### ❌ INCORRECT: Direct Instantiation
```java
DocumentAnalysisClient client = new DocumentAnalysisClient(endpoint, key);
```

### 2.2 DocumentModelAdministrationClient
#### ✅ CORRECT: Using DocumentModelAdministrationClientBuilder
```java
DocumentModelAdministrationClient adminClient = new DocumentModelAdministrationClientBuilder()
    .credential(new AzureKeyCredential("{key}"))
    .endpoint("{endpoint}")
    .buildClient();
```

### 2.3 DefaultAzureCredential
#### ✅ CORRECT: Using DefaultAzureCredentialBuilder
```java
import com.azure.identity.DefaultAzureCredentialBuilder;

DocumentAnalysisClient client = new DocumentAnalysisClientBuilder()
    .endpoint("{endpoint}")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

#### ❌ INCORRECT: Direct DefaultAzureCredential
```java
DocumentAnalysisClient client = new DocumentAnalysisClientBuilder()
    .credential(new DefaultAzureCredential())  // Must use builder
    .endpoint("{endpoint}")
    .buildClient();
```

---

## 3. Document Analysis Patterns

### 3.1 Analyze from File (Layout)
#### ✅ CORRECT: SyncPoller with BinaryData
```java
import com.azure.core.util.BinaryData;
import com.azure.core.util.polling.SyncPoller;
import java.io.File;

File document = new File("document.pdf");
BinaryData documentData = BinaryData.fromFile(document.toPath());

SyncPoller<OperationResult, AnalyzeResult> poller = 
    client.beginAnalyzeDocument("prebuilt-layout", documentData);

AnalyzeResult result = poller.getFinalResult();
```

#### ❌ INCORRECT: Wrong Method or Missing Poller
```java
AnalyzeResult result = client.analyzeDocument("prebuilt-layout", documentData);  // Missing poller
client.beginAnalyzeDocument("prebuilt-layout", new File("doc.pdf"));  // Wrong data type
```

### 3.2 Analyze from URL
#### ✅ CORRECT: beginAnalyzeDocumentFromUrl
```java
String documentUrl = "https://example.com/invoice.pdf";

SyncPoller<OperationResult, AnalyzeResult> poller = 
    client.beginAnalyzeDocumentFromUrl("prebuilt-invoice", documentUrl);

AnalyzeResult result = poller.getFinalResult();
```

#### ❌ INCORRECT: Using beginAnalyzeDocument for URLs
```java
client.beginAnalyzeDocument("prebuilt-invoice", documentUrl);  // Wrong method for URLs
```

---

## 4. Prebuilt Model Patterns

### 4.1 Available Prebuilt Models
| Model ID | Purpose |
|----------|---------|
| `prebuilt-layout` | Extract text, tables, selection marks |
| `prebuilt-document` | General document with key-value pairs |
| `prebuilt-receipt` | Receipt data extraction |
| `prebuilt-invoice` | Invoice field extraction |
| `prebuilt-businessCard` | Business card parsing |
| `prebuilt-idDocument` | ID document (passport, license) |
| `prebuilt-tax.us.w2` | US W2 tax forms |

### 4.2 Receipt Analysis
#### ✅ CORRECT: Field Extraction with Type Checking
```java
SyncPoller<OperationResult, AnalyzeResult> poller = 
    client.beginAnalyzeDocumentFromUrl("prebuilt-receipt", receiptUrl);

AnalyzeResult result = poller.getFinalResult();

for (AnalyzedDocument doc : result.getDocuments()) {
    Map<String, DocumentField> fields = doc.getFields();
    
    DocumentField merchantName = fields.get("MerchantName");
    if (merchantName != null && merchantName.getType() == DocumentFieldType.STRING) {
        System.out.printf("Merchant: %s (confidence: %.2f)%n",
            merchantName.getValueAsString(),
            merchantName.getConfidence());
    }
}
```

### 4.3 Processing Tables
#### ✅ CORRECT: Iterating Table Cells
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

## 5. Custom Model Patterns

### 5.1 Build Custom Model
#### ✅ CORRECT: BuildDocumentModelOptions with SyncPoller
```java
import com.azure.ai.formrecognizer.documentanalysis.administration.models.*;

String blobContainerUrl = "{SAS_URL_of_training_data}";
String prefix = "training-docs/";

SyncPoller<OperationResult, DocumentModelDetails> poller = adminClient.beginBuildDocumentModel(
    blobContainerUrl,
    DocumentModelBuildMode.TEMPLATE,
    prefix,
    new BuildDocumentModelOptions()
        .setModelId("my-custom-model")
        .setDescription("Custom invoice model"),
    Context.NONE);

DocumentModelDetails model = poller.getFinalResult();
```

### 5.2 Compose Models
#### ✅ CORRECT: ComposeDocumentModelOptions
```java
List<String> modelIds = Arrays.asList("model-1", "model-2", "model-3");

SyncPoller<OperationResult, DocumentModelDetails> poller = 
    adminClient.beginComposeDocumentModel(
        modelIds,
        new ComposeDocumentModelOptions()
            .setModelId("composed-model")
            .setDescription("Composed from multiple models"));

DocumentModelDetails composedModel = poller.getFinalResult();
```

### 5.3 Analyze with Custom Model
#### ✅ CORRECT: Using Custom Model ID
```java
SyncPoller<OperationResult, AnalyzeResult> poller = 
    client.beginAnalyzeDocumentFromUrl("my-custom-model", documentUrl);

AnalyzeResult result = poller.getFinalResult();

for (AnalyzedDocument doc : result.getDocuments()) {
    System.out.printf("Document type: %s (confidence: %.2f)%n",
        doc.getDocType(),
        doc.getConfidence());
}
```

---

## 6. Model Management Patterns

### 6.1 List Models
#### ✅ CORRECT: PagedIterable
```java
PagedIterable<DocumentModelSummary> models = adminClient.listDocumentModels();
for (DocumentModelSummary summary : models) {
    System.out.printf("Model: %s, Created: %s%n",
        summary.getModelId(),
        summary.getCreatedOn());
}
```

### 6.2 Get Model Details
#### ✅ CORRECT: getDocumentModel
```java
DocumentModelDetails model = adminClient.getDocumentModel("model-id");
```

### 6.3 Delete Model
#### ✅ CORRECT: deleteDocumentModel
```java
adminClient.deleteDocumentModel("model-id");
```

### 6.4 Check Resource Limits
#### ✅ CORRECT: getResourceDetails
```java
ResourceDetails resources = adminClient.getResourceDetails();
System.out.printf("Models: %d / %d%n",
    resources.getCustomDocumentModelCount(),
    resources.getCustomDocumentModelLimit());
```

---

## 7. Document Classification Patterns

### 7.1 Build Classifier
#### ✅ CORRECT: ClassifierDocumentTypeDetails
```java
Map<String, ClassifierDocumentTypeDetails> docTypes = new HashMap<>();
docTypes.put("invoice", new ClassifierDocumentTypeDetails()
    .setAzureBlobSource(new AzureBlobContentSource(containerUrl).setPrefix("invoices/")));
docTypes.put("receipt", new ClassifierDocumentTypeDetails()
    .setAzureBlobSource(new AzureBlobContentSource(containerUrl).setPrefix("receipts/")));

SyncPoller<OperationResult, DocumentClassifierDetails> poller = 
    adminClient.beginBuildDocumentClassifier(docTypes,
        new BuildDocumentClassifierOptions().setClassifierId("my-classifier"));

DocumentClassifierDetails classifier = poller.getFinalResult();
```

### 7.2 Classify Document
#### ✅ CORRECT: beginClassifyDocumentFromUrl
```java
SyncPoller<OperationResult, AnalyzeResult> poller = 
    client.beginClassifyDocumentFromUrl("my-classifier", documentUrl, Context.NONE);

AnalyzeResult result = poller.getFinalResult();

for (AnalyzedDocument doc : result.getDocuments()) {
    System.out.printf("Classified as: %s (confidence: %.2f)%n",
        doc.getDocType(),
        doc.getConfidence());
}
```

---

## 8. Error Handling

### 8.1 HttpResponseException
#### ✅ CORRECT: Azure SDK Exception Handling
```java
import com.azure.core.exception.HttpResponseException;

try {
    client.beginAnalyzeDocumentFromUrl("prebuilt-receipt", "invalid-url");
} catch (HttpResponseException e) {
    System.out.println("Status: " + e.getResponse().getStatusCode());
    System.out.println("Error: " + e.getMessage());
}
```

#### ❌ INCORRECT: Generic Exception Only
```java
try {
    client.beginAnalyzeDocumentFromUrl("prebuilt-receipt", url);
} catch (Exception e) {
    // Missing specific HttpResponseException handling
}
```

---

## 9. Environment Configuration

### 9.1 Environment Variables
#### ✅ CORRECT: Reading from Environment
```java
String endpoint = System.getenv("FORM_RECOGNIZER_ENDPOINT");
String key = System.getenv("FORM_RECOGNIZER_KEY");
```

#### ❌ INCORRECT: Hardcoded Credentials
```java
String endpoint = "https://myresource.cognitiveservices.azure.com/";
String key = "abc123secretkey";  // Never hardcode credentials
```

---

## 10. Best Practices

### 10.1 Long-Running Operations
- Always use SyncPoller for document analysis operations
- Call `getFinalResult()` to wait for completion

### 10.2 Field Type Checking
- Always check `DocumentFieldType` before extracting values
- Use appropriate `getValueAs*()` methods based on type

### 10.3 Confidence Scores
- Check confidence scores for extracted fields
- Consider thresholds for production use (typically > 0.8)