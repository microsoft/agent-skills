# Deployments Operations Reference

## Overview

Deployments represent AI model deployments in your Azure AI Foundry project.

## List Deployments

### List All Deployments

```python
deployments = project_client.deployments.list()
for deployment in deployments:
    print(f"Name: {deployment.name}")
    print(f"Model: {deployment.model_name}")
    print(f"Publisher: {deployment.model_publisher}")
    print("---")
```

### Filter by Publisher

```python
# List only OpenAI model deployments
for deployment in project_client.deployments.list(model_publisher="OpenAI"):
    print(f"{deployment.name}: {deployment.model_name}")
```

### Filter by Model Name

```python
# List deployments of a specific model
for deployment in project_client.deployments.list(model_name="gpt-4o"):
    print(f"{deployment.name}: {deployment.model_version}")
```

## Get Deployment

```python
from azure.ai.projects.models import ModelDeployment

deployment = project_client.deployments.get("my-deployment-name")

if isinstance(deployment, ModelDeployment):
    print(f"Type: {deployment.type}")
    print(f"Name: {deployment.name}")
    print(f"Model Name: {deployment.model_name}")
    print(f"Model Version: {deployment.model_version}")
    print(f"Model Publisher: {deployment.model_publisher}")
    print(f"Capabilities: {deployment.capabilities}")
```

## Deployment Properties

```python
deployment = project_client.deployments.get("gpt-4o-mini")

# Available properties
print(f"Name: {deployment.name}")           # Deployment name
print(f"Model: {deployment.model_name}")    # e.g., "gpt-4o-mini"
print(f"Version: {deployment.model_version}")  # e.g., "2024-07-18"
print(f"Publisher: {deployment.model_publisher}")  # e.g., "OpenAI"
print(f"Type: {deployment.type}")           # Deployment type
print(f"Capabilities: {deployment.capabilities}")  # Model capabilities
```

## Using Deployments

### Dynamic Model Selection

```python
# Find available GPT-4 deployments
gpt4_deployments = [
    d for d in project_client.deployments.list()
    if "gpt-4" in d.model_name.lower()
]

if gpt4_deployments:
    deployment_name = gpt4_deployments[0].name
    
    agent = project_client.agents.create_agent(
        model=deployment_name,
        name="dynamic-agent",
        instructions="You are helpful.",
    )
```

### Capability Checking

```python
deployment = project_client.deployments.get("my-deployment")

# Check if deployment supports certain capabilities
if deployment.capabilities:
    supports_vision = deployment.capabilities.get("vision", False)
    supports_functions = deployment.capabilities.get("function_calling", False)
    
    print(f"Vision: {supports_vision}")
    print(f"Function Calling: {supports_functions}")
```

## Environment Variables Pattern

```bash
# Store deployment name in environment
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini
```

```python
import os

# Use deployment from environment
agent = project_client.agents.create_agent(
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="You are helpful.",
)
```

## List Available Models

```python
# Print all available models grouped by publisher
from collections import defaultdict

deployments_by_publisher = defaultdict(list)

for deployment in project_client.deployments.list():
    deployments_by_publisher[deployment.model_publisher].append(deployment)

for publisher, deployments in deployments_by_publisher.items():
    print(f"\n{publisher}:")
    for d in deployments:
        print(f"  - {d.name} ({d.model_name} v{d.model_version})")
```
