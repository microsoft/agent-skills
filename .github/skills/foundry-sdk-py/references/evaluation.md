# Evaluation Operations Reference

## Overview

Evaluations in Azure AI Foundry use the OpenAI client's evals API to test agent quality.

## Setup

```python
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, DataSourceConfigCustom
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# Get OpenAI client for evals
openai_client = project_client.get_openai_client()
```

## Create Evaluation

### Define Data Source Configuration

```python
from azure.ai.projects.models import DataSourceConfigCustom

data_source_config = DataSourceConfigCustom(
    type="custom",
    item_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "expected_response": {"type": "string"},
        },
        "required": ["query"],
    },
    include_sample_schema=True,
)
```

### Define Testing Criteria (Evaluators)

```python
# Built-in evaluators
testing_criteria = [
    {
        "type": "azure_ai_evaluator",
        "name": "violence_detection",
        "evaluator_name": "builtin.violence",
        "data_mapping": {
            "query": "{{item.query}}",
            "response": "{{item.response}}",
        },
    },
    {
        "type": "azure_ai_evaluator",
        "name": "fluency_check",
        "evaluator_name": "builtin.fluency",
        "data_mapping": {
            "query": "{{item.query}}",
            "response": "{{item.response}}",
        },
    },
    {
        "type": "azure_ai_evaluator",
        "name": "task_adherence",
        "evaluator_name": "builtin.task_adherence",
        "data_mapping": {
            "query": "{{item.query}}",
            "response": "{{item.response}}",
        },
    },
]
```

### Create Evaluation Object

```python
eval_object = openai_client.evals.create(
    name="Agent Quality Evaluation",
    data_source_config=data_source_config,
    testing_criteria=testing_criteria,
)
print(f"Created evaluation: {eval_object.id}")
```

## Run Evaluation

### Define Test Data

```python
# Inline test data
data_source = {
    "type": "azure_ai_target_completions",
    "source": {
        "type": "file_content",
        "content": [
            {"item": {"query": "What is the capital of France?"}},
            {"item": {"query": "How do I reverse a string in Python?"}},
            {"item": {"query": "Explain machine learning in simple terms."}},
        ],
    },
    "input_messages": {
        "type": "template",
        "template": [
            {
                "type": "message",
                "role": "user",
                "content": {"type": "input_text", "text": "{{item.query}}"},
            }
        ],
    },
    "target": {
        "type": "azure_ai_agent",
        "name": agent.name,
        "version": agent.version,
    },
}
```

### Execute Evaluation Run

```python
eval_run = openai_client.evals.runs.create(
    eval_id=eval_object.id,
    name=f"Evaluation Run for Agent {agent.name}",
    data_source=data_source,
)
print(f"Evaluation run created: {eval_run.id}")
```

## Built-in Evaluators

| Evaluator | Description | Data Mapping |
|-----------|-------------|--------------|
| `builtin.violence` | Detects violent content | query, response |
| `builtin.fluency` | Measures response fluency | query, response |
| `builtin.task_adherence` | Checks if response follows instructions | query, response |
| `builtin.groundedness` | Checks factual grounding | query, response, context |
| `builtin.relevance` | Measures response relevance | query, response |
| `builtin.coherence` | Checks logical coherence | query, response |
| `builtin.similarity` | Compares to expected response | response, expected_response |

## Full Evaluation Example

```python
import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, DataSourceConfigCustom
from azure.identity import DefaultAzureCredential

# Setup
project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
openai_client = project_client.get_openai_client()

# Create agent
agent = project_client.agents.create_version(
    agent_name="eval-test-agent",
    definition=PromptAgentDefinition(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        instructions="You are a helpful assistant that answers questions concisely.",
    ),
)

# Configure evaluation
data_source_config = DataSourceConfigCustom(
    type="custom",
    item_schema={
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    },
    include_sample_schema=True,
)

testing_criteria = [
    {
        "type": "azure_ai_evaluator",
        "name": "fluency",
        "evaluator_name": "builtin.fluency",
        "data_mapping": {
            "query": "{{item.query}}",
            "response": "{{item.response}}",
        },
    },
    {
        "type": "azure_ai_evaluator",
        "name": "relevance",
        "evaluator_name": "builtin.relevance",
        "data_mapping": {
            "query": "{{item.query}}",
            "response": "{{item.response}}",
        },
    },
]

# Create evaluation
eval_object = openai_client.evals.create(
    name="Quality Check",
    data_source_config=data_source_config,
    testing_criteria=testing_criteria,
)

# Run evaluation
data_source = {
    "type": "azure_ai_target_completions",
    "source": {
        "type": "file_content",
        "content": [
            {"item": {"query": "What is 2+2?"}},
            {"item": {"query": "Who wrote Romeo and Juliet?"}},
        ],
    },
    "input_messages": {
        "type": "template",
        "template": [
            {
                "type": "message",
                "role": "user",
                "content": {"type": "input_text", "text": "{{item.query}}"},
            }
        ],
    },
    "target": {
        "type": "azure_ai_agent",
        "name": agent.name,
        "version": agent.version,
    },
}

eval_run = openai_client.evals.runs.create(
    eval_id=eval_object.id,
    name="Test Run",
    data_source=data_source,
)

print(f"Evaluation run created: {eval_run.id}")
print(f"Status: {eval_run.status}")
```

## Custom Evaluators

```python
# Define custom evaluator with specific criteria
custom_evaluator = {
    "type": "azure_ai_evaluator",
    "name": "custom_length_check",
    "evaluator_name": "builtin.fluency",  # Base on existing evaluator
    "data_mapping": {
        "query": "{{item.query}}",
        "response": "{{item.response}}",
    },
    "threshold": 0.8,  # Pass threshold
}

testing_criteria = [custom_evaluator]
```

## Evaluation with Ground Truth

```python
data_source_config = DataSourceConfigCustom(
    type="custom",
    item_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "expected_response": {"type": "string"},
        },
        "required": ["query", "expected_response"],
    },
    include_sample_schema=True,
)

testing_criteria = [
    {
        "type": "azure_ai_evaluator",
        "name": "similarity",
        "evaluator_name": "builtin.similarity",
        "data_mapping": {
            "response": "{{item.response}}",
            "expected_response": "{{item.expected_response}}",
        },
    },
]

# Test data with ground truth
data_source = {
    "type": "azure_ai_target_completions",
    "source": {
        "type": "file_content",
        "content": [
            {
                "item": {
                    "query": "What is the capital of France?",
                    "expected_response": "Paris",
                }
            },
        ],
    },
    # ...
}
```
