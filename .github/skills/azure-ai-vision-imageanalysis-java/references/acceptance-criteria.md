# Azure AI Vision Image Analysis SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-ai-vision-imageanalysis`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/vision/azure-ai-vision-imageanalysis
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Client Builder and Clients
```java
import com.azure.ai.vision.imageanalysis.ImageAnalysisClient;
import com.azure.ai.vision.imageanalysis.ImageAnalysisClientBuilder;
import com.azure.ai.vision.imageanalysis.ImageAnalysisAsyncClient;
```

#### ✅ CORRECT: Authentication
```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.core.credential.KeyCredential;
```

### 1.2 Model Imports

#### ✅ CORRECT: Analysis Models
```java
import com.azure.ai.vision.imageanalysis.models.ImageAnalysisResult;
import com.azure.ai.vision.imageanalysis.models.ImageAnalysisOptions;
import com.azure.ai.vision.imageanalysis.models.VisualFeatures;
import com.azure.ai.vision.imageanalysis.models.DetectedTextBlock;
import com.azure.ai.vision.imageanalysis.models.DetectedTextLine;
import com.azure.ai.vision.imageanalysis.models.DetectedTextWord;
import com.azure.ai.vision.imageanalysis.models.DetectedObject;
import com.azure.ai.vision.imageanalysis.models.DetectedTag;
import com.azure.ai.vision.imageanalysis.models.DetectedPerson;
import com.azure.ai.vision.imageanalysis.models.DenseCaption;
import com.azure.ai.vision.imageanalysis.models.CropRegion;
import com.azure.ai.vision.imageanalysis.models.ImageBoundingBox;
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong import paths
```java
// WRONG - Using old package names
import com.azure.cognitiveservices.vision.computervision.ComputerVisionClient;

// WRONG - Models not in models package
import com.azure.ai.vision.imageanalysis.ImageAnalysisResult;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Builder with KeyCredential
```java
String endpoint = System.getenv("VISION_ENDPOINT");
String key = System.getenv("VISION_KEY");

ImageAnalysisClient client = new ImageAnalysisClientBuilder()
    .endpoint(endpoint)
    .credential(new KeyCredential(key))
    .buildClient();
```

### 2.2 ✅ CORRECT: Builder with DefaultAzureCredential
```java
ImageAnalysisClient client = new ImageAnalysisClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### 2.3 ✅ CORRECT: Async Client
```java
ImageAnalysisAsyncClient asyncClient = new ImageAnalysisClientBuilder()
    .endpoint(endpoint)
    .credential(new KeyCredential(key))
    .buildAsyncClient();
```

### 2.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials
```java
// WRONG - hardcoded values
ImageAnalysisClient client = new ImageAnalysisClientBuilder()
    .endpoint("https://myresource.cognitiveservices.azure.com")
    .credential(new KeyCredential("hardcoded-key"))
    .buildClient();
```

---

## 3. Image Analysis Patterns

### 3.1 ✅ CORRECT: Generate Caption
```java
import com.azure.core.util.BinaryData;
import java.io.File;
import java.util.Arrays;

BinaryData imageData = BinaryData.fromFile(new File("image.jpg").toPath());

ImageAnalysisResult result = client.analyze(
    imageData,
    Arrays.asList(VisualFeatures.CAPTION),
    new ImageAnalysisOptions().setGenderNeutralCaption(true));

System.out.printf("Caption: \"%s\" (confidence: %.4f)%n",
    result.getCaption().getText(),
    result.getCaption().getConfidence());
```

### 3.2 ✅ CORRECT: Analyze from URL
```java
ImageAnalysisResult result = client.analyzeFromUrl(
    "https://example.com/image.jpg",
    Arrays.asList(VisualFeatures.CAPTION),
    new ImageAnalysisOptions().setGenderNeutralCaption(true));
```

### 3.3 ✅ CORRECT: Extract Text (OCR)
```java
ImageAnalysisResult result = client.analyze(
    imageData,
    Arrays.asList(VisualFeatures.READ),
    null);

for (DetectedTextBlock block : result.getRead().getBlocks()) {
    for (DetectedTextLine line : block.getLines()) {
        System.out.printf("Line: '%s'%n", line.getText());
        for (DetectedTextWord word : line.getWords()) {
            System.out.printf("  Word: '%s' (confidence: %.4f)%n",
                word.getText(),
                word.getConfidence());
        }
    }
}
```

### 3.4 ✅ CORRECT: Detect Objects
```java
ImageAnalysisResult result = client.analyzeFromUrl(
    imageUrl,
    Arrays.asList(VisualFeatures.OBJECTS),
    null);

for (DetectedObject obj : result.getObjects()) {
    System.out.printf("Object: %s (confidence: %.4f)%n",
        obj.getTags().get(0).getName(),
        obj.getTags().get(0).getConfidence());
    ImageBoundingBox box = obj.getBoundingBox();
    System.out.printf("  Location: x=%d, y=%d, w=%d, h=%d%n",
        box.getX(), box.getY(), box.getWidth(), box.getHeight());
}
```

### 3.5 ✅ CORRECT: Multiple Features
```java
ImageAnalysisResult result = client.analyzeFromUrl(
    imageUrl,
    Arrays.asList(
        VisualFeatures.CAPTION,
        VisualFeatures.TAGS,
        VisualFeatures.OBJECTS,
        VisualFeatures.READ),
    new ImageAnalysisOptions()
        .setGenderNeutralCaption(true)
        .setLanguage("en"));

System.out.println("Caption: " + result.getCaption().getText());
System.out.println("Tags: " + result.getTags().size());
System.out.println("Objects: " + result.getObjects().size());
```

---

## 4. Visual Features Reference

| Feature | Description |
|---------|-------------|
| `CAPTION` | Generate human-readable image description |
| `DENSE_CAPTIONS` | Captions for up to 10 regions |
| `READ` | OCR - Extract text from images |
| `TAGS` | Content tags for objects, scenes, actions |
| `OBJECTS` | Detect objects with bounding boxes |
| `SMART_CROPS` | Smart thumbnail regions |
| `PEOPLE` | Detect people with locations |

---

## 5. Error Handling

### 5.1 ✅ CORRECT: HTTP Exception Handling
```java
import com.azure.core.exception.HttpResponseException;

try {
    client.analyzeFromUrl(imageUrl, Arrays.asList(VisualFeatures.CAPTION), null);
} catch (HttpResponseException e) {
    System.out.println("Status: " + e.getResponse().getStatusCode());
    System.out.println("Error: " + e.getMessage());
}
```

---

## 6. Best Practices Checklist

- [ ] Use `DefaultAzureCredentialBuilder` or `KeyCredential` for authentication
- [ ] Use environment variables for endpoint and key configuration
- [ ] Use `setGenderNeutralCaption(true)` for inclusive captions
- [ ] Request only needed visual features to reduce latency
- [ ] Check regional availability for Caption and Dense Captions features
- [ ] Handle `HttpResponseException` appropriately
- [ ] Use async client for better throughput in high-concurrency scenarios
