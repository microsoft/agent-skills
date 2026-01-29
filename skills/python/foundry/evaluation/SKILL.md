---
name: azure-ai-evaluation-python
description: |
  Azure AI Evaluation SDK for Python. Use for evaluating generative AI applications with quality, safety, and custom evaluators.
  Triggers: "azure-ai-evaluation", "evaluators", "GroundednessEvaluator", "evaluate", "AI quality metrics".
---

# Azure AI Evaluation SDK for Python

Assess generative AI application performance with built-in and custom evaluators.

## Installation

```bash
pip install azure-ai-evaluation

# With remote evaluation support
pip install azure-ai-evaluation[remote]
```

## Environment Variables

```bash
# For AI-assisted evaluators
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

# For Foundry project integration
AIPROJECT_CONNECTION_STRING=<your-connection-string>
```

## Built-in Evaluators

### Quality Evaluators (AI-Assisted)

```python
from azure.ai.evaluation import (
    GroundednessEvaluator,
    RelevanceEvaluator,
    CoherenceEvaluator,
    FluencyEvaluator,
    SimilarityEvaluator,
    RetrievalEvaluator
)

# Initialize with Azure OpenAI model config
model_config = {
    "azure_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"],
    "api_key": os.environ["AZURE_OPENAI_API_KEY"],
    "azure_deployment": os.environ["AZURE_OPENAI_DEPLOYMENT"]
}

groundedness = GroundednessEvaluator(model_config)
relevance = RelevanceEvaluator(model_config)
coherence = CoherenceEvaluator(model_config)
```

### Quality Evaluators (NLP-based)

```python
from azure.ai.evaluation import (
    F1ScoreEvaluator,
    RougeScoreEvaluator,
    BleuScoreEvaluator,
    GleuScoreEvaluator,
    MeteorScoreEvaluator
)

f1 = F1ScoreEvaluator()
rouge = RougeScoreEvaluator()
bleu = BleuScoreEvaluator()
```

### Safety Evaluators

```python
from azure.ai.evaluation import (
    ViolenceEvaluator,
    SexualEvaluator,
    SelfHarmEvaluator,
    HateUnfairnessEvaluator,
    IndirectAttackEvaluator,
    ProtectedMaterialEvaluator
)

violence = ViolenceEvaluator(azure_ai_project=project_scope)
sexual = SexualEvaluator(azure_ai_project=project_scope)
```

## Single Row Evaluation

```python
from azure.ai.evaluation import GroundednessEvaluator

groundedness = GroundednessEvaluator(model_config)

result = groundedness(
    query="What is Azure AI?",
    context="Azure AI is Microsoft's AI platform...",
    response="Azure AI provides AI services and tools."
)

print(f"Groundedness score: {result['groundedness']}")
print(f"Reason: {result['groundedness_reason']}")
```

## Batch Evaluation with evaluate()

```python
from azure.ai.evaluation import evaluate

result = evaluate(
    data="test_data.jsonl",
    evaluators={
        "groundedness": groundedness,
        "relevance": relevance,
        "coherence": coherence
    },
    evaluator_config={
        "default": {
            "column_mapping": {
                "query": "${data.query}",
                "context": "${data.context}",
                "response": "${data.response}"
            }
        }
    }
)

print(result["metrics"])
```

## Composite Evaluators

```python
from azure.ai.evaluation import QAEvaluator, ContentSafetyEvaluator

# All quality metrics in one
qa_evaluator = QAEvaluator(model_config)

# All safety metrics in one
safety_evaluator = ContentSafetyEvaluator(azure_ai_project=project_scope)

result = evaluate(
    data="data.jsonl",
    evaluators={
        "qa": qa_evaluator,
        "content_safety": safety_evaluator
    }
)
```

## Evaluate Application Target

```python
from azure.ai.evaluation import evaluate
from my_app import chat_app  # Your application

result = evaluate(
    data="queries.jsonl",
    target=chat_app,  # Callable that takes query, returns response
    evaluators={
        "groundedness": groundedness
    },
    evaluator_config={
        "default": {
            "column_mapping": {
                "query": "${data.query}",
                "context": "${outputs.context}",
                "response": "${outputs.response}"
            }
        }
    }
)
```

## Custom Evaluators

### Code-Based

```python
from azure.ai.evaluation import evaluator

@evaluator
def word_count_evaluator(response: str) -> dict:
    return {"word_count": len(response.split())}

# Use in evaluate()
result = evaluate(
    data="data.jsonl",
    evaluators={"word_count": word_count_evaluator}
)
```

### Prompt-Based

```python
from azure.ai.evaluation import PromptChatTarget

class CustomEvaluator:
    def __init__(self, model_config):
        self.model = PromptChatTarget(model_config)
    
    def __call__(self, query: str, response: str) -> dict:
        prompt = f"Rate this response 1-5: Query: {query}, Response: {response}"
        result = self.model.send_prompt(prompt)
        return {"custom_score": int(result)}
```

## Log to Foundry Project

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project = AIProjectClient.from_connection_string(
    conn_str=os.environ["AIPROJECT_CONNECTION_STRING"],
    credential=DefaultAzureCredential()
)

result = evaluate(
    data="data.jsonl",
    evaluators={"groundedness": groundedness},
    azure_ai_project=project.scope  # Logs results to Foundry
)

print(f"View results: {result['studio_url']}")
```

## Evaluator Reference

| Evaluator | Type | Metrics |
|-----------|------|---------|
| `GroundednessEvaluator` | AI | groundedness (1-5) |
| `RelevanceEvaluator` | AI | relevance (1-5) |
| `CoherenceEvaluator` | AI | coherence (1-5) |
| `FluencyEvaluator` | AI | fluency (1-5) |
| `SimilarityEvaluator` | AI | similarity (1-5) |
| `RetrievalEvaluator` | AI | retrieval (1-5) |
| `F1ScoreEvaluator` | NLP | f1_score (0-1) |
| `RougeScoreEvaluator` | NLP | rouge scores |
| `ViolenceEvaluator` | Safety | violence (0-7) |
| `SexualEvaluator` | Safety | sexual (0-7) |
| `SelfHarmEvaluator` | Safety | self_harm (0-7) |
| `HateUnfairnessEvaluator` | Safety | hate_unfairness (0-7) |
| `QAEvaluator` | Composite | All quality metrics |
| `ContentSafetyEvaluator` | Composite | All safety metrics |

## Best Practices

1. **Use composite evaluators** for comprehensive assessment
2. **Map columns correctly** — mismatched columns cause silent failures
3. **Log to Foundry** for tracking and comparison across runs
4. **Create custom evaluators** for domain-specific metrics
5. **Use NLP evaluators** when you have ground truth answers
6. **Safety evaluators require** Azure AI project scope
7. **Batch evaluation** is more efficient than single-row loops

## Reference Files

| File | Contents |
|------|----------|
| [references/built-in-evaluators.md](references/built-in-evaluators.md) | Detailed patterns for AI-assisted, NLP-based, and Safety evaluators with configuration tables |
| [references/custom-evaluators.md](references/custom-evaluators.md) | Creating code-based and prompt-based custom evaluators, testing patterns |
| [scripts/run_batch_evaluation.py](scripts/run_batch_evaluation.py) | CLI tool for running batch evaluations with quality, safety, and custom evaluators |
