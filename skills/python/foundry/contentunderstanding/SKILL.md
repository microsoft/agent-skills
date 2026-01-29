---
name: azure-ai-contentunderstanding-python
description: |
  Azure AI Content Understanding SDK for Python. Use for multimodal content extraction from documents, images, audio, and video.
  Triggers: "azure-ai-contentunderstanding", "ContentUnderstandingClient", "multimodal analysis", "document extraction", "video analysis", "audio transcription".
---

# Azure AI Content Understanding SDK for Python

Multimodal AI service that extracts semantic content from documents, video, audio, and image files for RAG and automated workflows.

## Installation

```bash
pip install azure-ai-contentunderstanding
```

## Environment Variables

```bash
AZURE_CONTENTUNDERSTANDING_ENDPOINT=https://<resource>.cognitiveservices.azure.com/
```

## Authentication

```python
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.identity import DefaultAzureCredential
import os

client = ContentUnderstandingClient(
    endpoint=os.environ["AZURE_CONTENTUNDERSTANDING_ENDPOINT"],
    credential=DefaultAzureCredential()
)
```

## Core Workflow

Content Understanding operations are asynchronous long-running operations:

1. **Begin Analysis** — Start the analysis operation (returns immediately with operation location)
2. **Poll for Results** — Poll until analysis completes (SDK handles this with `.result()`)
3. **Process Results** — Extract structured results from `AnalyzeResult`

## Prebuilt Analyzers

| Analyzer | Content Type | Purpose |
|----------|--------------|---------|
| `prebuilt-documentSearch` | Documents | Extract markdown for RAG applications |
| `prebuilt-imageSearch` | Images | Extract content from images |
| `prebuilt-audioSearch` | Audio | Transcribe audio with timing |
| `prebuilt-videoSearch` | Video | Extract frames, transcripts, summaries |
| `prebuilt-invoice` | Documents | Extract invoice fields |

## Analyze Document

```python
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.identity import DefaultAzureCredential

client = ContentUnderstandingClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential()
)

# Analyze document from URL
poller = client.begin_analyze_document(
    analyzer_id="prebuilt-documentSearch",
    analyze_request={"url": "https://example.com/document.pdf"}
)

result = poller.result()

# Access markdown content
print(result.content.markdown)

# Access detailed document structure
for page in result.content.pages:
    print(f"Page {page.page_number}: {len(page.lines)} lines")
```

## Analyze from File

```python
with open("document.pdf", "rb") as f:
    poller = client.begin_analyze_document(
        analyzer_id="prebuilt-documentSearch",
        analyze_request={"file": f}
    )
    result = poller.result()
```

## Analyze Video

```python
poller = client.begin_analyze_document(
    analyzer_id="prebuilt-videoSearch",
    analyze_request={"url": "https://example.com/video.mp4"}
)

result = poller.result()

# Access video content (AudioVisualContent)
video_content = result.content

# Get transcript phrases with timing
for phrase in video_content.transcript_phrases:
    print(f"[{phrase.start_time} - {phrase.end_time}]: {phrase.text}")

# Get key frames (for video)
for frame in video_content.key_frames:
    print(f"Frame at {frame.time}: {frame.description}")
```

## Analyze Audio

```python
poller = client.begin_analyze_document(
    analyzer_id="prebuilt-audioSearch",
    analyze_request={"url": "https://example.com/audio.mp3"}
)

result = poller.result()

# Access audio transcript
for phrase in result.content.transcript_phrases:
    print(f"[{phrase.start_time}]: {phrase.text}")
```

## Custom Analyzers

Create custom analyzers with field schemas for specialized extraction:

```python
# Create custom analyzer
analyzer = client.create_analyzer(
    analyzer_id="my-invoice-analyzer",
    analyzer={
        "description": "Custom invoice analyzer",
        "base_analyzer_id": "prebuilt-documentSearch",
        "field_schema": {
            "fields": {
                "vendor_name": {"type": "string"},
                "invoice_total": {"type": "number"},
                "line_items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "amount": {"type": "number"}
                        }
                    }
                }
            }
        }
    }
)

# Use custom analyzer
poller = client.begin_analyze_document(
    analyzer_id="my-invoice-analyzer",
    analyze_request={"url": "https://example.com/invoice.pdf"}
)

result = poller.result()

# Access extracted fields
print(result.fields["vendor_name"])
print(result.fields["invoice_total"])
```

## Analyzer Management

```python
# List all analyzers
analyzers = client.list_analyzers()
for analyzer in analyzers:
    print(f"{analyzer.analyzer_id}: {analyzer.description}")

# Get specific analyzer
analyzer = client.get_analyzer("prebuilt-documentSearch")

# Delete custom analyzer
client.delete_analyzer("my-custom-analyzer")
```

## Async Client

```python
import asyncio
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.identity.aio import DefaultAzureCredential

async def analyze_document():
    async with ContentUnderstandingClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential()
    ) as client:
        poller = await client.begin_analyze_document(
            analyzer_id="prebuilt-documentSearch",
            analyze_request={"url": "https://example.com/doc.pdf"}
        )
        result = await poller.result()
        return result.content.markdown

asyncio.run(analyze_document())
```

## Content Types

| Class | For | Provides |
|-------|-----|----------|
| `DocumentContent` | PDF, images, Office docs | Pages, tables, figures, paragraphs |
| `AudioVisualContent` | Audio, video files | Transcript phrases, timing, key frames |

Both derive from `MediaContent` which provides basic info and markdown representation.

## Client Types

| Client | Purpose |
|--------|---------|
| `ContentUnderstandingClient` | Sync client for all operations |
| `ContentUnderstandingClient` (aio) | Async client for all operations |

## Best Practices

1. **Use prebuilt analyzers** for common scenarios (document/image/audio/video search)
2. **Create custom analyzers** only for domain-specific field extraction
3. **Use async client** for high-throughput scenarios
4. **Cache analyzer configurations** — they don't change frequently
5. **Handle long-running operations** — video/audio analysis can take minutes
6. **Use URL sources** when possible to avoid upload overhead
7. **Configure model deployments** before using prebuilt analyzers
