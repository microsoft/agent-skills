# Azure AI Text Translation SDK Acceptance Criteria

**SDK**: `azure-ai-translation-text`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Sync Client with API Key and Region
```python
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential
```

#### ✅ CORRECT: Sync Client with API Key and Endpoint
```python
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential
```

#### ✅ CORRECT: Sync Client with Entra ID (Recommended)
```python
from azure.ai.translation.text import TextTranslationClient
from azure.identity import DefaultAzureCredential
```

#### ✅ CORRECT: Async Client
```python
from azure.ai.translation.text.aio import TextTranslationClient
from azure.identity.aio import DefaultAzureCredential
```

### 1.2 Model Imports

#### ✅ CORRECT: DictionaryExample Models
```python
from azure.ai.translation.text.models import DictionaryExampleTextItem
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong credential type
```python
# WRONG - using wrong credential class
from azure.identity import ServicePrincipalCredential

client = TextTranslationClient(credential=ServicePrincipalCredential(...))
```

#### ❌ INCORRECT: Missing region or endpoint
```python
# WRONG - no region specified with AzureKeyCredential
credential = AzureKeyCredential(key)
client = TextTranslationClient(credential=credential)
```

#### ❌ INCORRECT: Mixing sync and async
```python
# WRONG - using sync client from async code
from azure.ai.translation.text import TextTranslationClient
from azure.identity.aio import DefaultAzureCredential

async def translate():
    client = TextTranslationClient(...)  # Should use .aio
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: With API Key and Region
```python
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential
import os

key = os.environ["AZURE_TRANSLATOR_KEY"]
region = os.environ["AZURE_TRANSLATOR_REGION"]

client = TextTranslationClient(credential=AzureKeyCredential(key), region=region)
```

### 2.2 ✅ CORRECT: With API Key and Endpoint
```python
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential
import os

endpoint = os.environ["AZURE_TRANSLATOR_ENDPOINT"]
key = os.environ["AZURE_TRANSLATOR_KEY"]

client = TextTranslationClient(endpoint=endpoint, credential=AzureKeyCredential(key))
```

### 2.3 ✅ CORRECT: With Entra ID (Recommended)
```python
from azure.ai.translation.text import TextTranslationClient
from azure.identity import DefaultAzureCredential
import os

endpoint = os.environ["AZURE_TRANSLATOR_ENDPOINT"]
credential = DefaultAzureCredential()

client = TextTranslationClient(endpoint=endpoint, credential=credential)
```

### 2.4 ✅ CORRECT: Async Client
```python
from azure.ai.translation.text.aio import TextTranslationClient
from azure.identity.aio import DefaultAzureCredential
import os

async with TextTranslationClient(
    endpoint=os.environ["AZURE_TRANSLATOR_ENDPOINT"],
    credential=DefaultAzureCredential(),
) as client:
    result = await client.translate(body=["Hello"], to=["es"])
```

### 2.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong parameter names
```python
# WRONG - using 'url' instead of 'endpoint'
client = TextTranslationClient(url=endpoint, credential=credential)

# WRONG - using 'key' instead of credential object
client = TextTranslationClient(key=key, region=region)
```

#### ❌ INCORRECT: Hardcoded credentials
```python
# WRONG - credentials hardcoded
client = TextTranslationClient(
    credential=AzureKeyCredential("abc123..."),
    region="eastus"
)
```

#### ❌ INCORRECT: Missing context manager for async
```python
# WRONG - not using context manager
client = TextTranslationClient(endpoint=endpoint, credential=credential)
result = await client.translate(body=["Hello"], to=["es"])
# Missing cleanup
```

---

## 3. Text Translation Patterns

### 3.1 ✅ CORRECT: Single Language Translation
```python
result = client.translate(
    body=["Hello, world!"],
    to=["es"]  # Spanish
)

for item in result:
    for translation in item.translations:
        print(f"Translated: {translation.text}")
```

### 3.2 ✅ CORRECT: Multiple Language Translation
```python
result = client.translate(
    body=["Hello, world!"],
    to=["es", "fr", "de"]  # Spanish, French, German
)

for item in result:
    for translation in item.translations:
        print(f"{translation.to}: {translation.text}")
```

### 3.3 ✅ CORRECT: With Source Language Specified
```python
result = client.translate(
    body=["Bonjour le monde"],
    from_parameter="fr",  # Note: 'from_parameter' not 'from'
    to=["en", "es"]
)
```

### 3.4 ✅ CORRECT: Batch Translation
```python
# Up to 100 texts per request
texts = ["Hello", "Good morning", "How are you?"]

result = client.translate(
    body=texts,
    to=["es"]
)

for item in result:
    print(item.translations[0].text)
```

### 3.5 ✅ CORRECT: With Translation Options
```python
result = client.translate(
    body=["<p>Hello, world!</p>"],
    to=["es"],
    text_type="html",                # "plain" or "html"
    profanity_action="Marked",       # "NoAction", "Deleted", "Marked"
    profanity_marker="Asterisk",     # "Asterisk", "Tag"
    include_alignment=True,
    include_sentence_length=True
)
```

### 3.6 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong parameter name for source language
```python
# WRONG - 'from' is a Python keyword
result = client.translate(body=["Hello"], to=["es"], from="en")
```

**Fix:** Use `from_parameter` instead of `from`, since `from` is a reserved Python keyword. This parameter specifies the source language code.

```python
result = client.translate(body=["Hello"], to=["es"], from_parameter="en")
```

#### ❌ INCORRECT: String instead of list for to parameter
```python
# WRONG - 'to' must be a list
result = client.translate(body=["Hello"], to="es")
```

**Fix:** The `to` parameter must always be a list of target language codes, even if translating to a single language. This allows the SDK to handle batch translations to multiple languages in a single request.

```python
result = client.translate(body=["Hello"], to=["es"])
```

#### ❌ INCORRECT: Not accessing translations correctly
```python
# WRONG - accessing text directly
for item in result:
    print(item.text)  # This won't work
```

**Fix:** Each item in the result is a translation item that contains a list of `translations` objects. You must iterate through the `translations` list to access the translated text. Each translation object has `to`, `text`, and other fields.

```python
for item in result:
    for translation in item.translations:
        print(translation.text)
```

---

## 4. Language Detection Patterns

### 4.1 ✅ CORRECT: Basic Language Detection
```python
result = client.translate(
    body=["Hola, como estas?"],
    to=["en"]
)

for item in result:
    if item.detected_language:
        print(f"Detected: {item.detected_language.language}")
        print(f"Confidence: {item.detected_language.score:.2f}")
```

### 4.2 ✅ CORRECT: Using Detect Method
```python
result = client.detect(body=["Bonjour"])

for item in result:
    print(f"Language: {item.language}")
    print(f"Confidence: {item.score}")
```

### 4.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not checking for None
```python
# WRONG - detected_language might be None
language = result[0].detected_language.language
```

**Fix:** The `detected_language` field can be `None` if the API cannot confidently detect the language. Always check before accessing its properties. This prevents `AttributeError` when the language is undetected.

```python
if result[0].detected_language:
    language = result[0].detected_language.language
```

---

## 5. Transliteration Patterns

### 5.1 ✅ CORRECT: Basic Transliteration
```python
result = client.transliterate(
    body=["konnichiwa"],
    language="ja",
    from_script="Latn",  # Latin script
    to_script="Jpan"     # Japanese script
)

for item in result:
    print(f"Transliterated: {item.text}")
    print(f"Script: {item.script}")
```

### 5.2 ✅ CORRECT: Language Code with Script Conversion
```python
result = client.transliterate(
    body=["Привет"],
    language="ru",
    from_script="Cyrl",  # Cyrillic
    to_script="Latn"     # Latin
)
```

### 5.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Invalid script codes
```python
# WRONG - script codes don't exist
result = client.transliterate(
    body=["hello"],
    language="en",
    from_script="Latin",   # Should be "Latn"
    to_script="Arabic"     # Should be "Arab"
)
```

---

## 6. Dictionary Lookup Patterns

### 6.1 ✅ CORRECT: Basic Dictionary Lookup
```python
result = client.lookup_dictionary_entries(
    body=["fly"],
    from_parameter="en",
    to="es"
)

for item in result:
    print(f"Source: {item.normalized_source}")
    for translation in item.translations:
        print(f"  {translation.normalized_target}")
        print(f"  Part of speech: {translation.pos_tag}")
        print(f"  Confidence: {translation.confidence}")
```

### 6.2 ✅ CORRECT: Dictionary Examples
```python
from azure.ai.translation.text.models import DictionaryExampleTextItem

result = client.lookup_dictionary_examples(
    body=[DictionaryExampleTextItem(text="fly", translation="volar")],
    from_parameter="en",
    to="es"
)

for item in result:
    for example in item.examples:
        print(f"Source: {example.source_prefix}{example.source_term}{example.source_suffix}")
        print(f"Target: {example.target_prefix}{example.target_term}{example.target_suffix}")
```

### 6.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong model for examples
```python
# WRONG - using strings instead of DictionaryExampleTextItem
result = client.lookup_dictionary_examples(
    body=[{"text": "fly", "translation": "volar"}],
    from_parameter="en",
    to="es"
)
```

**Fix:** The `lookup_dictionary_examples` method requires the `body` parameter to be a list of `DictionaryExampleTextItem` objects, not dictionaries or strings. This ensures proper serialization and API compatibility.

```python
from azure.ai.translation.text.models import DictionaryExampleTextItem

result = client.lookup_dictionary_examples(
    body=[DictionaryExampleTextItem(text="fly", translation="volar")],
    from_parameter="en",
    to="es"
)
```

---

## 7. Sentence Breaking Patterns

### 7.1 ✅ CORRECT: Find Sentence Boundaries
```python
result = client.find_sentence_boundaries(
    body=["Hello! How are you? I hope you are well."],
    language="en"
)

for item in result:
    print(f"Sentence lengths: {item.sent_len}")
```

### 7.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing language parameter
```python
# WRONG - language is required
result = client.find_sentence_boundaries(
    body=["Hello! How are you?"]
)
```

---

## 8. Supported Languages Patterns

### 8.1 ✅ CORRECT: Get All Supported Languages
```python
languages = client.get_supported_languages()

# Translation languages
for code, lang in languages.translation.items():
    print(f"{code}: {lang.name} ({lang.native_name})")

# Transliteration languages
for code, lang in languages.transliteration.items():
    print(f"{code}: {lang.name}")

# Dictionary languages
for code, lang in languages.dictionary.items():
    print(f"{code}: {lang.name}")
```

### 8.2 ✅ CORRECT: Caching Languages
```python
# Cache languages to avoid repeated API calls
supported_languages = client.get_supported_languages()

def get_translation_languages():
    return supported_languages.translation

def is_supported(lang_code):
    return lang_code in supported_languages.translation
```

---

## 9. Async Patterns

### 9.1 ✅ CORRECT: Full Async Example
```python
import asyncio
from azure.ai.translation.text.aio import TextTranslationClient
from azure.identity.aio import DefaultAzureCredential
import os

async def main():
    async with TextTranslationClient(
        endpoint=os.environ["AZURE_TRANSLATOR_ENDPOINT"],
        credential=DefaultAzureCredential(),
    ) as client:
        result = await client.translate(
            body=["Hello, world!"],
            to=["es", "fr"]
        )
        
        for item in result:
            for translation in item.translations:
                print(f"{translation.to}: {translation.text}")

asyncio.run(main())
```

### 9.2 ✅ CORRECT: Batch Processing with Async
```python
async def translate_batch(texts, target_lang):
    async with TextTranslationClient(
        endpoint=os.environ["AZURE_TRANSLATOR_ENDPOINT"],
        credential=DefaultAzureCredential(),
    ) as client:
        result = await client.translate(
            body=texts,
            to=[target_lang]
        )
        
        translations = []
        for item in result:
            translations.append(item.translations[0].text)
        return translations
```

### 9.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing await
```python
# WRONG - missing await
async def bad_translate():
    result = client.translate(body=["Hello"], to=["es"])  # Missing await
    return result[0].translations[0].text
```

#### ❌ INCORRECT: Wrong credential type
```python
# WRONG - using sync credential with async client
from azure.ai.translation.text.aio import TextTranslationClient
from azure.identity import DefaultAzureCredential  # Should be from .aio

async with TextTranslationClient(credential=DefaultAzureCredential()):
    ...
```

---

## 10. Best Practices Checklist

### Correct Patterns
- [ ] Use `DefaultAzureCredential` for authentication (Entra ID)
- [ ] Use `AzureKeyCredential` with region for API key auth
- [ ] Batch up to 100 texts in single request
- [ ] Check `detected_language` before accessing
- [ ] Use `from_parameter` not `from` for source language
- [ ] Use list for `to` parameter (e.g., `to=["es", "fr"]`)
- [ ] Use async client for high-throughput scenarios
- [ ] Cache `get_supported_languages()` response
- [ ] Specify `text_type="html"` when translating HTML
- [ ] Import `DictionaryExampleTextItem` for examples

### Anti-Patterns to Avoid
- [ ] Hardcoded credentials
- [ ] String instead of list for `to` parameter
- [ ] Using Python keyword `from` (use `from_parameter`)
- [ ] Not checking `detected_language` for None
- [ ] Sync credential with async client
- [ ] Invalid script codes for transliteration
- [ ] Missing `language` parameter for sentence breaking
- [ ] Accessing translations without iterating
- [ ] Not using context managers for resources

---

## 11. Environment Variables

### Required
```bash
AZURE_TRANSLATOR_KEY=<your-api-key>
AZURE_TRANSLATOR_REGION=<region>  # e.g., eastus, westus2
# OR
AZURE_TRANSLATOR_ENDPOINT=https://<resource>.cognitiveservices.azure.com
```

### Optional
```bash
AZURE_TRANSLATOR_CUSTOM_ENDPOINT=  # For private endpoints
```

---

## 12. Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `TypeError: 'to' must be a list` | Using string for target languages | Use `to=["es", "fr"]` not `to="es"` |
| `NameError: name 'from' is not defined` | Using Python keyword | Use `from_parameter="en"` not `from="en"` |
| `AttributeError: 'NoneType' object has no attribute 'language'` | Not checking detected_language | Add `if item.detected_language:` check |
| `AuthenticationError` | Wrong credentials or region | Verify KEY and REGION env vars |
| `ValueError: Invalid script code` | Wrong transliteration script | Use correct 4-letter codes (e.g., "Latn", "Cyrl") |
| `TypeError: expected str, got dict` | Wrong model type for examples | Use `DictionaryExampleTextItem` not dict |
| `NotImplementedError: await without async context` | Using sync client in async code | Import from `.aio` module |

---

## 13. Test Scenarios Checklist

### Basic Operations
- [ ] Client creation with API key + region
- [ ] Client creation with endpoint + key
- [ ] Client creation with Entra ID
- [ ] Async client creation
- [ ] Basic single language translation
- [ ] Multiple language translation
- [ ] Batch translation (up to 100 texts)
- [ ] Language detection via translate
- [ ] Language detection via detect method
- [ ] Get supported languages

### Advanced Features
- [ ] Translation with source language specified
- [ ] Translation with text_type="html"
- [ ] Translation with profanity handling
- [ ] Translation with alignment and sentence length
- [ ] Transliteration between scripts
- [ ] Dictionary lookup with part of speech
- [ ] Dictionary examples lookup
- [ ] Sentence boundary detection
- [ ] Caching supported languages

### Async
- [ ] Async translate operation
- [ ] Async batch processing
- [ ] Proper await usage
- [ ] Async context manager

### Error Handling
- [ ] Check detected_language for None
- [ ] Validate language codes exist
- [ ] Handle authentication errors
- [ ] Handle invalid parameters
