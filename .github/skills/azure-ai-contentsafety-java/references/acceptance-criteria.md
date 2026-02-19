# Azure AI Content Safety SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-ai-contentsafety`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/contentsafety/azure-ai-contentsafety
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Client Builder and Clients
```java
import com.azure.ai.contentsafety.ContentSafetyClient;
import com.azure.ai.contentsafety.ContentSafetyClientBuilder;
import com.azure.ai.contentsafety.BlocklistClient;
import com.azure.ai.contentsafety.BlocklistClientBuilder;
```

#### ✅ CORRECT: Authentication
```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.core.credential.KeyCredential;
```

### 1.2 Model Imports

#### ✅ CORRECT: Analysis Models
```java
import com.azure.ai.contentsafety.models.AnalyzeTextOptions;
import com.azure.ai.contentsafety.models.AnalyzeTextResult;
import com.azure.ai.contentsafety.models.TextCategoriesAnalysis;
import com.azure.ai.contentsafety.models.TextCategory;
import com.azure.ai.contentsafety.models.AnalyzeTextOutputType;
import com.azure.ai.contentsafety.models.AnalyzeImageOptions;
import com.azure.ai.contentsafety.models.AnalyzeImageResult;
import com.azure.ai.contentsafety.models.ContentSafetyImageData;
import com.azure.ai.contentsafety.models.ImageCategoriesAnalysis;
```

#### ✅ CORRECT: Blocklist Models
```java
import com.azure.ai.contentsafety.models.TextBlocklistItem;
import com.azure.ai.contentsafety.models.TextBlocklistMatch;
import com.azure.ai.contentsafety.models.AddOrUpdateTextBlocklistItemsOptions;
import com.azure.ai.contentsafety.models.AddOrUpdateTextBlocklistItemsResult;
import com.azure.ai.contentsafety.models.RemoveTextBlocklistItemsOptions;
import com.azure.ai.contentsafety.models.TextBlocklist;
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong import paths
```java
// WRONG - Models not in main package
import com.azure.ai.contentsafety.AnalyzeTextOptions;

// WRONG - Using non-existent classes
import com.azure.ai.contentsafety.ContentModerationClient;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Builder with KeyCredential
```java
String endpoint = System.getenv("CONTENT_SAFETY_ENDPOINT");
String key = System.getenv("CONTENT_SAFETY_KEY");

ContentSafetyClient client = new ContentSafetyClientBuilder()
    .credential(new KeyCredential(key))
    .endpoint(endpoint)
    .buildClient();

BlocklistClient blocklistClient = new BlocklistClientBuilder()
    .credential(new KeyCredential(key))
    .endpoint(endpoint)
    .buildClient();
```

### 2.2 ✅ CORRECT: Builder with DefaultAzureCredential
```java
ContentSafetyClient client = new ContentSafetyClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint)
    .buildClient();
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials
```java
// WRONG - hardcoded values
ContentSafetyClient client = new ContentSafetyClientBuilder()
    .endpoint("https://myresource.cognitiveservices.azure.com")
    .credential(new KeyCredential("hardcoded-key"))
    .buildClient();
```

---

## 3. Text Analysis Patterns

### 3.1 ✅ CORRECT: Basic Text Analysis
```java
AnalyzeTextResult result = client.analyzeText(
    new AnalyzeTextOptions("This is text to analyze"));

for (TextCategoriesAnalysis category : result.getCategoriesAnalysis()) {
    System.out.printf("Category: %s, Severity: %d%n",
        category.getCategory(),
        category.getSeverity());
}
```

### 3.2 ✅ CORRECT: Text Analysis with Options
```java
AnalyzeTextOptions options = new AnalyzeTextOptions("Text to analyze")
    .setCategories(Arrays.asList(
        TextCategory.HATE,
        TextCategory.VIOLENCE))
    .setOutputType(AnalyzeTextOutputType.EIGHT_SEVERITY_LEVELS);

AnalyzeTextResult result = client.analyzeText(options);
```

### 3.3 ✅ CORRECT: Text Analysis with Blocklist
```java
AnalyzeTextOptions options = new AnalyzeTextOptions("Text with potentially blocked words")
    .setBlocklistNames(Arrays.asList("my-blocklist"))
    .setHaltOnBlocklistHit(true);

AnalyzeTextResult result = client.analyzeText(options);

if (result.getBlocklistsMatch() != null) {
    for (TextBlocklistMatch match : result.getBlocklistsMatch()) {
        System.out.printf("Blocklist: %s, Item: %s%n",
            match.getBlocklistName(),
            match.getBlocklistItemId());
    }
}
```

---

## 4. Image Analysis Patterns

### 4.1 ✅ CORRECT: Analyze Image from File
```java
import com.azure.core.util.BinaryData;
import java.nio.file.Files;
import java.nio.file.Paths;

byte[] imageBytes = Files.readAllBytes(Paths.get("image.png"));
ContentSafetyImageData imageData = new ContentSafetyImageData()
    .setContent(BinaryData.fromBytes(imageBytes));

AnalyzeImageResult result = client.analyzeImage(
    new AnalyzeImageOptions(imageData));

for (ImageCategoriesAnalysis category : result.getCategoriesAnalysis()) {
    System.out.printf("Category: %s, Severity: %d%n",
        category.getCategory(),
        category.getSeverity());
}
```

### 4.2 ✅ CORRECT: Analyze Image from URL
```java
ContentSafetyImageData imageData = new ContentSafetyImageData()
    .setBlobUrl("https://example.com/image.jpg");

AnalyzeImageResult result = client.analyzeImage(
    new AnalyzeImageOptions(imageData));
```

---

## 5. Blocklist Management

### 5.1 ✅ CORRECT: Add Block Items
```java
List<TextBlocklistItem> items = Arrays.asList(
    new TextBlocklistItem("badword1").setDescription("Offensive term"),
    new TextBlocklistItem("badword2").setDescription("Another term")
);

AddOrUpdateTextBlocklistItemsResult result = blocklistClient.addOrUpdateBlocklistItems(
    "my-blocklist",
    new AddOrUpdateTextBlocklistItemsOptions(items));

for (TextBlocklistItem item : result.getBlocklistItems()) {
    System.out.printf("Added: %s (ID: %s)%n",
        item.getText(),
        item.getBlocklistItemId());
}
```

### 5.2 ✅ CORRECT: List Blocklists
```java
PagedIterable<TextBlocklist> blocklists = blocklistClient.listTextBlocklists();

for (TextBlocklist blocklist : blocklists) {
    System.out.printf("Blocklist: %s%n", blocklist.getName());
}
```

### 5.3 ✅ CORRECT: Remove Block Items
```java
List<String> itemIds = Arrays.asList("item-id-1", "item-id-2");

blocklistClient.removeBlocklistItems(
    "my-blocklist",
    new RemoveTextBlocklistItemsOptions(itemIds));
```

---

## 6. Error Handling

### 6.1 ✅ CORRECT: HTTP Exception Handling
```java
import com.azure.core.exception.HttpResponseException;

try {
    client.analyzeText(new AnalyzeTextOptions("test"));
} catch (HttpResponseException e) {
    System.out.println("Status: " + e.getResponse().getStatusCode());
    System.out.println("Error: " + e.getMessage());
}
```

### 6.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Empty catch blocks
```java
// WRONG - swallowing exceptions
try {
    client.analyzeText(options);
} catch (Exception e) {
    // Do nothing
}
```

---

## 7. Best Practices Checklist

- [ ] Use `DefaultAzureCredentialBuilder` or `KeyCredential` for authentication
- [ ] Use environment variables for endpoint and key configuration
- [ ] Specify only needed categories to reduce latency
- [ ] Use blocklists for custom content filtering
- [ ] Severity >= 4 typically indicates content should be blocked
- [ ] Handle `HttpResponseException` appropriately
- [ ] Note blocklist changes take ~5 minutes to take effect
