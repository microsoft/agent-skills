# Azure AI Document Translation SDK Acceptance Criteria

**SDK**: `azure-ai-translation-document`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Sync Client
```python
from azure.ai.translation.document import DocumentTranslationClient
from azure.core.credentials import AzureKeyCredential
# OR
from azure.identity import DefaultAzureCredential
```

#### ✅ CORRECT: Async Client
```python
from azure.ai.translation.document.aio import DocumentTranslationClient
from azure.identity.aio import DefaultAzureCredential
```

#### ✅ CORRECT: Single Document Client
```python
from azure.ai.translation.document import SingleDocumentTranslationClient
from azure.core.credentials import AzureKeyCredential
```

### 1.2 Model Imports

#### ✅ CORRECT: Input/Output Models
```python
from azure.ai.translation.document import (
    DocumentTranslationInput,
    TranslationTarget,
)
```

#### ✅ CORRECT: Glossary Models
```python
from azure.ai.translation.document import TranslationGlossary
```

#### ✅ CORRECT: File Purpose Enum
```python
from azure.ai.translation.document import FilePurpose
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong import paths
```python
# WRONG - DocumentTranslationInput is not directly in azure.ai.translation
from azure.ai.translation import DocumentTranslationInput

# WRONG - Trying to import non-existent TranslationDocument
from azure.ai.translation.document import TranslationDocument
```

#### ❌ INCORRECT: Mixing sync and async imports
```python
# WRONG - using sync client with async context manager
from azure.ai.translation.document import DocumentTranslationClient
async with DocumentTranslationClient(...) as client:
    ...
```

**The fix:** Use the async client from `azure.ai.translation.document.aio` when using async context managers. Import `DocumentTranslationClient` from `.aio` instead of the base module, then use `async with` for proper async context management.

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Sync Client with Entra ID (Recommended)
```python
import os
from azure.ai.translation.document import DocumentTranslationClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
client = DocumentTranslationClient(endpoint, DefaultAzureCredential())

# Use with context manager for cleanup
with client:
    # Use client
    pass
```

### 2.2 ✅ CORRECT: Sync Client with API Key
```python
import os
from azure.ai.translation.document import DocumentTranslationClient
from azure.core.credentials import AzureKeyCredential

endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]

client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))
```

### 2.3 ✅ CORRECT: Async Client
```python
import os
from azure.ai.translation.document.aio import DocumentTranslationClient
from azure.identity.aio import DefaultAzureCredential

endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
client = DocumentTranslationClient(endpoint, DefaultAzureCredential())

async with client:
    # Use client
    pass
```

### 2.4 ✅ CORRECT: Single Document Client
```python
from azure.ai.translation.document import SingleDocumentTranslationClient
from azure.core.credentials import AzureKeyCredential

single_client = SingleDocumentTranslationClient(endpoint, AzureKeyCredential(key))
```

### 2.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials
```python
# WRONG - Never hardcode credentials
client = DocumentTranslationClient("https://example.cognitiveservices.azure.com", AzureKeyCredential("key123"))
```

#### ❌ INCORRECT: Wrong parameter names
```python
# WRONG - should be 'endpoint' not 'url'
client = DocumentTranslationClient(url=endpoint, credential=cred)
```

#### ❌ INCORRECT: Not using context manager
```python
# WRONG - should close client explicitly or use context manager
client = DocumentTranslationClient(endpoint, credential)
poller = client.begin_translation(...)
# Missing: client.close() or proper cleanup
```

---

## 3. Batch Document Translation Patterns

### 3.1 ✅ CORRECT: Basic Batch Translation
```python
from azure.ai.translation.document import (
    DocumentTranslationInput,
    TranslationTarget,
)

source_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
target_url = os.environ["AZURE_TARGET_CONTAINER_URL"]

poller = client.begin_translation(
    inputs=[
        DocumentTranslationInput(
            source_url=source_url,
            targets=[
                TranslationTarget(
                    target_url=target_url,
                    language="es"
                )
            ]
        )
    ]
)

# Wait for completion
result = poller.result()
```

### 3.2 ✅ CORRECT: Multiple Target Languages
```python
poller = client.begin_translation(
    inputs=[
        DocumentTranslationInput(
            source_url=source_url,
            targets=[
                TranslationTarget(target_url=target_url_es, language="es"),
                TranslationTarget(target_url=target_url_fr, language="fr"),
                TranslationTarget(target_url=target_url_de, language="de"),
            ]
        )
    ]
)
```

### 3.3 ✅ CORRECT: Batch with Glossary
```python
from azure.ai.translation.document import TranslationGlossary

poller = client.begin_translation(
    inputs=[
        DocumentTranslationInput(
            source_url=source_url,
            targets=[
                TranslationTarget(
                    target_url=target_url,
                    language="es",
                    glossaries=[
                        TranslationGlossary(
                            glossary_url="https://<storage>.blob.core.windows.net/glossary/terms.csv",
                            file_format="csv"
                        )
                    ]
                )
            ]
        )
    ]
)
```

### 3.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Inline blob URLs without SAS
```python
# WRONG - blob URLs need SAS tokens for security
poller = client.begin_translation(
    inputs=[
        DocumentTranslationInput(
            source_url="https://storage.blob.core.windows.net/container/",  # Missing SAS
            targets=[...]
        )
    ]
)
```

#### ❌ INCORRECT: Wrong parameter names
```python
# WRONG - should use 'inputs' not 'documents'
poller = client.begin_translation(
    documents=[DocumentTranslationInput(...)]  # Wrong
)
```

---

## 4. Single Document Translation

### 4.1 ✅ CORRECT: Translate Single Document
```python
from azure.ai.translation.document import SingleDocumentTranslationClient

single_client = SingleDocumentTranslationClient(endpoint, AzureKeyCredential(key))

with open("document.docx", "rb") as f:
    document_content = f.read()

result = single_client.translate(
    body=document_content,
    target_language="es",
    content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)

# Save result
with open("document_es.docx", "wb") as f:
    f.write(result)
```

### 4.2 ✅ CORRECT: Single Document with Glossary
```python
result = single_client.translate(
    body=document_content,
    target_language="es",
    content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    glossary_url="https://<storage>.blob.core.windows.net/glossary/terms.csv"
)
```

### 4.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using batch client for single document
```python
# WRONG - use SingleDocumentTranslationClient instead
client = DocumentTranslationClient(...)
result = client.translate(...)  # DocumentTranslationClient doesn't have translate method
```

---

## 5. Status Polling & Monitoring

### 5.1 ✅ CORRECT: Check Translation Status
```python
# After begin_translation, check status
poller = client.begin_translation(inputs=[...])

# Check overall status
print(f"Status: {poller.status()}")
print(f"Succeeded: {poller.details.documents_succeeded_count}")
print(f"Failed: {poller.details.documents_failed_count}")

# Wait for completion
result = poller.result()
```

### 5.2 ✅ CORRECT: List Translation Operations
```python
operations = client.list_translation_statuses()

for op in operations:
    print(f"Operation ID: {op.id}")
    print(f"Status: {op.status}")
    print(f"Total documents: {op.documents_total_count}")
    print(f"Succeeded: {op.documents_succeeded_count}")
    print(f"Failed: {op.documents_failed_count}")
```

### 5.3 ✅ CORRECT: List Document Statuses in Job
```python
operation_id = poller.id
document_statuses = client.list_document_statuses(operation_id)

for doc in document_statuses:
    print(f"Document: {doc.source_document_url}")
    print(f"Status: {doc.status}")
    print(f"Translated to: {doc.translated_to}")
    if doc.error:
        print(f"Error: {doc.error.message}")
```

### 5.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not checking for errors
```python
# WRONG - not handling failed documents
operations = client.list_translation_statuses()
for op in operations:
    # Not checking if documents_failed_count > 0
    pass
```

#### ❌ INCORRECT: Wrong status enum values
```python
# WRONG - status strings vary, should check actual enum
if op.status == "completed":  # May not match actual status string
    pass
```

---

## 6. Async Patterns

### 6.1 ✅ CORRECT: Async Batch Translation
```python
import asyncio
from azure.ai.translation.document.aio import DocumentTranslationClient
from azure.identity.aio import DefaultAzureCredential

async def translate_documents():
    async with DocumentTranslationClient(
        endpoint=os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"],
        credential=DefaultAzureCredential()
    ) as client:
        poller = await client.begin_translation(
            inputs=[
                DocumentTranslationInput(
                    source_url=source_url,
                    targets=[TranslationTarget(target_url=target_url, language="es")]
                )
            ]
        )
        
        result = await poller.result()
        return result

asyncio.run(translate_documents())
```

### 6.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Sync client in async function
```python
# WRONG - using sync client in async context
async def bad_example():
    from azure.ai.translation.document import DocumentTranslationClient
    async with DocumentTranslationClient(...) as client:  # Won't work, not async
        ...
```

**The fix:** Import the async variant from `azure.ai.translation.document.aio` instead. The sync `DocumentTranslationClient` is not compatible with async context managers (`async with`). Always use the `.aio` module when working in async functions.

#### ❌ INCORRECT: Missing await
```python
# WRONG - missing await for async operations
async def bad():
    poller = client.begin_translation(...)  # Missing await
    result = poller.result()  # Missing await
```

---

## 7. Format Preservation & Supported Formats

### 7.1 ✅ CORRECT: Get Supported Document Formats
```python
formats = client.get_supported_document_formats()

for fmt in formats:
    print(f"Format: {fmt.format}")
    print(f"Extensions: {fmt.file_extensions}")
    print(f"Content types: {fmt.content_types}")
```

### 7.2 ✅ CORRECT: Get Supported Languages
```python
languages = client.get_supported_languages()

for lang in languages:
    print(f"Language: {lang.name} ({lang.code})")
    print(f"Direction: {lang.direction}")
```

### 7.3 ✅ CORRECT: Common Content Types
```python
# For single document translation, specify content type
content_types = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
    "application/pdf": "pdf",
    "text/html": "html",
    "text/plain": "txt",
}

result = single_client.translate(
    body=document_content,
    target_language="es",
    content_type=content_types["application/pdf"]
)
```

### 7.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong file format
```python
# WRONG - passing wrong content type for file type
with open("document.docx", "rb") as f:
    result = single_client.translate(
        body=f.read(),
        target_language="es",
        content_type="application/pdf"  # Wrong! File is DOCX
    )
```

---

## 8. Error Handling & Cancellation

### 8.1 ✅ CORRECT: Check Document-Level Errors
```python
operation_id = poller.id
document_statuses = client.list_document_statuses(operation_id)

failed_docs = []
for doc in document_statuses:
    if doc.status == "failed":
        failed_docs.append({
            "url": doc.source_document_url,
            "error": doc.error.message if doc.error else "Unknown error"
        })

if failed_docs:
    print(f"Failed documents: {len(failed_docs)}")
    for doc in failed_docs:
        print(f"  - {doc['url']}: {doc['error']}")
```

### 8.2 ✅ CORRECT: Cancel Translation
```python
poller = client.begin_translation(inputs=[...])

# Cancel the operation
client.cancel_translation(poller.id)

# Verify cancellation
result = poller.result()
if result.status == "cancelled":
    print("Translation cancelled successfully")
```

### 8.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Ignoring error details
```python
# WRONG - not extracting error messages
for doc in document_statuses:
    if doc.status == "failed":
        print("Translation failed")  # No context
```

#### ❌ INCORRECT: Not validating SAS permissions
```python
# WRONG - container URLs don't have proper permissions
source_url = "https://storage.blob.core.windows.net/source/"  # Missing SAS, no Read/List perms
target_url = "https://storage.blob.core.windows.net/target/"  # Missing SAS, no Write/List perms

poller = client.begin_translation(
    inputs=[DocumentTranslationInput(source_url=source_url, targets=[...])]
)
```

---

## 9. Environment Variables

### ✅ CORRECT: Required Configuration
```bash
AZURE_DOCUMENT_TRANSLATION_ENDPOINT=https://<resource>.cognitiveservices.azure.com
AZURE_DOCUMENT_TRANSLATION_KEY=<your-api-key>

# Storage URLs with SAS tokens
AZURE_SOURCE_CONTAINER_URL=https://<storage>.blob.core.windows.net/<container>?<sas>
AZURE_TARGET_CONTAINER_URL=https://<storage>.blob.core.windows.net/<container>?<sas>
```

### ✅ CORRECT: Load from Environment
```python
import os

endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
key = os.environ.get("AZURE_DOCUMENT_TRANSLATION_KEY")
source_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
target_url = os.environ["AZURE_TARGET_CONTAINER_URL"]
```

---

## 10. Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `AuthenticationError` | Invalid credentials or endpoint | Check environment variables, use DefaultAzureCredential or valid API key |
| `NotFound` (404) | Invalid storage URL or missing SAS | Verify container URL and SAS token permissions |
| `Forbidden` (403) | Insufficient SAS permissions | Ensure SAS has Read/List for source, Write/List for target |
| `DocumentTranslationInput not found` | Wrong import path | Import from `azure.ai.translation.document` not from submodules |
| `AttributeError: 'Poller' has no attribute 'id'` | Trying to get ID before start | ID is available immediately after `begin_translation()` |
| `ValueError: target_language` | Invalid language code | Use supported language codes (check with `get_supported_languages()`) |
| `Async not awaited` | Missing await keyword | Add `await` to all async operations |

---

## 11. Test Scenarios Checklist

### Basic Operations
- [ ] Client creation with context manager (sync)
- [ ] Client creation with context manager (async)
- [ ] Single document translation
- [ ] Batch document translation
- [ ] Multiple target languages
- [ ] Status checking and polling
- [ ] Document-level error checking
- [ ] Operation cancellation

### Format & Language Support
- [ ] Get supported document formats
- [ ] Get supported languages
- [ ] Translate with specific content type
- [ ] Format preservation validation

### Advanced Features
- [ ] Glossary usage with batch translation
- [ ] Glossary usage with single document
- [ ] List all translation operations
- [ ] List document statuses in job

### Error Handling
- [ ] Handle failed documents
- [ ] Check error messages
- [ ] Validate SAS permissions before translation
- [ ] Handle network errors

### Async Patterns
- [ ] Async batch translation
- [ ] Async single document translation
- [ ] Proper await usage
- [ ] Context manager cleanup

---

## 12. Quick Reference: Storage & SAS

### SAS Token Permissions

**Source Container (Read-Only):**
- `read` (r)
- `list` (l)

**Target Container (Write):**
- `write` (w)
- `list` (l)

### Example SAS Token Generation (Azure CLI)

```bash
# Source container
az storage container generate-sas \
  --account-name myaccount \
  --name source \
  --permissions rl \
  --expiry 2025-02-28

# Target container
az storage container generate-sas \
  --account-name myaccount \
  --name target \
  --permissions wl \
  --expiry 2025-02-28
```

### Verify Container URLs

```python
# URLs should include SAS token
source_url = "https://myaccount.blob.core.windows.net/source?sv=2021-12-02&..."
target_url = "https://myaccount.blob.core.windows.net/target?sv=2021-12-02&..."

# Verify
assert "?" in source_url, "Source URL missing SAS token"
assert "?" in target_url, "Target URL missing SAS token"
```
