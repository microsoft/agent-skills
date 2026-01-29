# Azure AI Vision Image Analysis Java SDK - Examples

Comprehensive code examples for the Azure AI Vision Image Analysis SDK for Java.

## Table of Contents

- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Visual Features](#visual-features)
- [Generate Caption](#generate-caption)
- [Extract Text (OCR)](#extract-text-ocr)
- [Detect Objects](#detect-objects)
- [Get Tags](#get-tags)
- [Detect People](#detect-people)
- [Smart Cropping](#smart-cropping)
- [Dense Captions](#dense-captions)
- [Multiple Features](#multiple-features)
- [Async Patterns](#async-patterns)
- [Error Handling](#error-handling)
- [Complete Application Example](#complete-application-example)

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-ai-vision-imageanalysis</artifactId>
    <version>1.1.0-beta.1</version>
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
import com.azure.ai.vision.imageanalysis.ImageAnalysisClient;
import com.azure.ai.vision.imageanalysis.ImageAnalysisClientBuilder;
import com.azure.core.credential.KeyCredential;

String endpoint = System.getenv("VISION_ENDPOINT");
String key = System.getenv("VISION_KEY");

ImageAnalysisClient client = new ImageAnalysisClientBuilder()
    .endpoint(endpoint)
    .credential(new KeyCredential(key))
    .buildClient();
```

### With DefaultAzureCredential (Recommended)

```java
import com.azure.identity.DefaultAzureCredentialBuilder;

ImageAnalysisClient client = new ImageAnalysisClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### Async Client

```java
import com.azure.ai.vision.imageanalysis.ImageAnalysisAsyncClient;

ImageAnalysisAsyncClient asyncClient = new ImageAnalysisClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncClient();
```

## Visual Features

| Feature | Description |
|---------|-------------|
| `CAPTION` | Generate human-readable image description |
| `DENSE_CAPTIONS` | Captions for up to 10 regions |
| `READ` | OCR - Extract text from images |
| `TAGS` | Content tags for objects, scenes, actions |
| `OBJECTS` | Detect objects with bounding boxes |
| `SMART_CROPS` | Smart thumbnail regions |
| `PEOPLE` | Detect people with locations |

## Generate Caption

### From File

```java
import com.azure.ai.vision.imageanalysis.models.*;
import com.azure.core.util.BinaryData;
import java.io.File;
import java.util.Arrays;

// Load image from file
File imageFile = new File("photo.jpg");
BinaryData imageData = BinaryData.fromFile(imageFile.toPath());

// Analyze with caption
ImageAnalysisResult result = client.analyze(
    imageData,
    Arrays.asList(VisualFeatures.CAPTION),
    new ImageAnalysisOptions().setGenderNeutralCaption(true));

// Get caption
CaptionResult caption = result.getCaption();
System.out.printf("Caption: \"%s\" (confidence: %.4f)%n",
    caption.getText(),
    caption.getConfidence());
```

### From URL

```java
String imageUrl = "https://example.com/photo.jpg";

ImageAnalysisResult result = client.analyzeFromUrl(
    imageUrl,
    Arrays.asList(VisualFeatures.CAPTION),
    new ImageAnalysisOptions().setGenderNeutralCaption(true));

System.out.printf("Caption: \"%s\"%n", result.getCaption().getText());
```

### With Language

```java
ImageAnalysisResult result = client.analyzeFromUrl(
    imageUrl,
    Arrays.asList(VisualFeatures.CAPTION),
    new ImageAnalysisOptions()
        .setGenderNeutralCaption(true)
        .setLanguage("en"));  // Supported: en, es, fr, de, it, pt, ja, ko, zh
```

## Extract Text (OCR)

```java
File documentImage = new File("document.jpg");
BinaryData imageData = BinaryData.fromFile(documentImage.toPath());

ImageAnalysisResult result = client.analyze(
    imageData,
    Arrays.asList(VisualFeatures.READ),
    null);

ReadResult readResult = result.getRead();

System.out.println("=== Extracted Text ===");
for (DetectedTextBlock block : readResult.getBlocks()) {
    System.out.println("Block:");
    
    for (DetectedTextLine line : block.getLines()) {
        System.out.printf("  Line: '%s'%n", line.getText());
        
        // Get bounding polygon
        List<ImagePoint> polygon = line.getBoundingPolygon();
        System.out.printf("    Bounding polygon: [");
        for (ImagePoint point : polygon) {
            System.out.printf("(%d,%d) ", point.getX(), point.getY());
        }
        System.out.println("]");
        
        // Get individual words
        for (DetectedTextWord word : line.getWords()) {
            System.out.printf("    Word: '%s' (confidence: %.4f)%n",
                word.getText(),
                word.getConfidence());
        }
    }
}
```

### Extract Text from URL

```java
String documentUrl = "https://example.com/receipt.jpg";

ImageAnalysisResult result = client.analyzeFromUrl(
    documentUrl,
    Arrays.asList(VisualFeatures.READ),
    null);

// Collect all text
StringBuilder fullText = new StringBuilder();
for (DetectedTextBlock block : result.getRead().getBlocks()) {
    for (DetectedTextLine line : block.getLines()) {
        fullText.append(line.getText()).append("\n");
    }
}

System.out.println("Full extracted text:");
System.out.println(fullText.toString());
```

## Detect Objects

```java
String imageUrl = "https://example.com/street-scene.jpg";

ImageAnalysisResult result = client.analyzeFromUrl(
    imageUrl,
    Arrays.asList(VisualFeatures.OBJECTS),
    null);

System.out.println("=== Detected Objects ===");
for (DetectedObject obj : result.getObjects()) {
    // Get the primary tag (highest confidence)
    DetectedTag primaryTag = obj.getTags().get(0);
    
    System.out.printf("Object: %s (confidence: %.4f)%n",
        primaryTag.getName(),
        primaryTag.getConfidence());
    
    // Get bounding box
    ImageBoundingBox box = obj.getBoundingBox();
    System.out.printf("  Location: x=%d, y=%d, width=%d, height=%d%n",
        box.getX(), box.getY(), box.getWidth(), box.getHeight());
    
    // Additional tags for this object
    if (obj.getTags().size() > 1) {
        System.out.println("  Additional tags:");
        for (int i = 1; i < obj.getTags().size(); i++) {
            DetectedTag tag = obj.getTags().get(i);
            System.out.printf("    - %s (%.4f)%n", tag.getName(), tag.getConfidence());
        }
    }
}

System.out.printf("Total objects detected: %d%n", result.getObjects().size());
```

## Get Tags

```java
String imageUrl = "https://example.com/nature.jpg";

ImageAnalysisResult result = client.analyzeFromUrl(
    imageUrl,
    Arrays.asList(VisualFeatures.TAGS),
    null);

System.out.println("=== Image Tags ===");

// Sort by confidence
List<DetectedTag> sortedTags = new ArrayList<>(result.getTags());
sortedTags.sort((a, b) -> Double.compare(b.getConfidence(), a.getConfidence()));

for (DetectedTag tag : sortedTags) {
    System.out.printf("%-20s (confidence: %.4f)%n",
        tag.getName(),
        tag.getConfidence());
}

// Filter high-confidence tags (>80%)
System.out.println("\nHigh-confidence tags (>80%):");
for (DetectedTag tag : sortedTags) {
    if (tag.getConfidence() > 0.80) {
        System.out.println("  - " + tag.getName());
    }
}
```

## Detect People

```java
String imageUrl = "https://example.com/group-photo.jpg";

ImageAnalysisResult result = client.analyzeFromUrl(
    imageUrl,
    Arrays.asList(VisualFeatures.PEOPLE),
    null);

System.out.println("=== Detected People ===");
System.out.printf("Number of people: %d%n", result.getPeople().size());

int personIndex = 1;
for (DetectedPerson person : result.getPeople()) {
    ImageBoundingBox box = person.getBoundingBox();
    
    System.out.printf("Person %d:%n", personIndex++);
    System.out.printf("  Confidence: %.4f%n", person.getConfidence());
    System.out.printf("  Location: x=%d, y=%d, width=%d, height=%d%n",
        box.getX(), box.getY(), box.getWidth(), box.getHeight());
    
    // Calculate center point
    int centerX = box.getX() + box.getWidth() / 2;
    int centerY = box.getY() + box.getHeight() / 2;
    System.out.printf("  Center: (%d, %d)%n", centerX, centerY);
}
```

## Smart Cropping

```java
String imageUrl = "https://example.com/landscape.jpg";

// Request crops with specific aspect ratios
ImageAnalysisResult result = client.analyzeFromUrl(
    imageUrl,
    Arrays.asList(VisualFeatures.SMART_CROPS),
    new ImageAnalysisOptions()
        .setSmartCropsAspectRatios(Arrays.asList(1.0, 1.5, 0.75)));  // 1:1, 3:2, 3:4

System.out.println("=== Smart Crop Regions ===");
for (CropRegion crop : result.getSmartCrops()) {
    ImageBoundingBox box = crop.getBoundingBox();
    
    System.out.printf("Aspect ratio: %.2f%n", crop.getAspectRatio());
    System.out.printf("  Region: x=%d, y=%d, width=%d, height=%d%n",
        box.getX(), box.getY(), box.getWidth(), box.getHeight());
}
```

### Use Smart Crops for Thumbnails

```java
// Get square thumbnail region
ImageAnalysisResult result = client.analyzeFromUrl(
    imageUrl,
    Arrays.asList(VisualFeatures.SMART_CROPS),
    new ImageAnalysisOptions()
        .setSmartCropsAspectRatios(Arrays.asList(1.0)));  // Square

CropRegion squareCrop = result.getSmartCrops().get(0);
ImageBoundingBox box = squareCrop.getBoundingBox();

// Use these coordinates to crop your image
System.out.printf("Thumbnail region: x=%d, y=%d, size=%dx%d%n",
    box.getX(), box.getY(), box.getWidth(), box.getHeight());
```

## Dense Captions

```java
String imageUrl = "https://example.com/complex-scene.jpg";

ImageAnalysisResult result = client.analyzeFromUrl(
    imageUrl,
    Arrays.asList(VisualFeatures.DENSE_CAPTIONS),
    new ImageAnalysisOptions().setGenderNeutralCaption(true));

System.out.println("=== Dense Captions ===");
int regionIndex = 1;
for (DenseCaption caption : result.getDenseCaptions()) {
    ImageBoundingBox box = caption.getBoundingBox();
    
    System.out.printf("Region %d:%n", regionIndex++);
    System.out.printf("  Caption: \"%s\"%n", caption.getText());
    System.out.printf("  Confidence: %.4f%n", caption.getConfidence());
    System.out.printf("  Location: x=%d, y=%d, width=%d, height=%d%n",
        box.getX(), box.getY(), box.getWidth(), box.getHeight());
}
```

## Multiple Features

Analyze with multiple features in a single request.

```java
String imageUrl = "https://example.com/photo.jpg";

ImageAnalysisResult result = client.analyzeFromUrl(
    imageUrl,
    Arrays.asList(
        VisualFeatures.CAPTION,
        VisualFeatures.TAGS,
        VisualFeatures.OBJECTS,
        VisualFeatures.PEOPLE,
        VisualFeatures.READ),
    new ImageAnalysisOptions()
        .setGenderNeutralCaption(true)
        .setLanguage("en"));

// Caption
System.out.println("=== Caption ===");
System.out.printf("\"%s\" (%.4f)%n",
    result.getCaption().getText(),
    result.getCaption().getConfidence());

// Tags
System.out.println("\n=== Tags ===");
for (DetectedTag tag : result.getTags()) {
    if (tag.getConfidence() > 0.7) {
        System.out.printf("  %s (%.2f)%n", tag.getName(), tag.getConfidence());
    }
}

// Objects
System.out.println("\n=== Objects ===");
System.out.printf("  Count: %d%n", result.getObjects().size());
for (DetectedObject obj : result.getObjects()) {
    System.out.printf("  - %s%n", obj.getTags().get(0).getName());
}

// People
System.out.println("\n=== People ===");
System.out.printf("  Count: %d%n", result.getPeople().size());

// Text
System.out.println("\n=== Text ===");
int lineCount = 0;
for (DetectedTextBlock block : result.getRead().getBlocks()) {
    lineCount += block.getLines().size();
}
System.out.printf("  Lines of text: %d%n", lineCount);

// Metadata
System.out.println("\n=== Image Metadata ===");
System.out.printf("  Dimensions: %d x %d%n",
    result.getMetadata().getWidth(),
    result.getMetadata().getHeight());
System.out.printf("  Model: %s%n", result.getModelVersion());
```

## Async Patterns

### Basic Async Analysis

```java
ImageAnalysisAsyncClient asyncClient = new ImageAnalysisClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncClient();

String imageUrl = "https://example.com/photo.jpg";

asyncClient.analyzeFromUrl(
    imageUrl,
    Arrays.asList(VisualFeatures.CAPTION, VisualFeatures.TAGS),
    new ImageAnalysisOptions().setGenderNeutralCaption(true))
    .subscribe(
        result -> {
            System.out.println("Caption: " + result.getCaption().getText());
            System.out.println("Tags: " + result.getTags().size());
        },
        error -> System.err.println("Error: " + error.getMessage()),
        () -> System.out.println("Analysis complete")
    );

// Keep application running
Thread.sleep(10000);
```

### Parallel Analysis

```java
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

List<String> imageUrls = Arrays.asList(
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg",
    "https://example.com/image3.jpg"
);

Flux.fromIterable(imageUrls)
    .flatMap(url -> asyncClient.analyzeFromUrl(
        url,
        Arrays.asList(VisualFeatures.CAPTION),
        null)
        .map(result -> new ImageResult(url, result.getCaption().getText())))
    .subscribe(
        imageResult -> System.out.printf("%s: %s%n", 
            imageResult.url, imageResult.caption),
        error -> System.err.println("Error: " + error.getMessage())
    );

// Helper class
class ImageResult {
    String url;
    String caption;
    
    ImageResult(String url, String caption) {
        this.url = url;
        this.caption = caption;
    }
}
```

## Error Handling

```java
import com.azure.core.exception.HttpResponseException;

try {
    ImageAnalysisResult result = client.analyzeFromUrl(
        "invalid-url",
        Arrays.asList(VisualFeatures.CAPTION),
        null);
        
} catch (HttpResponseException e) {
    int statusCode = e.getResponse().getStatusCode();
    System.err.println("HTTP Status: " + statusCode);
    System.err.println("Error: " + e.getMessage());
    
    switch (statusCode) {
        case 400:
            System.err.println("Bad request - check image URL or format");
            break;
        case 401:
            System.err.println("Unauthorized - check API key");
            break;
        case 404:
            System.err.println("Resource not found");
            break;
        case 415:
            System.err.println("Unsupported media type - check image format");
            break;
        case 429:
            System.err.println("Rate limited - retry with backoff");
            break;
        default:
            System.err.println("Unexpected error");
    }
} catch (Exception e) {
    System.err.println("Unexpected error: " + e.getMessage());
}
```

## Complete Application Example

```java
import com.azure.ai.vision.imageanalysis.ImageAnalysisClient;
import com.azure.ai.vision.imageanalysis.ImageAnalysisClientBuilder;
import com.azure.ai.vision.imageanalysis.models.*;
import com.azure.core.util.BinaryData;
import com.azure.identity.DefaultAzureCredentialBuilder;

import java.io.File;
import java.util.*;

public class ImageAnalyzer {
    
    private final ImageAnalysisClient client;
    
    public ImageAnalyzer() {
        this.client = new ImageAnalysisClientBuilder()
            .endpoint(System.getenv("VISION_ENDPOINT"))
            .credential(new DefaultAzureCredentialBuilder().build())
            .buildClient();
    }
    
    public ImageAnalysisReport analyzeImage(String imagePath) {
        File imageFile = new File(imagePath);
        BinaryData imageData = BinaryData.fromFile(imageFile.toPath());
        
        ImageAnalysisResult result = client.analyze(
            imageData,
            Arrays.asList(
                VisualFeatures.CAPTION,
                VisualFeatures.TAGS,
                VisualFeatures.OBJECTS,
                VisualFeatures.PEOPLE,
                VisualFeatures.READ),
            new ImageAnalysisOptions()
                .setGenderNeutralCaption(true)
                .setLanguage("en"));
        
        return buildReport(imagePath, result);
    }
    
    public ImageAnalysisReport analyzeImageUrl(String imageUrl) {
        ImageAnalysisResult result = client.analyzeFromUrl(
            imageUrl,
            Arrays.asList(
                VisualFeatures.CAPTION,
                VisualFeatures.TAGS,
                VisualFeatures.OBJECTS,
                VisualFeatures.PEOPLE,
                VisualFeatures.READ),
            new ImageAnalysisOptions()
                .setGenderNeutralCaption(true)
                .setLanguage("en"));
        
        return buildReport(imageUrl, result);
    }
    
    private ImageAnalysisReport buildReport(String source, ImageAnalysisResult result) {
        // Extract caption
        String caption = result.getCaption().getText();
        double captionConfidence = result.getCaption().getConfidence();
        
        // Extract high-confidence tags
        List<String> tags = new ArrayList<>();
        for (DetectedTag tag : result.getTags()) {
            if (tag.getConfidence() > 0.7) {
                tags.add(tag.getName());
            }
        }
        
        // Extract objects
        List<String> objects = new ArrayList<>();
        for (DetectedObject obj : result.getObjects()) {
            objects.add(obj.getTags().get(0).getName());
        }
        
        // Count people
        int peopleCount = result.getPeople().size();
        
        // Extract text
        StringBuilder extractedText = new StringBuilder();
        for (DetectedTextBlock block : result.getRead().getBlocks()) {
            for (DetectedTextLine line : block.getLines()) {
                extractedText.append(line.getText()).append("\n");
            }
        }
        
        return new ImageAnalysisReport(
            source,
            caption,
            captionConfidence,
            tags,
            objects,
            peopleCount,
            extractedText.toString().trim(),
            result.getMetadata().getWidth(),
            result.getMetadata().getHeight()
        );
    }
    
    // Report class
    public static class ImageAnalysisReport {
        public final String source;
        public final String caption;
        public final double captionConfidence;
        public final List<String> tags;
        public final List<String> objects;
        public final int peopleCount;
        public final String extractedText;
        public final int width;
        public final int height;
        
        public ImageAnalysisReport(String source, String caption, double captionConfidence,
                                   List<String> tags, List<String> objects, int peopleCount,
                                   String extractedText, int width, int height) {
            this.source = source;
            this.caption = caption;
            this.captionConfidence = captionConfidence;
            this.tags = tags;
            this.objects = objects;
            this.peopleCount = peopleCount;
            this.extractedText = extractedText;
            this.width = width;
            this.height = height;
        }
        
        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            sb.append("=== Image Analysis Report ===\n");
            sb.append(String.format("Source: %s\n", source));
            sb.append(String.format("Dimensions: %dx%d\n", width, height));
            sb.append(String.format("Caption: \"%s\" (%.2f%%)\n", caption, captionConfidence * 100));
            sb.append(String.format("Tags: %s\n", String.join(", ", tags)));
            sb.append(String.format("Objects: %s\n", String.join(", ", objects)));
            sb.append(String.format("People detected: %d\n", peopleCount));
            if (!extractedText.isEmpty()) {
                sb.append(String.format("Extracted text:\n%s\n", extractedText));
            }
            return sb.toString();
        }
    }
    
    public static void main(String[] args) {
        ImageAnalyzer analyzer = new ImageAnalyzer();
        
        // Analyze from URL
        String imageUrl = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/ComputerVision/Images/landmark.jpg";
        
        try {
            ImageAnalysisReport report = analyzer.analyzeImageUrl(imageUrl);
            System.out.println(report);
        } catch (Exception e) {
            System.err.println("Analysis failed: " + e.getMessage());
        }
    }
}
```

## Environment Variables

```bash
VISION_ENDPOINT=https://<resource>.cognitiveservices.azure.com/
VISION_KEY=<your-api-key>

# For DefaultAzureCredential
AZURE_CLIENT_ID=<service-principal-client-id>
AZURE_CLIENT_SECRET=<service-principal-secret>
AZURE_TENANT_ID=<tenant-id>
```

## Image Requirements

- **Formats**: JPEG, PNG, GIF, BMP, WEBP, ICO, TIFF, MPO
- **Size**: Less than 20 MB
- **Dimensions**: 50x50 to 16000x16000 pixels

## Regional Availability

Caption and Dense Captions require GPU-supported regions. Check [supported regions](https://learn.microsoft.com/azure/ai-services/computer-vision/concept-describe-images-40) before deployment.

## Best Practices

1. **Use DefaultAzureCredential** — Prefer managed identity over API keys
2. **Combine features** — Request multiple features in one call for efficiency
3. **Check confidence scores** — Filter results based on confidence thresholds
4. **Use async for batches** — Process multiple images in parallel
5. **Handle regional limits** — Caption features require specific regions
6. **Optimize image size** — Resize large images before sending
7. **Enable gender-neutral captions** — Use inclusive language in captions
8. **Implement retry logic** — Handle rate limiting with exponential backoff
