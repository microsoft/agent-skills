# Azure AI Content Safety SDK Acceptance Criteria

**SDK**: `azure-ai-contentsafety`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: ContentSafetyClient and BlocklistClient
```python
from azure.ai.contentsafety import ContentSafetyClient, BlocklistClient
```

#### ✅ CORRECT: Credentials
```python
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
```

### 1.2 Model Imports

#### ✅ CORRECT: Text analysis models
```python
from azure.ai.contentsafety.models import AnalyzeTextOptions, TextCategory, AnalyzeTextOutputType
```

#### ✅ CORRECT: Image analysis models
```python
from azure.ai.contentsafety.models import AnalyzeImageOptions, ImageData, ImageCategory
```

#### ✅ CORRECT: Blocklist models
```python
from azure.ai.contentsafety.models import (
    TextBlocklist,
    TextBlocklistItem,
    AddOrUpdateTextBlocklistItemsOptions,
    RemoveTextBlocklistItemsOptions,
)
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Importing clients from models
```python
# WRONG - clients are in azure.ai.contentsafety, not models
from azure.ai.contentsafety.models import ContentSafetyClient
from azure.ai.contentsafety.models import BlocklistClient
```

#### ❌ INCORRECT: Wrong credential import path
```python
# WRONG - AzureKeyCredential is in azure.core.credentials
from azure.ai.contentsafety import AzureKeyCredential
```

---

## 2. Authentication Patterns

### 2.1 ✅ CORRECT: API Key Authentication
```python
import os
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential

client = ContentSafetyClient(
    endpoint=os.environ["CONTENT_SAFETY_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["CONTENT_SAFETY_KEY"]),
)
```

### 2.2 ✅ CORRECT: Microsoft Entra ID Authentication
```python
import os
from azure.ai.contentsafety import ContentSafetyClient
from azure.identity import DefaultAzureCredential

client = ContentSafetyClient(
    endpoint=os.environ["CONTENT_SAFETY_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoding secrets or endpoint
```python
# WRONG - hardcoded secrets and endpoint
client = ContentSafetyClient(
    endpoint="https://example.cognitiveservices.azure.com",
    credential=AzureKeyCredential("my-secret-key"),
)
```

#### ❌ INCORRECT: Passing key directly as credential
```python
# WRONG - credential must be AzureKeyCredential
client = ContentSafetyClient(
    endpoint=os.environ["CONTENT_SAFETY_ENDPOINT"],
    credential=os.environ["CONTENT_SAFETY_KEY"],
)
```

---

## 3. Text Analysis Patterns

### 3.1 ✅ CORRECT: Analyze Text with Categories
```python
from azure.ai.contentsafety.models import AnalyzeTextOptions, TextCategory

request = AnalyzeTextOptions(text="Your text content to analyze")
response = client.analyze_text(request)

for category in [
    TextCategory.HATE,
    TextCategory.SELF_HARM,
    TextCategory.SEXUAL,
    TextCategory.VIOLENCE,
]:
    result = next(
        (item for item in response.categories_analysis if item.category == category),
        None,
    )
    if result:
        print(f"{category}: severity {result.severity}")
```

### 3.2 ❌ INCORRECT: Using image models for text
```python
# WRONG - ImageCategory is for image analysis
from azure.ai.contentsafety.models import AnalyzeTextOptions, ImageCategory

request = AnalyzeTextOptions(text="text")
response = client.analyze_text(request)
if any(item.category == ImageCategory.HATE for item in response.categories_analysis):
    print("Wrong category enum")
```

---

## 4. Image Analysis Patterns

### 4.1 ✅ CORRECT: Analyze Image from File Bytes
```python
from azure.ai.contentsafety.models import AnalyzeImageOptions, ImageData

with open("image.jpg", "rb") as file:
    request = AnalyzeImageOptions(image=ImageData(content=file.read()))

response = client.analyze_image(request)
```

### 4.2 ✅ CORRECT: Analyze Image from Blob URL
```python
from azure.ai.contentsafety.models import AnalyzeImageOptions, ImageData

request = AnalyzeImageOptions(
    image=ImageData(blob_url="https://example.com/image.jpg")
)
response = client.analyze_image(request)
```

### 4.3 ❌ INCORRECT: Using text models for image
```python
# WRONG - AnalyzeTextOptions is for text analysis only
from azure.ai.contentsafety.models import AnalyzeTextOptions

request = AnalyzeTextOptions(text="image.jpg")
response = client.analyze_image(request)
```

### 4.4 ❌ INCORRECT: Wrong ImageData field
```python
# WRONG - ImageData uses blob_url, not url
request = AnalyzeImageOptions(
    image=ImageData(url="https://example.com/image.jpg")
)
```

---

## 5. Blocklist Management Patterns

### 5.1 ✅ CORRECT: Create or Update Blocklist
```python
from azure.ai.contentsafety import BlocklistClient
from azure.ai.contentsafety.models import TextBlocklist

blocklist_client = BlocklistClient(endpoint, credential)

blocklist = TextBlocklist(
    blocklist_name="my-blocklist",
    description="Custom terms to block",
)

blocklist_client.create_or_update_text_blocklist(
    blocklist_name="my-blocklist",
    options=blocklist,
)
```

### 5.2 ✅ CORRECT: Add Items to Blocklist
```python
from azure.ai.contentsafety.models import AddOrUpdateTextBlocklistItemsOptions, TextBlocklistItem

items = AddOrUpdateTextBlocklistItemsOptions(
    blocklist_items=[
        TextBlocklistItem(text="blocked-term-1"),
        TextBlocklistItem(text="blocked-term-2"),
    ]
)

blocklist_client.add_or_update_blocklist_items(
    blocklist_name="my-blocklist",
    options=items,
)
```

### 5.3 ✅ CORRECT: Analyze Text with Blocklist
```python
from azure.ai.contentsafety.models import AnalyzeTextOptions

request = AnalyzeTextOptions(
    text="Text containing blocked-term-1",
    blocklist_names=["my-blocklist"],
    halt_on_blocklist_hit=True,
)

response = client.analyze_text(request)
if response.blocklists_match:
    for match in response.blocklists_match:
        print(f"Blocked: {match.blocklist_item_text}")
```

### 5.4 ✅ CORRECT: Remove Blocklist Items
```python
from azure.ai.contentsafety.models import RemoveTextBlocklistItemsOptions

blocklist_client.remove_blocklist_items(
    blocklist_name="my-blocklist",
    options=RemoveTextBlocklistItemsOptions(blocklist_item_ids=["item-id"]),
)
```

### 5.5 ❌ INCORRECT: Using ContentSafetyClient for blocklist operations
```python
# WRONG - blocklist operations are on BlocklistClient
client = ContentSafetyClient(endpoint, credential)
client.create_or_update_text_blocklist(...)
```

---

## 6. Multi-Severity Classification Patterns

### 6.1 ✅ CORRECT: Eight severity levels for text
```python
from azure.ai.contentsafety.models import AnalyzeTextOptions, AnalyzeTextOutputType

request = AnalyzeTextOptions(
    text="Your text",
    output_type=AnalyzeTextOutputType.EIGHT_SEVERITY_LEVELS,
)
response = client.analyze_text(request)
```

### 6.2 ❌ INCORRECT: Using string output type
```python
# WRONG - output_type must be AnalyzeTextOutputType enum
request = AnalyzeTextOptions(
    text="Your text",
    output_type="EightSeverityLevels",
)
```
