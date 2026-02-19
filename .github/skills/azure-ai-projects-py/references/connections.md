# Connections Operations Reference

## Overview

Connections provide access to external Azure services like Azure OpenAI, Azure AI Search, Bing, and more.

## List Connections

### List All Connections

```python
connections = project_client.connections.list()
for conn in connections:
    print(f"Name: {conn.name}")
    print(f"Type: {conn.connection_type}")
    print(f"ID: {conn.id}")
    print("---")
```

### Filter by Connection Type

```python
from azure.ai.projects.models import ConnectionType

# List Azure OpenAI connections
for conn in project_client.connections.list(
    connection_type=ConnectionType.AZURE_OPEN_AI
):
    print(f"Azure OpenAI: {conn.name}")

# List Azure AI Search connections
for conn in project_client.connections.list(
    connection_type=ConnectionType.AZURE_AI_SEARCH
):
    print(f"AI Search: {conn.name}")
```

## Connection Types

```python
from azure.ai.projects.models import ConnectionType

# Available connection types:
# - ConnectionType.AZURE_OPEN_AI
# - ConnectionType.AZURE_AI_SEARCH
# - ConnectionType.AZURE_BLOB
# - ConnectionType.AZURE_AI_SERVICES
# - ConnectionType.API_KEY
# - ConnectionType.COGNITIVE_SEARCH
# - ConnectionType.COGNITIVE_SERVICE
# - ConnectionType.CUSTOM
```

## Get Connection

### Get by Name

```python
connection = project_client.connections.get(connection_name="my-search-connection")
print(f"Name: {connection.name}")
print(f"Type: {connection.connection_type}")
```

### Get with Credentials

```python
connection = project_client.connections.get(
    connection_name="my-search-connection",
    include_credentials=True,
)
print(f"Endpoint: {connection.endpoint_url}")
# Access credentials based on connection type
```

### Get Default Connection

```python
from azure.ai.projects.models import ConnectionType

# Get default Azure OpenAI connection
default_aoai = project_client.connections.get_default(
    connection_type=ConnectionType.AZURE_OPEN_AI
)
print(f"Default Azure OpenAI: {default_aoai.name}")

# Get with credentials
default_aoai = project_client.connections.get_default(
    connection_type=ConnectionType.AZURE_OPEN_AI,
    include_credentials=True,
)
```

## Using Connections with Tools

### Bing Grounding

```python
from azure.ai.projects.models import (
    BingGroundingAgentTool,
    BingGroundingSearchToolParameters,
    BingGroundingSearchConfiguration,
)

# Get Bing connection
bing_connection = project_client.connections.get(
    os.environ["BING_CONNECTION_NAME"]
)

# Use in agent
tools = [
    BingGroundingAgentTool(
        bing_grounding=BingGroundingSearchToolParameters(
            search_configurations=[
                BingGroundingSearchConfiguration(
                    project_connection_id=bing_connection.id
                )
            ]
        )
    )
]
```

### Azure AI Search

```python
from azure.ai.projects.models import (
    AzureAISearchAgentTool,
    AzureAISearchToolResource,
    AISearchIndexResource,
    AzureAISearchQueryType,
)

# Get search connection
search_connection = project_client.connections.get(
    os.environ["AI_SEARCH_CONNECTION_NAME"]
)

# Use in agent
tools = [
    AzureAISearchAgentTool(
        azure_ai_search=AzureAISearchToolResource(
            indexes=[
                AISearchIndexResource(
                    project_connection_id=search_connection.id,
                    index_name="my-index",
                    query_type=AzureAISearchQueryType.SEMANTIC,
                )
            ]
        )
    )
]
```

### OpenAI Client from Connection

```python
# Get OpenAI client for a specific Azure OpenAI connection
openai_client = project_client.get_openai_client(
    api_version="2024-10-21",
    connection_name="my-aoai-connection",
)

response = openai_client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

## Connection Properties

```python
connection = project_client.connections.get(
    connection_name="my-connection",
    include_credentials=True,
)

# Common properties
print(f"ID: {connection.id}")
print(f"Name: {connection.name}")
print(f"Type: {connection.connection_type}")
print(f"Endpoint: {connection.endpoint_url}")

# Check authentication type
if hasattr(connection, 'authentication_type'):
    print(f"Auth Type: {connection.authentication_type}")
```

## Environment Variables Pattern

```bash
# Recommended environment variables for connections
BING_CONNECTION_NAME=my-bing-connection
AI_SEARCH_CONNECTION_NAME=my-search-connection
AOAI_CONNECTION_NAME=my-aoai-connection
```

```python
import os

# Load connections from environment
bing_conn = project_client.connections.get(os.environ["BING_CONNECTION_NAME"])
search_conn = project_client.connections.get(os.environ["AI_SEARCH_CONNECTION_NAME"])
```
