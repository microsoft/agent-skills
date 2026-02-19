# Azure AI Vision Image Analysis Acceptance Criteria

**SDK**: `azure-ai-vision-imageanalysis`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Purpose**: Skill testing acceptance criteria for validating generated image analysis code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Sync Client with Entra ID (Recommended)
```python
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.identity import DefaultAzureCredential
```

#### ✅ CORRECT: Sync Client with API Key
```python
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.core.credentials import AzureKeyCredential
```

#### ✅ CORRECT: Async Client with Entra ID
```python
from azure.ai.vision.imageanalysis.aio import ImageAnalysisClient
from azure.identity.aio import DefaultAzureCredential
```

#### ✅ CORRECT: Async Client with API Key
```python
from azure.ai.vision.imageanalysis.aio import ImageAnalysisClient
from azure.core.credentials.aio import AsyncTokenCredential
```

### 1.2 Model/Enum Imports

#### ✅ CORRECT: Visual Features
```python
from azure.ai.vision.imageanalysis.models import VisualFeatures
```

#### ✅ CORRECT: Exception Handling
```python
from azure.core.exceptions import HttpResponseError
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong module paths
```python
# WRONG - VisualFeatures not in main module
from azure.ai.vision.imageanalysis import VisualFeatures

# WRONG - importing non-existent ImageAnalysis class
from azure.ai.vision import ImageAnalysis

# WRONG - old SDK patterns
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
```

#### ❌ INCORRECT: Mixing sync and async credentials
```python
# WRONG - using sync credential with async client
from azure.ai.vision.imageanalysis.aio import ImageAnalysisClient
from azure.identity import DefaultAzureCredential  # Should be from .aio

async with ImageAnalysisClient(endpoint=endpoint, credential=DefaultAzureCredential()):
    ...
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Sync Client with Entra ID
```python
import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.identity import DefaultAzureCredential

client = ImageAnalysisClient(
    endpoint=os.environ["VISION_ENDPOINT"],
    credential=DefaultAzureCredential()
)
```

### 2.2 ✅ CORRECT: Sync Client with API Key
```python
import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.core.credentials import AzureKeyCredential

client = ImageAnalysisClient(
    endpoint=os.environ["VISION_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["VISION_KEY"])
)
```

### 2.3 ✅ CORRECT: Async Client
```python
from azure.ai.vision.imageanalysis.aio import ImageAnalysisClient
from azure.identity.aio import DefaultAzureCredential

async with ImageAnalysisClient(
    endpoint=os.environ["VISION_ENDPOINT"],
    credential=DefaultAzureCredential()
) as client:
    result = await client.analyze_from_url(...)
```

### 2.4 ✅ CORRECT: Context Manager for Resource Cleanup
```python
with ImageAnalysisClient(endpoint=endpoint, credential=credential) as client:
    result = client.analyze_from_url(
        image_url=image_url,
        visual_features=[VisualFeatures.CAPTION]
    )
```

### 2.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials
```python
# WRONG - Never hardcode keys
client = ImageAnalysisClient(
    endpoint="https://myresource.cognitiveservices.azure.com",
    credential=AzureKeyCredential("hardcoded-key-12345")
)
```

#### ❌ INCORRECT: Wrong parameter names
```python
# WRONG - using 'url' instead of 'endpoint'
client = ImageAnalysisClient(url=endpoint, credential=cred)

# WRONG - using 'api_key' instead of credential
client = ImageAnalysisClient(endpoint=endpoint, api_key=key)
```

#### ❌ INCORRECT: Not using context manager
```python
# WRONG - no cleanup
client = ImageAnalysisClient(endpoint=endpoint, credential=credential)
result = client.analyze_from_url(...)
# Missing: client.close() or 'with' statement
```

---

## 3. Image Analysis Patterns

### 3.1 ✅ CORRECT: Analyze from URL with Caption
```python
from azure.ai.vision.imageanalysis.models import VisualFeatures

result = client.analyze_from_url(
    image_url="https://example.com/image.jpg",
    visual_features=[VisualFeatures.CAPTION]
)

if result.caption:
    print(f"Caption: {result.caption.text}")
    print(f"Confidence: {result.caption.confidence}")
```

### 3.2 ✅ CORRECT: Analyze from File
```python
with open("image.jpg", "rb") as f:
    image_data = f.read()

result = client.analyze(
    image_data=image_data,
    visual_features=[VisualFeatures.CAPTION, VisualFeatures.TAGS]
)
```

### 3.3 ✅ CORRECT: Multiple Visual Features
```python
result = client.analyze_from_url(
    image_url=image_url,
    visual_features=[
        VisualFeatures.CAPTION,
        VisualFeatures.TAGS,
        VisualFeatures.OBJECTS,
        VisualFeatures.READ,
        VisualFeatures.PEOPLE,
        VisualFeatures.DENSE_CAPTIONS,
        VisualFeatures.SMART_CROPS,
    ],
    gender_neutral_caption=True,
    language="en"
)
```

### 3.4 ✅ CORRECT: Tags Analysis
```python
result = client.analyze_from_url(
    image_url=image_url,
    visual_features=[VisualFeatures.TAGS]
)

if result.tags:
    for tag in result.tags.list:
        print(f"Tag: {tag.name} (confidence: {tag.confidence:.2f})")
```

### 3.5 ✅ CORRECT: Object Detection
```python
result = client.analyze_from_url(
    image_url=image_url,
    visual_features=[VisualFeatures.OBJECTS]
)

if result.objects:
    for obj in result.objects.list:
        print(f"Object: {obj.tags[0].name}")
        box = obj.bounding_box
        print(f"  Bounding box: x={box.x}, y={box.y}, w={box.width}, h={box.height}")
```

### 3.6 ✅ CORRECT: OCR (Text Extraction)
```python
result = client.analyze_from_url(
    image_url=image_url,
    visual_features=[VisualFeatures.READ]
)

if result.read:
    for block in result.read.blocks:
        for line in block.lines:
            print(f"Line: {line.text}")
            for word in line.words:
                print(f"  Word: {word.text} (confidence: {word.confidence:.2f})")
```

### 3.7 ✅ CORRECT: Dense Captions (Multiple Regions)
```python
result = client.analyze_from_url(
    image_url=image_url,
    visual_features=[VisualFeatures.DENSE_CAPTIONS]
)

if result.dense_captions:
    for caption in result.dense_captions.list:
        print(f"Caption: {caption.text}")
        print(f"  Bounding box: {caption.bounding_box}")
```

### 3.8 ✅ CORRECT: People Detection
```python
result = client.analyze_from_url(
    image_url=image_url,
    visual_features=[VisualFeatures.PEOPLE]
)

if result.people:
    for person in result.people.list:
        print(f"Person confidence: {person.confidence:.2f}")
        box = person.bounding_box
        print(f"  Bounding box: x={box.x}, y={box.y}, w={box.width}, h={box.height}")
```

### 3.9 ✅ CORRECT: Smart Cropping
```python
result = client.analyze_from_url(
    image_url=image_url,
    visual_features=[VisualFeatures.SMART_CROPS],
    smart_crops_aspect_ratios=[0.9, 1.33, 1.78]  # Portrait, 4:3, 16:9
)

if result.smart_crops:
    for crop in result.smart_crops.list:
        print(f"Aspect ratio: {crop.aspect_ratio}")
        box = crop.bounding_box
        print(f"  Crop region: x={box.x}, y={box.y}, w={box.width}, h={box.height}")
```

### 3.10 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong visual feature enum usage
```python
# WRONG - string instead of VisualFeatures enum
result = client.analyze_from_url(
    image_url=image_url,
    visual_features=["CAPTION", "TAGS"]  # Should use VisualFeatures.CAPTION, etc.
)
```

#### ❌ INCORRECT: Accessing result properties directly
```python
# WRONG - result.caption is an object, not a string
for caption in result.caption:  # Can't iterate
     print(caption)
```

To correctly access caption, always check if it exists first, then access the `.text` property on the result.caption object.

#### ❌ INCORRECT: Missing error handling
```python
# WRONG - no error handling
result = client.analyze_from_url(...)  # May fail with invalid URL or auth error
for tag in result.tags.list:
     print(tag.name)
```

Always wrap client calls in try-except blocks to handle `HttpResponseError` exceptions that may occur due to invalid URLs, authentication failures, or other API errors.

#### ❌ INCORRECT: Wrong method for analyzing files
```python
# WRONG - analyze_from_url with file data
with open("image.jpg", "rb") as f:
     result = client.analyze_from_url(
          image_url=f.read(),  # Should use analyze() method
          visual_features=[VisualFeatures.CAPTION]
     )
```

For file-based analysis, read the file contents and use the `analyze()` method with the `image_data` parameter instead of `analyze_from_url()`.

---

## 4. Async Patterns

### 4.1 ✅ CORRECT: Full Async Example
```python
import asyncio
import os
from azure.ai.vision.imageanalysis.aio import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.identity.aio import DefaultAzureCredential

async def analyze_image():
    async with ImageAnalysisClient(
        endpoint=os.environ["VISION_ENDPOINT"],
        credential=DefaultAzureCredential()
    ) as client:
        result = await client.analyze_from_url(
            image_url="https://example.com/image.jpg",
            visual_features=[VisualFeatures.CAPTION]
        )
        print(result.caption.text)

asyncio.run(analyze_image())
```

### 4.2 ✅ CORRECT: Async File Analysis
```python
async def analyze_file():
    async with ImageAnalysisClient(
        endpoint=os.environ["VISION_ENDPOINT"],
        credential=DefaultAzureCredential()
    ) as client:
        with open("image.jpg", "rb") as f:
            image_data = f.read()
        
        result = await client.analyze(
            image_data=image_data,
            visual_features=[VisualFeatures.CAPTION]
        )
        return result.caption.text
```

### 4.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing await
```python
# WRONG - missing await for async operations
async def bad_example():
     result = client.analyze_from_url(...)  # Missing await
     print(result.caption.text)
```

Always use the `await` keyword when calling async methods on async clients to properly wait for the coroutine to complete.

#### ❌ INCORRECT: Wrong credential type
```python
# WRONG - using sync credential with async client
from azure.ai.vision.imageanalysis.aio import ImageAnalysisClient
from azure.identity import DefaultAzureCredential  # Should be from .aio
```

When using the async client from `azure.ai.vision.imageanalysis.aio`, always import the async credential from `azure.identity.aio` to avoid type mismatches and runtime errors.

#### ❌ INCORRECT: Not using async context manager
```python
# WRONG - no proper cleanup
client = ImageAnalysisClient(endpoint=endpoint, credential=credential)
result = await client.analyze_from_url(...)
```

Always use `async with` when creating async clients to ensure proper resource cleanup and connection management.

---

## 5. Error Handling Patterns

### 5.1 ✅ CORRECT: Basic Error Handling
```python
from azure.core.exceptions import HttpResponseError

try:
    result = client.analyze_from_url(
        image_url=image_url,
        visual_features=[VisualFeatures.CAPTION]
    )
except HttpResponseError as e:
    print(f"Status code: {e.status_code}")
    print(f"Reason: {e.reason}")
    print(f"Message: {e.error.message}")
```

### 5.2 ✅ CORRECT: Check for Result Content
```python
result = client.analyze_from_url(
    image_url=image_url,
    visual_features=[VisualFeatures.CAPTION, VisualFeatures.TAGS]
)

if result.caption:
    print(f"Caption: {result.caption.text}")
else:
    print("No caption available")

if result.tags:
    for tag in result.tags.list:
        print(f"Tag: {tag.name}")
else:
    print("No tags available")
```

### 5.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Ignoring errors
```python
# WRONG - no error handling
try:
     result = client.analyze_from_url(...)
except:
     pass  # Silent failure
```

Never use bare `except:` clauses. Always catch specific exceptions like `HttpResponseError` and log or re-raise them to ensure errors are properly handled and visible.

#### ❌ INCORRECT: Accessing None values
```python
# WRONG - assuming caption always exists
print(result.caption.text)  # Crashes if caption is None
```

Always check if a result property exists (is not None) before accessing its nested attributes to avoid AttributeError crashes.

---

## 6. Environment Variables

### Required Variables
```bash
VISION_ENDPOINT=https://<resource>.cognitiveservices.azure.com
```

### Optional (for API Key auth)
```bash
VISION_KEY=<your-api-key>
```

---

## 7. Test Scenarios Checklist

### Basic Operations
- [ ] Client creation with Entra ID
- [ ] Client creation with API Key
- [ ] Context manager for cleanup
- [ ] Analyze from URL with caption
- [ ] Analyze from file

### Visual Features
- [ ] Caption analysis
- [ ] Tags analysis
- [ ] Object detection with bounding boxes
- [ ] OCR/Text extraction (READ)
- [ ] Dense captions (multiple regions)
- [ ] People detection
- [ ] Smart cropping with aspect ratios

### Async
- [ ] Async client creation
- [ ] Async analyze_from_url
- [ ] Async analyze (file)
- [ ] Proper await usage
- [ ] Async context manager

### Error Handling
- [ ] HttpResponseError handling
- [ ] Check result content before accessing
- [ ] Invalid URL handling
- [ ] Authentication errors

### Advanced
- [ ] Multiple visual features in one call
- [ ] Gender-neutral captions
- [ ] Language specification
- [ ] Confidence score extraction
- [ ] Bounding box coordinates

---

## 8. Quick Reference: Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `ImportError: cannot import name 'ImageAnalysisClient'` | Wrong module | Import from `azure.ai.vision.imageanalysis` |
| `AttributeError: 'NoneType' has no attribute 'text'` | Not checking if caption exists | Use `if result.caption:` before access |
| `ValueError: Invalid visual feature` | String instead of enum | Use `VisualFeatures.CAPTION` not `"CAPTION"` |
| `HttpResponseError: 401 Unauthorized` | Auth failure | Check endpoint and credentials |
| `HttpResponseError: 400 Bad Request` | Invalid image or URL | Verify image format and URL accessibility |
| `RuntimeError: coroutine was never awaited` | Missing await in async | Add `await` to async method calls |
| `TypeError: object is not async context manager` | Using sync client as async | Import from `azure.ai.vision.imageanalysis.aio` |
| `FileNotFoundError` | Image file path | Verify file exists and path is absolute |

