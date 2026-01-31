# Azure AI Content Safety SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-ai-contentsafety`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/contentsafety/azure-ai-contentsafety
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Azure SDK Client Imports
```java
import com.azure.ai.contentsafety.ContentSafetyClient;
import com.azure.ai.contentsafety.ContentSafetyClientBuilder;
import com.azure.ai.contentsafety.BlocklistClient;
import com.azure.ai.contentsafety.BlocklistClientBuilder;
import com.azure.core.credential.KeyCredential;
```

#### ❌ INCORRECT: Non-existent or Wrong Package
```java
import com.azure.contentsafety.Client;  // Wrong package path
import azure.ai.contentsafety.ContentSafetyClient;  // Wrong root package
```

### 1.2 Model Imports
#### ✅ CORRECT: Model Classes from Models Package
```java
import com.azure.ai.contentsafety.models.AnalyzeTextOptions;
import com.azure.ai.contentsafety.models.AnalyzeTextResult;
import com.azure.ai.contentsafety.models.TextCategory;
import com.azure.ai.contentsafety.models.TextCategoriesAnalysis;
```

#### ❌ INCORRECT: Wrong Model Package
```java
import com.azure.ai.contentsafety.AnalyzeTextOptions;  // Missing models subpackage
```

---

## 2. Client Creation Patterns

### 2.1 ContentSafetyClient with API Key
#### ✅ CORRECT: Using ContentSafetyClientBuilder
```java
String endpoint = System.getenv("CONTENT_SAFETY_ENDPOINT");
String key = System.getenv("CONTENT_SAFETY_KEY");

ContentSafetyClient client = new ContentSafetyClientBuilder()
    .credential(new KeyCredential(key))
    .endpoint(endpoint)
    .buildClient();
```

#### ❌ INCORRECT: Direct Instantiation
```java
ContentSafetyClient client = new ContentSafetyClient(endpoint, key);
```

### 2.2 BlocklistClient
#### ✅ CORRECT: Using BlocklistClientBuilder
```java
BlocklistClient blocklistClient = new BlocklistClientBuilder()
    .credential(new KeyCredential(key))
    .endpoint(endpoint)
    .buildClient();
```

### 2.3 DefaultAzureCredential
#### ✅ CORRECT: Using DefaultAzureCredentialBuilder
```java
import com.azure.identity.DefaultAzureCredentialBuilder;

ContentSafetyClient client = new ContentSafetyClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint)
    .buildClient();
```

#### ❌ INCORRECT: Direct DefaultAzureCredential
```java
ContentSafetyClient client = new ContentSafetyClientBuilder()
    .credential(new DefaultAzureCredential())  // Must use builder
    .endpoint(endpoint)
    .buildClient();
```

---

## 3. Text Analysis Patterns

### 3.1 Basic Text Analysis
#### ✅ CORRECT: AnalyzeTextOptions with String
```java
AnalyzeTextResult result = client.analyzeText(
    new AnalyzeTextOptions("This is text to analyze"));

for (TextCategoriesAnalysis category : result.getCategoriesAnalysis()) {
    System.out.printf("Category: %s, Severity: %d%n",
        category.getCategory(),
        category.getSeverity());
}
```

#### ❌ INCORRECT: Wrong Method or Parameters
```java
client.analyzeText("text");  // Missing AnalyzeTextOptions wrapper
client.analyze(options);  // Wrong method name
```

### 3.2 Text Analysis with Options
#### ✅ CORRECT: Category and Output Type Selection
```java
AnalyzeTextOptions options = new AnalyzeTextOptions("Text to analyze")
    .setCategories(Arrays.asList(
        TextCategory.HATE,
        TextCategory.VIOLENCE))
    .setOutputType(AnalyzeTextOutputType.EIGHT_SEVERITY_LEVELS);

AnalyzeTextResult result = client.analyzeText(options);
```

### 3.3 Text Analysis with Blocklist
#### ✅ CORRECT: Blocklist Configuration
```java
AnalyzeTextOptions options = new AnalyzeTextOptions("Text to check")
    .setBlocklistNames(Arrays.asList("my-blocklist"))
    .setHaltOnBlocklistHit(true);

AnalyzeTextResult result = client.analyzeText(options);

if (result.getBlocklistsMatch() != null) {
    for (TextBlocklistMatch match : result.getBlocklistsMatch()) {
        System.out.printf("Blocklist: %s, Item: %s%n",
            match.getBlocklistName(),
            match.getBlocklistItemText());
    }
}
```

---

## 4. Image Analysis Patterns

### 4.1 Analyze Image from File
#### ✅ CORRECT: ContentSafetyImageData with BinaryData
```java
import com.azure.core.util.BinaryData;
import java.nio.file.Files;
import java.nio.file.Paths;

byte[] imageBytes = Files.readAllBytes(Paths.get("image.png"));
ContentSafetyImageData imageData = new ContentSafetyImageData()
    .setContent(BinaryData.fromBytes(imageBytes));

AnalyzeImageResult result = client.analyzeImage(
    new AnalyzeImageOptions(imageData));
```

### 4.2 Analyze Image from URL
#### ✅ CORRECT: setBlobUrl for Remote Images
```java
ContentSafetyImageData imageData = new ContentSafetyImageData()
    .setBlobUrl("https://example.com/image.jpg");

AnalyzeImageResult result = client.analyzeImage(
    new AnalyzeImageOptions(imageData));
```

#### ❌ INCORRECT: Wrong Image Data Setup
```java
AnalyzeImageResult result = client.analyzeImage("https://example.com/image.jpg");  // Missing options
```

---

## 5. Blocklist Management Patterns

### 5.1 Create or Update Blocklist
#### ✅ CORRECT: Using RequestOptions
```java
import com.azure.core.http.rest.RequestOptions;
import com.azure.core.http.rest.Response;
import com.azure.core.util.BinaryData;
import java.util.Map;

Map<String, String> description = Map.of("description", "Custom blocklist");
BinaryData resource = BinaryData.fromObject(description);

Response<BinaryData> response = blocklistClient.createOrUpdateTextBlocklistWithResponse(
    "my-blocklist", resource, new RequestOptions());
```

### 5.2 Add Block Items
#### ✅ CORRECT: TextBlocklistItem with AddOrUpdateTextBlocklistItemsOptions
```java
List<TextBlocklistItem> items = Arrays.asList(
    new TextBlocklistItem("badword1").setDescription("Offensive term"),
    new TextBlocklistItem("badword2").setDescription("Another term")
);

AddOrUpdateTextBlocklistItemsResult result = blocklistClient.addOrUpdateBlocklistItems(
    "my-blocklist",
    new AddOrUpdateTextBlocklistItemsOptions(items));
```

### 5.3 List Blocklists
#### ✅ CORRECT: PagedIterable
```java
PagedIterable<TextBlocklist> blocklists = blocklistClient.listTextBlocklists();

for (TextBlocklist blocklist : blocklists) {
    System.out.printf("Blocklist: %s, Description: %s%n",
        blocklist.getName(),
        blocklist.getDescription());
}
```

### 5.4 Remove Block Items
#### ✅ CORRECT: RemoveTextBlocklistItemsOptions
```java
List<String> itemIds = Arrays.asList("item-id-1", "item-id-2");

blocklistClient.removeBlocklistItems(
    "my-blocklist",
    new RemoveTextBlocklistItemsOptions(itemIds));
```

### 5.5 Delete Blocklist
#### ✅ CORRECT: Delete by Name
```java
blocklistClient.deleteTextBlocklist("my-blocklist");
```

---

## 6. Error Handling

### 6.1 HttpResponseException
#### ✅ CORRECT: Azure SDK Exception Handling
```java
import com.azure.core.exception.HttpResponseException;

try {
    client.analyzeText(new AnalyzeTextOptions("test"));
} catch (HttpResponseException e) {
    System.out.println("Status: " + e.getResponse().getStatusCode());
    System.out.println("Error: " + e.getMessage());
}
```

#### ❌ INCORRECT: Generic Exception Only
```java
try {
    client.analyzeText(new AnalyzeTextOptions("test"));
} catch (Exception e) {
    // Missing specific HttpResponseException handling
}
```

---

## 7. Environment Configuration

### 7.1 Environment Variables
#### ✅ CORRECT: Reading from Environment
```java
String endpoint = System.getenv("CONTENT_SAFETY_ENDPOINT");
String key = System.getenv("CONTENT_SAFETY_KEY");
```

#### ❌ INCORRECT: Hardcoded Credentials
```java
String endpoint = "https://myresource.cognitiveservices.azure.com/";
String key = "abc123secretkey";  // Never hardcode credentials
```

---

## 8. Harm Categories Reference

### 8.1 Available Categories
| Category | Enum Value | Description |
|----------|------------|-------------|
| Hate | `TextCategory.HATE` | Discriminatory language based on identity groups |
| Sexual | `TextCategory.SEXUAL` | Sexual content, relationships, acts |
| Violence | `TextCategory.VIOLENCE` | Physical harm, weapons, injury |
| Self-harm | `TextCategory.SELF_HARM` | Self-injury, suicide-related content |

### 8.2 Severity Levels
- Text: 0-7 scale (default outputs 0, 2, 4, 6)
- Image: 0, 2, 4, 6 (trimmed scale)
- Block threshold: Typically severity >= 4 for strict moderation

---

## 9. Best Practices

### 9.1 Performance
- Only request needed categories to reduce latency
- Process multiple items in parallel for throughput
- Cache blocklist results where appropriate

### 9.2 Blocklist Management
- Changes take ~5 minutes to take effect
- Use descriptive names for blocklist items
- Test blocklist behavior before production deployment
