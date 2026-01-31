# Skill Creator Acceptance Criteria

**Tool**: Skill Creator Guide
**Purpose**: Skill testing acceptance criteria for validating skill creation patterns

---

## 1. SKILL.md Structure

### 1.1 Frontmatter

#### ✅ CORRECT: Valid YAML frontmatter
```yaml
---
name: my-skill-py
description: Brief description of what the skill does and when to use it. Triggers on specific keywords or scenarios.
---
```

#### ✅ CORRECT: With package field for SDKs
```yaml
---
name: azure-ai-inference-py
description: Azure AI Inference SDK for Python. Use for chat completions and embeddings.
package: azure-ai-inference
---
```

#### ❌ INCORRECT: Missing required fields
```yaml
---
name: my-skill
---
```

#### ❌ INCORRECT: Description too long (over 500 chars)
```yaml
---
name: my-skill
description: [Very long description that exceeds 500 characters...]
---
```

---

## 2. Skill Naming

### 2.1 Language Suffixes

#### ✅ CORRECT: Language-specific suffixes
```
azure-ai-inference-py          # Python
azure-ai-inference-dotnet      # .NET/C#
azure-ai-inference-ts          # TypeScript
azure-ai-inference-java        # Java
```

#### ✅ CORRECT: Core skills (no suffix)
```
mcp-builder                    # Cross-language
skill-creator                  # Meta/tooling
azd-deployment                 # Infrastructure
```

#### ❌ INCORRECT: Wrong or missing suffix
```
azure-ai-inference             # Missing language suffix
azure-ai-inference-python      # Wrong suffix (use -py)
azure-ai-inference-csharp      # Wrong suffix (use -dotnet)
```

---

## 3. Skill Body Structure

### 3.1 SDK Skills Structure

#### ✅ CORRECT: Standard SDK skill structure
```markdown
# SDK Name

Brief introduction.

## Installation

```bash
pip install package-name
```

## Environment Variables

```bash
AZURE_ENDPOINT=https://...
```

## Authentication

```python
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
```

## Core Workflow

[Minimal viable example]

## Feature Tables

| Method | Description |
|--------|-------------|

## Best Practices

1. Use DefaultAzureCredential
2. Handle errors properly
3. Close clients

## Reference Links

| Topic | Link |
|-------|------|
```

#### ❌ INCORRECT: Missing essential sections
```markdown
# SDK Name

Here's some code:
```python
# random code without context
```
```

---

## 4. Authentication Patterns

### 4.1 DefaultAzureCredential (Required)

#### ✅ CORRECT: Python
```python
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
client = ServiceClient(endpoint, credential)
```

#### ✅ CORRECT: C#/.NET
```csharp
var credential = new DefaultAzureCredential();
var client = new ServiceClient(new Uri(endpoint), credential);
```

#### ✅ CORRECT: Java
```java
TokenCredential credential = new DefaultAzureCredentialBuilder().build();
ServiceClient client = new ServiceClientBuilder()
    .endpoint(endpoint)
    .credential(credential)
    .buildClient();
```

#### ✅ CORRECT: TypeScript
```typescript
import { DefaultAzureCredential } from "@azure/identity";
const credential = new DefaultAzureCredential();
const client = new ServiceClient(endpoint, credential);
```

#### ❌ INCORRECT: Hardcoded credentials
```python
client = ServiceClient(endpoint, "hardcoded-api-key")
```

---

## 5. Environment Variables

### 5.1 Configuration Pattern

#### ✅ CORRECT: Environment-based configuration
```python
import os
endpoint = os.environ["AZURE_ENDPOINT"]
```

#### ✅ CORRECT: With defaults
```python
import os
endpoint = os.getenv("AZURE_ENDPOINT", "https://default.endpoint.com")
```

#### ❌ INCORRECT: Hardcoded values
```python
endpoint = "https://my-resource.azure.com"
```

---

## 6. File Organization

### 6.1 Skill Directory Structure

#### ✅ CORRECT: Standard structure
```
skill-name/
├── SKILL.md                    # Required
└── references/                 # Optional
    ├── acceptance-criteria.md  # For testing
    ├── api-reference.md        # Detailed docs
    └── examples.md             # Code examples
```

#### ✅ CORRECT: With scripts
```
skill-name/
├── SKILL.md
├── references/
└── scripts/
    └── helper.py               # Reusable scripts
```

#### ❌ INCORRECT: Including unnecessary files
```
skill-name/
├── SKILL.md
├── README.md                   # Duplicate of SKILL.md
├── CHANGELOG.md                # Not needed
└── package.json                # Don't include dependencies
```

---

## 7. Code Examples

### 7.1 Example Quality

#### ✅ CORRECT: Complete, runnable example
```python
import os
from azure.identity import DefaultAzureCredential
from azure.ai.inference import ChatCompletionsClient

endpoint = os.environ["AZURE_INFERENCE_ENDPOINT"]
credential = DefaultAzureCredential()

client = ChatCompletionsClient(endpoint=endpoint, credential=credential)

response = client.complete(
    messages=[{"role": "user", "content": "Hello"}]
)

print(response.choices[0].message.content)
```

#### ❌ INCORRECT: Incomplete snippet
```python
client.complete(messages)  # What is client? What are messages?
```

---

## 8. Best Practices Section

### 8.1 Required Best Practices

#### ✅ CORRECT: Numbered, actionable practices
```markdown
## Best Practices

1. **Use DefaultAzureCredential** - Works across local dev and Azure deployment
2. **Read from environment variables** - Never hardcode endpoints or keys
3. **Handle errors with try/except** - Catch specific exceptions
4. **Close clients properly** - Use context managers or explicit close
5. **Use async for I/O** - Prefer async clients for concurrent operations
```

#### ❌ INCORRECT: Vague or missing
```markdown
## Best Practices

Follow good coding practices.
```
