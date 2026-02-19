# Azure AI Content Understanding SDK Acceptance Criteria

**SDK**: `azure-ai-contentunderstanding`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Commit**: `azure-ai-contentunderstanding_1.0.0b1`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Sync Client
```python
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.identity import DefaultAzureCredential
```

#### ✅ CORRECT: Async Client
```python
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.identity.aio import DefaultAzureCredential
```

### 1.2 Model Imports

#### ✅ CORRECT: Analyze Models
```python
from azure.ai.contentunderstanding.models import AnalyzeInput, AnalyzeResult
from azure.ai.contentunderstanding.models import MediaContentKind, DocumentContent, AudioVisualContent
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong import modules
```python
# WRONG - client is not in models
from azure.ai.contentunderstanding.models import ContentUnderstandingClient

# WRONG - async credential for sync client
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.identity.aio import DefaultAzureCredential

# WRONG - sync credential for async client
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.identity import DefaultAzureCredential
```

---

## 2. Authentication

### 2.1 ✅ CORRECT: DefaultAzureCredential (Sync)
```python
import os
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
credential = DefaultAzureCredential()
client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)
```

### 2.2 ✅ CORRECT: DefaultAzureCredential (Async)
```python
import os
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.identity.aio import DefaultAzureCredential

endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
credential = DefaultAzureCredential()

async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
    ...
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials or missing credential
```python
# WRONG - hardcoded endpoint
client = ContentUnderstandingClient(endpoint="https://example.com", credential=DefaultAzureCredential())

# WRONG - hardcoded key string
from azure.core.credentials import AzureKeyCredential
client = ContentUnderstandingClient(endpoint=endpoint, credential=AzureKeyCredential("my-key"))

# WRONG - missing credential
client = ContentUnderstandingClient(endpoint=endpoint)
```

---

## 3. Document Extraction

### 3.1 ✅ CORRECT: prebuilt-documentSearch from URL
```python
from azure.ai.contentunderstanding.models import AnalyzeInput

poller = client.begin_analyze(
    analyzer_id="prebuilt-documentSearch",
    inputs=[AnalyzeInput(url="https://example.com/document.pdf")]
)
result = poller.result()

content = result.contents[0]
print(content.markdown)
```

### 3.2 ✅ CORRECT: Access document content details
```python
from azure.ai.contentunderstanding.models import MediaContentKind, DocumentContent

content = result.contents[0]
if content.kind == MediaContentKind.DOCUMENT:
    document_content: DocumentContent = content  # type: ignore
    print(document_content.start_page_number)
```

### 3.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong analyze method or request shape
```python
# WRONG - begin_analyze_document does not match SDK examples
poller = client.begin_analyze_document(
    analyzer_id="prebuilt-documentSearch",
    analyze_request={"url": "https://example.com/document.pdf"}
)

# WRONG - missing inputs list
poller = client.begin_analyze(
    analyzer_id="prebuilt-documentSearch",
    url="https://example.com/document.pdf"
)
```

---

## 4. Image Extraction

### 4.1 ✅ CORRECT: prebuilt-imageSearch from URL
```python
from azure.ai.contentunderstanding.models import AnalyzeInput

poller = client.begin_analyze(
    analyzer_id="prebuilt-imageSearch",
    inputs=[AnalyzeInput(url="https://example.com/image.jpg")]
)
result = poller.result()
content = result.contents[0]
print(content.markdown)
```

### 4.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Invalid analyzer ID
```python
poller = client.begin_analyze(
    analyzer_id="prebuilt-image-search",
    inputs=[AnalyzeInput(url="https://example.com/image.jpg")]
)
```

---

## 5. Audio Transcription

### 5.1 ✅ CORRECT: prebuilt-audioSearch transcript phrases
```python
from azure.ai.contentunderstanding.models import AnalyzeInput

poller = client.begin_analyze(
    analyzer_id="prebuilt-audioSearch",
    inputs=[AnalyzeInput(url="https://example.com/audio.mp3")]
)
result = poller.result()

content = result.contents[0]
for phrase in content.transcript_phrases:
    print(f"[{phrase.start_time}] {phrase.text}")
```

### 5.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Invalid analyzer ID
```python
poller = client.begin_analyze(
    analyzer_id="prebuilt-audio-search",
    inputs=[AnalyzeInput(url="https://example.com/audio.mp3")]
)
```

---

## 6. Video Analysis

### 6.1 ✅ CORRECT: prebuilt-videoSearch with transcript and key frames
```python
from azure.ai.contentunderstanding.models import AnalyzeInput

poller = client.begin_analyze(
    analyzer_id="prebuilt-videoSearch",
    inputs=[AnalyzeInput(url="https://example.com/video.mp4")]
)
result = poller.result()

content = result.contents[0]
for phrase in content.transcript_phrases:
    print(phrase.text)
for frame in content.key_frames:
    print(frame.description)
```

### 6.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Skipping poller.result
```python
poller = client.begin_analyze(
    analyzer_id="prebuilt-videoSearch",
    inputs=[AnalyzeInput(url="https://example.com/video.mp4")]
)

# WRONG - must call .result() to retrieve analysis output
content = poller.contents[0]
```
