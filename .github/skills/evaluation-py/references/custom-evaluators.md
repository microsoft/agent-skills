# Custom Evaluators Reference

Patterns for creating custom evaluators with Azure AI Evaluation SDK.

## Code-Based Evaluators

### Simple Function Evaluator

Use the `@evaluator` decorator for simple metrics:

```python
from azure.ai.evaluation import evaluator

@evaluator
def word_count_evaluator(response: str) -> dict:
    """Count words in response."""
    return {"word_count": len(response.split())}

@evaluator
def response_length_evaluator(response: str) -> dict:
    """Measure response length in characters."""
    return {
        "char_count": len(response),
        "is_concise": len(response) < 500
    }

# Usage
result = word_count_evaluator(response="Hello world")
# {"word_count": 2}
```

### Multi-Input Evaluator

Evaluators can accept multiple inputs:

```python
from azure.ai.evaluation import evaluator

@evaluator
def keyword_coverage_evaluator(
    query: str,
    response: str,
    required_keywords: list[str] | None = None
) -> dict:
    """Check if response covers required keywords from query."""
    if required_keywords is None:
        # Extract keywords from query
        required_keywords = [w.lower() for w in query.split() if len(w) > 3]
    
    response_lower = response.lower()
    covered = [kw for kw in required_keywords if kw in response_lower]
    
    coverage = len(covered) / len(required_keywords) if required_keywords else 1.0
    
    return {
        "keyword_coverage": coverage,
        "keywords_found": covered,
        "keywords_missing": [kw for kw in required_keywords if kw not in response_lower]
    }
```

### Class-Based Evaluator

For evaluators needing initialization or state:

```python
from azure.ai.evaluation import evaluator

class DomainSpecificEvaluator:
    """Evaluator with domain-specific vocabulary."""
    
    def __init__(self, domain_terms: list[str], threshold: float = 0.5):
        self.domain_terms = [t.lower() for t in domain_terms]
        self.threshold = threshold
    
    def __call__(self, response: str) -> dict:
        response_lower = response.lower()
        matches = sum(1 for term in self.domain_terms if term in response_lower)
        score = matches / len(self.domain_terms) if self.domain_terms else 0
        
        return {
            "domain_relevance": score,
            "domain_terms_found": matches,
            "passes_threshold": score >= self.threshold
        }

# Usage
azure_evaluator = DomainSpecificEvaluator(
    domain_terms=["azure", "cloud", "microsoft", "deployment", "resource"],
    threshold=0.4
)

result = azure_evaluator(response="Deploy your app to Azure cloud resources.")
```

### Async Evaluator

For evaluators that need async operations:

```python
import asyncio
from azure.ai.evaluation import evaluator

@evaluator
async def async_validation_evaluator(response: str, context: str) -> dict:
    """Async evaluator for external validation."""
    # Simulate async validation (e.g., external API call)
    await asyncio.sleep(0.1)
    
    # Check factual consistency
    context_words = set(context.lower().split())
    response_words = set(response.lower().split())
    overlap = len(context_words & response_words)
    
    return {
        "context_overlap": overlap,
        "validation_status": "valid" if overlap > 5 else "needs_review"
    }
```

## Prompt-Based Evaluators

### Using PromptChatTarget

Create evaluators that use LLM judgment:

```python
from azure.ai.evaluation import AzureOpenAIModelConfiguration

class PromptBasedEvaluator:
    """LLM-based evaluator using custom prompts."""
    
    EVALUATION_PROMPT = """You are an expert evaluator. Rate the following response.

Query: {query}
Response: {response}

Rate the response on a scale of 1-5 for:
1. Accuracy: Is the information correct?
2. Completeness: Does it fully answer the query?
3. Clarity: Is it easy to understand?

Return ONLY a JSON object with keys: accuracy, completeness, clarity (integers 1-5).
"""
    
    def __init__(self, model_config: dict):
        from openai import AzureOpenAI
        
        self.client = AzureOpenAI(
            azure_endpoint=model_config["azure_endpoint"],
            api_key=model_config.get("api_key"),
            api_version=model_config.get("api_version", "2024-06-01")
        )
        self.deployment = model_config["azure_deployment"]
    
    def __call__(self, query: str, response: str) -> dict:
        import json
        
        prompt = self.EVALUATION_PROMPT.format(query=query, response=response)
        
        completion = self.client.chat.completions.create(
            model=self.deployment,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(completion.choices[0].message.content)
        
        # Add aggregate score
        result["overall_score"] = (
            result["accuracy"] + result["completeness"] + result["clarity"]
        ) / 3
        
        return result
```

### Multi-Criteria Prompt Evaluator

```python
class MultiCriteriaEvaluator:
    """Evaluate against multiple criteria with detailed feedback."""
    
    CRITERIA = {
        "technical_accuracy": "Is the technical information correct and precise?",
        "best_practices": "Does it follow industry best practices?",
        "security": "Are security considerations addressed?",
        "performance": "Are performance implications considered?"
    }
    
    PROMPT_TEMPLATE = """Evaluate this response against the criterion.

Query: {query}
Response: {response}
Context: {context}

Criterion: {criterion_name}
Definition: {criterion_definition}

Provide:
1. Score (1-5): 1=poor, 5=excellent
2. Reason: Brief explanation (1-2 sentences)

Return JSON: {{"score": <int>, "reason": "<string>"}}
"""
    
    def __init__(self, model_config: dict, criteria: dict | None = None):
        from openai import AzureOpenAI
        
        self.client = AzureOpenAI(
            azure_endpoint=model_config["azure_endpoint"],
            api_key=model_config.get("api_key"),
            api_version=model_config.get("api_version", "2024-06-01")
        )
        self.deployment = model_config["azure_deployment"]
        self.criteria = criteria or self.CRITERIA
    
    def __call__(
        self,
        query: str,
        response: str,
        context: str = ""
    ) -> dict:
        import json
        
        results = {}
        scores = []
        
        for name, definition in self.criteria.items():
            prompt = self.PROMPT_TEMPLATE.format(
                query=query,
                response=response,
                context=context,
                criterion_name=name,
                criterion_definition=definition
            )
            
            completion = self.client.chat.completions.create(
                model=self.deployment,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            criterion_result = json.loads(completion.choices[0].message.content)
            results[f"{name}_score"] = criterion_result["score"]
            results[f"{name}_reason"] = criterion_result["reason"]
            scores.append(criterion_result["score"])
        
        results["aggregate_score"] = sum(scores) / len(scores)
        return results
```

## Composite Custom Evaluators

### Combining Multiple Evaluators

```python
from azure.ai.evaluation import (
    GroundednessEvaluator,
    RelevanceEvaluator,
    evaluate
)

class ComprehensiveEvaluator:
    """Combine built-in and custom evaluators."""
    
    def __init__(self, model_config: dict):
        self.groundedness = GroundednessEvaluator(model_config)
        self.relevance = RelevanceEvaluator(model_config)
        self.custom_domain = DomainSpecificEvaluator(
            domain_terms=["azure", "cloud", "api"]
        )
    
    def __call__(
        self,
        query: str,
        context: str,
        response: str
    ) -> dict:
        results = {}
        
        # Run built-in evaluators
        ground_result = self.groundedness(
            query=query, context=context, response=response
        )
        rel_result = self.relevance(
            query=query, context=context, response=response
        )
        
        # Run custom evaluator
        domain_result = self.custom_domain(response=response)
        
        # Combine results
        results.update(ground_result)
        results.update(rel_result)
        results.update(domain_result)
        
        # Calculate weighted score
        results["composite_score"] = (
            ground_result.get("groundedness", 0) * 0.4 +
            rel_result.get("relevance", 0) * 0.4 +
            domain_result.get("domain_relevance", 0) * 5 * 0.2  # Scale to 1-5
        )
        
        return results
```

## Using Custom Evaluators in Batch Evaluation

### With evaluate() Function

```python
from azure.ai.evaluation import evaluate

# Define custom evaluators
@evaluator
def format_checker(response: str) -> dict:
    has_code = "```" in response
    has_list = any(line.strip().startswith(("-", "*", "1.")) 
                   for line in response.split("\n"))
    return {
        "has_code_blocks": has_code,
        "has_lists": has_list,
        "is_structured": has_code or has_list
    }

domain_eval = DomainSpecificEvaluator(["python", "azure", "sdk"])

# Run batch evaluation
result = evaluate(
    data="test_data.jsonl",
    evaluators={
        "format": format_checker,
        "domain": domain_eval,
        "groundedness": GroundednessEvaluator(model_config)
    },
    evaluator_config={
        "default": {
            "column_mapping": {
                "query": "${data.question}",
                "context": "${data.context}",
                "response": "${data.answer}"
            }
        }
    }
)

print(result["metrics"])
```

### Column Mapping for Custom Evaluators

```python
result = evaluate(
    data="data.jsonl",
    evaluators={
        "keyword_coverage": keyword_coverage_evaluator
    },
    evaluator_config={
        "keyword_coverage": {
            "column_mapping": {
                "query": "${data.user_query}",
                "response": "${data.model_response}",
                "required_keywords": "${data.expected_keywords}"
            }
        }
    }
)
```

## Evaluator Testing Patterns

### Unit Testing Custom Evaluators

```python
import pytest
from my_evaluators import word_count_evaluator, DomainSpecificEvaluator

class TestWordCountEvaluator:
    def test_empty_response(self):
        result = word_count_evaluator(response="")
        assert result["word_count"] == 0
    
    def test_simple_response(self):
        result = word_count_evaluator(response="Hello world")
        assert result["word_count"] == 2
    
    def test_multiline_response(self):
        result = word_count_evaluator(response="Hello\nworld\ntest")
        assert result["word_count"] == 3

class TestDomainSpecificEvaluator:
    @pytest.fixture
    def evaluator(self):
        return DomainSpecificEvaluator(
            domain_terms=["azure", "cloud"],
            threshold=0.5
        )
    
    def test_full_coverage(self, evaluator):
        result = evaluator(response="Azure cloud services")
        assert result["domain_relevance"] == 1.0
        assert result["passes_threshold"] is True
    
    def test_partial_coverage(self, evaluator):
        result = evaluator(response="Deploy to Azure")
        assert result["domain_relevance"] == 0.5
        assert result["passes_threshold"] is True
    
    def test_no_coverage(self, evaluator):
        result = evaluator(response="Hello world")
        assert result["domain_relevance"] == 0.0
        assert result["passes_threshold"] is False
```

## Best Practices

1. **Return dictionaries** - All evaluators must return `dict` with metric names as keys
2. **Use descriptive metric names** - Include evaluator context in key names (e.g., `domain_relevance` not just `score`)
3. **Handle edge cases** - Empty inputs, missing fields, None values
4. **Keep evaluators focused** - One evaluator = one concept (combine with composite evaluators)
5. **Document input requirements** - Clear docstrings explaining expected inputs
6. **Test thoroughly** - Unit tests for all custom evaluators before batch evaluation
7. **Consider async** - Use async for evaluators with I/O operations
8. **Normalize scores** - Keep scores in consistent ranges (0-1 or 1-5)
