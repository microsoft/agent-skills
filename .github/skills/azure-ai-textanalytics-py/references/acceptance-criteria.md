# Azure AI Text Analytics SDK Acceptance Criteria

**SDK**: `azure-ai-textanalytics`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Sync TextAnalyticsClient
```python
from azure.ai.textanalytics import TextAnalyticsClient
from azure.identity import DefaultAzureCredential
```

#### ✅ CORRECT: Async TextAnalyticsClient
```python
from azure.ai.textanalytics.aio import TextAnalyticsClient
from azure.identity.aio import DefaultAzureCredential
```

#### ✅ CORRECT: API Key Authentication
```python
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
```

### 1.2 Model & Operation Imports

#### ✅ CORRECT: Action Classes
```python
from azure.ai.textanalytics import (
    RecognizeEntitiesAction,
    ExtractKeyPhrasesAction,
    AnalyzeSentimentAction,
    RecognizePiiEntitiesAction,
)
```

#### ✅ CORRECT: Enums
```python
from azure.ai.textanalytics import (
    PiiEntityDomain,
    PiiEntityCategory,
    TextDocumentInput,
)
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong module paths
```python
# WRONG - TextAnalyticsClient not in models
from azure.ai.textanalytics.models import TextAnalyticsClient

# WRONG - Actions not directly available
from azure.ai.textanalytics import analyze_sentiment
```

#### ❌ INCORRECT: Importing from wrong location
```python
# WRONG
from azure.ai.language import TextAnalyticsClient
from azure.ai.language.nlp import analyze_sentiment
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: With DefaultAzureCredential
```python
from azure.ai.textanalytics import TextAnalyticsClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
client = TextAnalyticsClient(endpoint, DefaultAzureCredential())
```

### 2.2 ✅ CORRECT: With Context Manager
```python
from azure.ai.textanalytics import TextAnalyticsClient
from azure.identity import DefaultAzureCredential

with TextAnalyticsClient(
    endpoint=os.environ["AZURE_LANGUAGE_ENDPOINT"],
    credential=DefaultAzureCredential()
) as client:
    result = client.analyze_sentiment(documents)
```

### 2.3 ✅ CORRECT: With API Key
```python
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

client = TextAnalyticsClient(
    endpoint=os.environ["AZURE_LANGUAGE_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["AZURE_LANGUAGE_KEY"])
)
```

### 2.4 ✅ CORRECT: Async Client
```python
from azure.ai.textanalytics.aio import TextAnalyticsClient
from azure.identity.aio import DefaultAzureCredential

async with TextAnalyticsClient(
    endpoint=os.environ["AZURE_LANGUAGE_ENDPOINT"],
    credential=DefaultAzureCredential()
) as client:
    result = await client.analyze_sentiment(documents)
```

### 2.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials
```python
# WRONG
client = TextAnalyticsClient(
    endpoint="https://my-language.cognitiveservices.azure.com",
    credential=AzureKeyCredential("hardcoded-key")
)
```

#### ❌ INCORRECT: Wrong parameter names
```python
# WRONG - should be 'endpoint', not 'url'
client = TextAnalyticsClient(
    url="https://...",
    credential=credential
)

# WRONG - should be 'credential', not 'key'
client = TextAnalyticsClient(endpoint=endpoint, key=key)
```

#### ❌ INCORRECT: Mixing sync and async
```python
# WRONG - sync credential with async client
from azure.ai.textanalytics.aio import TextAnalyticsClient
from azure.identity import DefaultAzureCredential  # Should use .aio

async with TextAnalyticsClient(endpoint=endpoint, credential=DefaultAzureCredential()):
    ...
```

---

## 3. Sentiment Analysis Patterns

### 3.1 ✅ CORRECT: Basic Sentiment Analysis
```python
documents = [
    "I had a wonderful experience at this restaurant.",
    "The service was terrible and the food was cold."
]

result = client.analyze_sentiment(documents)

for doc in result:
    if not doc.is_error:
        print(f"Overall sentiment: {doc.sentiment}")
        print(f"Scores - Positive: {doc.confidence_scores.positive:.2f}")
```

### 3.2 ✅ CORRECT: Sentiment with Opinion Mining
```python
documents = ["The hotel was beautiful but the service was poor."]

result = client.analyze_sentiment(documents, show_opinion_mining=True)

for doc in result:
    if not doc.is_error:
        print(f"Document sentiment: {doc.sentiment}")
        
        for sentence in doc.sentences:
            for opinion in sentence.mined_opinions:
                target = opinion.target
                print(f"Target: {target.text} ({target.sentiment})")
                for assessment in opinion.assessments:
                    print(f"  Assessment: {assessment.text} ({assessment.sentiment})")
```

### 3.3 ✅ CORRECT: Sentiment with Language Specification
```python
from azure.ai.textanalytics import TextDocumentInput

documents = [
    TextDocumentInput(id="1", text="Este es un texto en español", language="es"),
    TextDocumentInput(id="2", text="Ceci est un texte en français", language="fr"),
]

result = client.analyze_sentiment(documents)
```

### 3.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not handling errors
```python
# WRONG - doesn't check is_error
for doc in result:
    print(doc.sentiment)  # Crashes if doc.is_error is True
```

Always check the `is_error` attribute before accessing document results. If `is_error` is `True`, the analysis failed for that document and accessing `doc.sentiment` will raise an exception. Use an `if not doc.is_error:` guard before accessing any result attributes.

#### ❌ INCORRECT: Accessing wrong attributes
```python
# WRONG - confidence_scores not available without show_opinion_mining
result = client.analyze_sentiment(documents)  # Missing parameter
for doc in result:
    print(doc.confidence_scores)  # May be None
```

---

## 4. Entity Recognition Patterns

### 4.1 ✅ CORRECT: Named Entity Recognition
```python
documents = [
    "Microsoft was founded by Bill Gates and Paul Allen in Seattle.",
    "Apple Inc. is headquartered in Cupertino, California."
]

result = client.recognize_entities(documents)

for doc in result:
    if not doc.is_error:
        for entity in doc.entities:
            print(f"Entity: {entity.text}")
            print(f"  Category: {entity.category}")
            print(f"  Confidence: {entity.confidence_score:.2f}")
```

### 4.2 ✅ CORRECT: Linked Entities
```python
documents = ["Steve Jobs founded Apple in his garage."]

result = client.recognize_linked_entities(documents)

for doc in result:
    if not doc.is_error:
        for entity in doc.entities:
            print(f"Entity: {entity.text}")
            print(f"  Wikipedia URL: {entity.url}")
            for link in entity.matches:
                print(f"  Confidence: {link.confidence_score:.2f}")
```

### 4.3 ✅ CORRECT: PII Detection
```python
documents = [
    "My email is john@example.com and my phone is 555-123-4567.",
    "Social Security Number: 123-45-6789"
]

result = client.recognize_pii_entities(documents)

for doc in result:
    if not doc.is_error:
        print(f"Redacted: {doc.redacted_text}")
        for entity in doc.entities:
            print(f"PII: {entity.text}")
            print(f"  Category: {entity.category}")
            print(f"  Confidence: {entity.confidence_score:.2f}")
```

### 4.4 ✅ CORRECT: PII with Domain Restriction
```python
from azure.ai.textanalytics import PiiEntityDomain

documents = ["My credit card is 4532-1111-2222-3333"]

result = client.recognize_pii_entities(
    documents,
    domain=PiiEntityDomain.FINANCE  # Only detect finance-related PII
)
```

### 4.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong category names
```python
# WRONG - PiiEntityDomain has specific values
result = client.recognize_pii_entities(documents, domain="PAYMENT")
```

The `domain` parameter expects a `PiiEntityDomain` enum value, not a string. Import `PiiEntityDomain` from `azure.ai.textanalytics` and use enum values like `PiiEntityDomain.FINANCE`, `PiiEntityDomain.HEALTH`, or `PiiEntityDomain.RETAIL`.

---

## 5. Key Phrase Extraction Patterns

### 5.1 ✅ CORRECT: Extract Key Phrases
```python
documents = [
    "Azure AI Services provide powerful machine learning capabilities.",
    "The natural language processing models are state-of-the-art."
]

result = client.extract_key_phrases(documents)

for doc in result:
    if not doc.is_error:
        print(f"Key phrases: {doc.key_phrases}")
```

### 5.2 ✅ CORRECT: With Language Specification
```python
from azure.ai.textanalytics import TextDocumentInput

documents = [
    TextDocumentInput(id="1", text="El análisis de texto es muy importante", language="es"),
]

result = client.extract_key_phrases(documents)
```

### 5.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not checking errors
```python
# WRONG
for doc in result:
    for phrase in doc.key_phrases:  # Crashes if is_error
        print(phrase)
```

---

## 6. Language Detection Patterns

### 6.1 ✅ CORRECT: Detect Language
```python
documents = [
    "Hello, how are you?",
    "Bonjour, comment allez-vous?",
    "Hola, ¿cómo estás?"
]

result = client.detect_language(documents)

for doc in result:
    if not doc.is_error:
        lang = doc.primary_language
        print(f"Language: {lang.name}")
        print(f"ISO 639-1: {lang.iso6391_name}")
        print(f"Confidence: {lang.confidence_score:.2f}")
```

### 6.2 ✅ CORRECT: With Country Hint
```python
documents = ["This could be English or Spanish based on context"]

result = client.detect_language(documents, country_hint="US")
```

### 6.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong attribute names
```python
# WRONG - should be iso6391_name, not iso639_name
print(doc.primary_language.iso639_name)
```

The correct attribute name is `iso6391_name` (note: "6391", not "639"). This follows the ISO 639-1 standard for language codes. Use `doc.primary_language.iso6391_name` to get the two-letter language code like "en", "es", "fr".

---

## 7. Healthcare Text Analytics Patterns

### 7.1 ✅ CORRECT: Analyze Healthcare Entities
```python
documents = [
    "Patient has hypertension and was prescribed lisinopril 10mg daily."
]

poller = client.begin_analyze_healthcare_entities(documents)
result = poller.result()

for doc in result:
    if not doc.is_error:
        for entity in doc.entities:
            print(f"Entity: {entity.text}")
            print(f"  Category: {entity.category}")
            print(f"  Normalized: {entity.normalized_text}")
            
            if entity.data_sources:
                for source in entity.data_sources:
                    print(f"  Source: {source.name} - ID: {source.entity_id}")
```

### 7.2 ✅ CORRECT: Healthcare Relations
```python
poller = client.begin_analyze_healthcare_entities(documents)
result = poller.result()

for doc in result:
    if not doc.is_error:
        # Access relations between entities
        for relation in doc.relations:
            print(f"Relation type: {relation.relation_type}")
            print(f"  Source: {relation.target[0].text}")
            print(f"  Target: {relation.target[1].text}")
```

### 7.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not polling for completion
```python
# WRONG - begin_analyze_healthcare_entities is long-running
poller = client.begin_analyze_healthcare_entities(documents)
result = poller  # WRONG - should call result()
```

The `begin_analyze_healthcare_entities()` method is a long-running operation that returns a poller object. You must call `.result()` on the poller to wait for the operation to complete and retrieve the actual analysis results. Without calling `.result()`, you only have the poller object, not the document analysis data.

---

## 8. Multiple Analysis (Batch) Patterns

### 8.1 ✅ CORRECT: Batch Analysis with Actions
```python
from azure.ai.textanalytics import (
    RecognizeEntitiesAction,
    ExtractKeyPhrasesAction,
    AnalyzeSentimentAction,
)

documents = ["Microsoft announced new AI features."]

poller = client.begin_analyze_actions(
    documents,
    actions=[
        AnalyzeSentimentAction(),
        RecognizeEntitiesAction(),
        ExtractKeyPhrasesAction(),
    ],
)

results = poller.result()

for doc_results in results:
    for result in doc_results:
        if result.kind == "SentimentAnalysis":
            print(f"Sentiment: {result.sentiment}")
        elif result.kind == "EntityRecognition":
            print(f"Entities: {[e.text for e in result.entities]}")
        elif result.kind == "KeyPhraseExtraction":
            print(f"Key phrases: {result.key_phrases}")
```

### 8.2 ✅ CORRECT: With PII Analysis
```python
from azure.ai.textanalytics import RecognizePiiEntitiesAction

poller = client.begin_analyze_actions(
    documents,
    actions=[
        AnalyzeSentimentAction(),
        RecognizePiiEntitiesAction(),
    ],
)

results = poller.result()
```

### 8.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not iterating nested results
```python
# WRONG - results is a list of action results, not individual document results
results = poller.result()
for result in results:
    print(result.sentiment)  # WRONG structure
```

The `poller.result()` from `begin_analyze_actions()` returns a nested structure: each element in `results` is itself a list of action results for that document. You must iterate twice: once over documents, then over their actions. Use `for doc_results in results:` then `for result in doc_results:` to properly access individual action results and their properties like `sentiment`.

---

## 9. Async Patterns

### 9.1 ✅ CORRECT: Full Async Example
```python
import asyncio
from azure.ai.textanalytics.aio import TextAnalyticsClient
from azure.identity.aio import DefaultAzureCredential

async def main():
    async with TextAnalyticsClient(
        endpoint=os.environ["AZURE_LANGUAGE_ENDPOINT"],
        credential=DefaultAzureCredential()
    ) as client:
        documents = ["This is a test."]
        
        result = await client.analyze_sentiment(documents)
        for doc in result:
            if not doc.is_error:
                print(f"Sentiment: {doc.sentiment}")

asyncio.run(main())
```

### 9.2 ✅ CORRECT: Async with Long-Running Operation
```python
async def analyze_healthcare():
    async with TextAnalyticsClient(
        endpoint=os.environ["AZURE_LANGUAGE_ENDPOINT"],
        credential=DefaultAzureCredential()
    ) as client:
        documents = ["Patient diagnosed with type 2 diabetes."]
        
        poller = await client.begin_analyze_healthcare_entities(documents)
        result = await poller.result()
        
        for doc in result:
            if not doc.is_error:
                for entity in doc.entities:
                    print(entity.text)
```

### 9.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing await
```python
# WRONG
async with TextAnalyticsClient(...) as client:
    result = client.analyze_sentiment(documents)  # Missing await
```

All async methods on the async client must be awaited. The `analyze_sentiment()` method in the async client (`TextAnalyticsClient` from `azure.ai.textanalytics.aio`) is a coroutine and returns a coroutine object without `await`. You must use `await client.analyze_sentiment(documents)` to get the actual result.

#### ❌ INCORRECT: Wrong credential type
```python
# WRONG - sync credential with async client
from azure.ai.textanalytics.aio import TextAnalyticsClient
from azure.identity import DefaultAzureCredential  # Should use .aio

async with TextAnalyticsClient(endpoint=endpoint, credential=DefaultAzureCredential()):
    ...
```

---

## 10. Error Handling Patterns

### 10.1 ✅ CORRECT: Check for Errors
```python
documents = ["Valid text", ""]

result = client.analyze_sentiment(documents)

for doc in result:
    if doc.is_error:
        print(f"Document {doc.id}: Error - {doc.error.message}")
    else:
        print(f"Document {doc.id}: Sentiment - {doc.sentiment}")
```

### 10.2 ✅ CORRECT: Handle Service Errors
```python
from azure.core.exceptions import HttpResponseError

try:
    result = client.analyze_sentiment(documents)
except HttpResponseError as e:
    print(f"Service error: {e.message}")
    print(f"Status code: {e.status_code}")
```

### 10.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Ignoring errors
```python
# WRONG
for doc in result:
    print(doc.sentiment)  # Crashes if is_error

# WRONG - empty error message
except HttpResponseError:
    pass  # Silent failure
```

---

## 11. Environment Variables

### Required Variables
```bash
AZURE_LANGUAGE_ENDPOINT=https://<resource>.cognitiveservices.azure.com
```

### Optional Variables (for API key authentication)
```bash
AZURE_LANGUAGE_KEY=<your-api-key>
```

---

## 12. Common Pattern Checklist

### Basic Operations
- [ ] Client creation with DefaultAzureCredential
- [ ] Using context manager for resource cleanup
- [ ] Checking `is_error` before accessing document results
- [ ] Proper credential type matching (sync vs async)

### Analysis Operations
- [ ] `analyze_sentiment()` with/without opinion mining
- [ ] `recognize_entities()` for NER
- [ ] `recognize_pii_entities()` with/without domain
- [ ] `extract_key_phrases()`
- [ ] `detect_language()` with/without country hint
- [ ] `recognize_linked_entities()`

### Advanced Operations
- [ ] `begin_analyze_healthcare_entities()` with polling
- [ ] `begin_analyze_actions()` for batch analysis
- [ ] Async operations with proper await syntax
- [ ] Error handling with HttpResponseError

### Async Patterns
- [ ] Async client with `aio` imports
- [ ] Async credential from `azure.identity.aio`
- [ ] `async with` context managers
- [ ] `await` on all async operations

---

## 13. Quick Reference: Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `AttributeError: is_error` | Doc is None or wrong type | Check doc exists and check `not doc.is_error` |
| `confidence_scores is None` | Missing parameter in method call | Add `show_opinion_mining=True` for sentiment |
| `iso639_name` not found | Wrong attribute name | Use `iso6391_name` (note: "6391", not "639") |
| `Sync operation in async` | Missing `await` | Add `await` to all async operations |
| `AttributeError: result()` | Forgetting long-running operation | Call `poller.result()` for `begin_*` methods |
| `HttpResponseError` | Invalid endpoint or credentials | Check AZURE_LANGUAGE_ENDPOINT and credentials |
| `Nested iteration failed` | Wrong result structure | Use `for doc_results in results:` then `for result in doc_results:` |
