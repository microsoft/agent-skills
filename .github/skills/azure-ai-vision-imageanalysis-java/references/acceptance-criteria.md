# Azure AI Vision Image Analysis SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-ai-vision-imageanalysis`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/vision/azure-ai-vision-imageanalysis
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Azure SDK Client Imports
```java
import com.azure.ai.vision.imageanalysis.ImageAnalysisClient;
import com.azure.ai.vision.imageanalysis.ImageAnalysisClientBuilder;
import com.azure.ai.vision.imageanalysis.ImageAnalysisAsyncClient;
import com.azure.core.credential.KeyCredential;
```

#### ❌ INCORRECT: Non-existent or Wrong Package
```java
import com.azure.vision.imageanalysis.ImageAnalysisClient;  // Wrong package path
import com.azure.cognitiveservices.vision.ImageAnalysisClient;  // Old API
```

### 1.2 Model Imports
#### ✅ CORRECT: Model Classes from Models Package
```java
import com.azure.ai.vision.imageanalysis.models.ImageAnalysisResult;
import com.azure.ai.vision.imageanalysis.models.VisualFeatures;
import com.azure.ai.vision.imageanalysis.models.ImageAnalysisOptions;
import com.azure.ai.vision.imageanalysis.models.DetectedObject;
import com.azure.ai.vision.imageanalysis.models.DetectedTag;
```

#### ❌ INCORRECT: Wrong Model Package
```java
import com.azure.ai.vision.imageanalysis.ImageAnalysisResult;  // Missing models subpackage
```

---

## 2. Client Creation Patterns

### 2.1 Sync Client with API Key
#### ✅ CORRECT: Using ImageAnalysisClientBuilder
```java
String endpoint = System.getenv("VISION_ENDPOINT");
String key = System.getenv("VISION_KEY");

ImageAnalysisClient client = new ImageAnalysisClientBuilder()
    .endpoint(endpoint)
    .credential(new KeyCredential(key))
    .buildClient();
```

#### ❌ INCORRECT: Direct Instantiation
```java
ImageAnalysisClient client = new ImageAnalysisClient(endpoint, key);
```

### 2.2 Async Client
#### ✅ CORRECT: Using buildAsyncClient
```java
ImageAnalysisAsyncClient asyncClient = new ImageAnalysisClientBuilder()
    .endpoint(endpoint)
    .credential(new KeyCredential(key))
    .buildAsyncClient();
```

### 2.3 DefaultAzureCredential
#### ✅ CORRECT: Using DefaultAzureCredentialBuilder
```java
import com.azure.identity.DefaultAzureCredentialBuilder;

ImageAnalysisClient client = new ImageAnalysisClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

#### ❌ INCORRECT: Direct DefaultAzureCredential
```java
ImageAnalysisClient client = new ImageAnalysisClientBuilder()
    .credential(new DefaultAzureCredential())  // Must use builder
    .buildClient();
```

---

## 3. Visual Features Reference

| Feature | Enum Value | Description |
|---------|------------|-------------|
| Caption | `VisualFeatures.CAPTION` | Generate human-readable image description |
| Dense Captions | `VisualFeatures.DENSE_CAPTIONS` | Captions for up to 10 regions |
| Read (OCR) | `VisualFeatures.READ` | Extract text from images |
| Tags | `VisualFeatures.TAGS` | Content tags for objects, scenes, actions |
| Objects | `VisualFeatures.OBJECTS` | Detect objects with bounding boxes |
| Smart Crops | `VisualFeatures.SMART_CROPS` | Smart thumbnail regions |
| People | `VisualFeatures.PEOPLE` | Detect people with locations |

---

## 4. Image Analysis Patterns

### 4.1 Analyze from File
#### ✅ CORRECT: BinaryData with analyze Method
```java
import com.azure.core.util.BinaryData;
import java.io.File;
import java.util.Arrays;

BinaryData imageData = BinaryData.fromFile(new File("image.jpg").toPath());

ImageAnalysisResult result = client.analyze(
    imageData,
    Arrays.asList(VisualFeatures.CAPTION),
    new ImageAnalysisOptions().setGenderNeutralCaption(true));
```

#### ❌ INCORRECT: Wrong Method or Data Type
```java
client.analyze("image.jpg", features);  // Wrong - string instead of BinaryData
client.analyzeImage(imageData, features);  // Wrong method name
```

### 4.2 Analyze from URL
#### ✅ CORRECT: analyzeFromUrl Method
```java
ImageAnalysisResult result = client.analyzeFromUrl(
    "https://example.com/image.jpg",
    Arrays.asList(VisualFeatures.CAPTION),
    new ImageAnalysisOptions().setGenderNeutralCaption(true));
```

#### ❌ INCORRECT: Using analyze for URLs
```java
client.analyze("https://example.com/image.jpg", features, options);  // Wrong method
```

### 4.3 Caption Generation
#### ✅ CORRECT: Caption with Confidence
```java
ImageAnalysisResult result = client.analyzeFromUrl(
    imageUrl,
    Arrays.asList(VisualFeatures.CAPTION),
    new ImageAnalysisOptions().setGenderNeutralCaption(true));

System.out.printf("Caption: \"%s\" (confidence: %.4f)%n",
    result.getCaption().getText(),
    result.getCaption().getConfidence());
```

### 4.4 OCR Text Extraction
#### ✅ CORRECT: Using VisualFeatures.READ
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

### 4.5 Object Detection
#### ✅ CORRECT: Objects with Bounding Boxes
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

### 4.6 Tag Extraction
#### ✅ CORRECT: Tags with Confidence
```java
ImageAnalysisResult result = client.analyzeFromUrl(
    imageUrl,
    Arrays.asList(VisualFeatures.TAGS),
    null);

for (DetectedTag tag : result.getTags()) {
    System.out.printf("Tag: %s (confidence: %.4f)%n",
        tag.getName(),
        tag.getConfidence());
}
```

### 4.7 People Detection
#### ✅ CORRECT: People with Bounding Boxes
```java
ImageAnalysisResult result = client.analyzeFromUrl(
    imageUrl,
    Arrays.asList(VisualFeatures.PEOPLE),
    null);

for (DetectedPerson person : result.getPeople()) {
    ImageBoundingBox box = person.getBoundingBox();
    System.out.printf("Person at x=%d, y=%d (confidence: %.4f)%n",
        box.getX(), box.getY(), person.getConfidence());
}
```

### 4.8 Smart Cropping
#### ✅ CORRECT: setSmartCropsAspectRatios
```java
ImageAnalysisResult result = client.analyzeFromUrl(
    imageUrl,
    Arrays.asList(VisualFeatures.SMART_CROPS),
    new ImageAnalysisOptions().setSmartCropsAspectRatios(Arrays.asList(1.0, 1.5)));

for (CropRegion crop : result.getSmartCrops()) {
    System.out.printf("Crop region: aspect=%.2f, x=%d, y=%d, w=%d, h=%d%n",
        crop.getAspectRatio(),
        crop.getBoundingBox().getX(),
        crop.getBoundingBox().getY(),
        crop.getBoundingBox().getWidth(),
        crop.getBoundingBox().getHeight());
}
```

### 4.9 Dense Captions
#### ✅ CORRECT: Multiple Region Captions
```java
ImageAnalysisResult result = client.analyzeFromUrl(
    imageUrl,
    Arrays.asList(VisualFeatures.DENSE_CAPTIONS),
    new ImageAnalysisOptions().setGenderNeutralCaption(true));

for (DenseCaption caption : result.getDenseCaptions()) {
    System.out.printf("Caption: \"%s\" (confidence: %.4f)%n",
        caption.getText(),
        caption.getConfidence());
}
```

---

## 5. Multiple Features Pattern

### 5.1 Analyzing Multiple Features
#### ✅ CORRECT: List of VisualFeatures
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

// Access all results
System.out.println("Caption: " + result.getCaption().getText());
System.out.println("Tags: " + result.getTags().size());
System.out.println("Objects: " + result.getObjects().size());
System.out.println("Text blocks: " + result.getRead().getBlocks().size());
```

---

## 6. Async Patterns

### 6.1 Async Analysis
#### ✅ CORRECT: Reactive Subscription
```java
asyncClient.analyzeFromUrl(
    imageUrl,
    Arrays.asList(VisualFeatures.CAPTION),
    null)
    .subscribe(
        result -> System.out.println("Caption: " + result.getCaption().getText()),
        error -> System.err.println("Error: " + error.getMessage()),
        () -> System.out.println("Complete")
    );
```

---

## 7. Error Handling

### 7.1 HttpResponseException
#### ✅ CORRECT: Azure SDK Exception Handling
```java
import com.azure.core.exception.HttpResponseException;

try {
    client.analyzeFromUrl(imageUrl, Arrays.asList(VisualFeatures.CAPTION), null);
} catch (HttpResponseException e) {
    System.out.println("Status: " + e.getResponse().getStatusCode());
    System.out.println("Error: " + e.getMessage());
}
```

#### ❌ INCORRECT: Generic Exception Only
```java
try {
    client.analyzeFromUrl(imageUrl, features, options);
} catch (Exception e) {
    // Missing specific HttpResponseException handling
}
```

---

## 8. Environment Configuration

### 8.1 Environment Variables
#### ✅ CORRECT: Reading from Environment
```java
String endpoint = System.getenv("VISION_ENDPOINT");
String key = System.getenv("VISION_KEY");
```

#### ❌ INCORRECT: Hardcoded Credentials
```java
String endpoint = "https://myresource.cognitiveservices.azure.com/";
String key = "abc123secretkey";  // Never hardcode credentials
```

---

## 9. Image Requirements

### 9.1 Supported Formats
- JPEG, PNG, GIF, BMP, WEBP, ICO, TIFF, MPO

### 9.2 Size Limits
- Maximum size: 20 MB
- Dimensions: 50x50 to 16000x16000 pixels

### 9.3 Regional Availability
- Caption and Dense Captions require GPU-supported regions
- Check supported regions before deployment

---

## 10. Best Practices

### 10.1 Performance
- Request only needed visual features to reduce latency
- Use async client for high-throughput scenarios
- Consider caching results for repeated analysis

### 10.2 Gender-Neutral Captions
- Enable `setGenderNeutralCaption(true)` for inclusive descriptions

### 10.3 Language Support
- Use `setLanguage()` for localized results where supported