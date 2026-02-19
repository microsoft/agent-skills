# Acceptance Criteria: hosted-agents-v2-py

**SDK**: `azure-ai-projects`  
**Minimum Version**: `>=2.0.0b3`  
**Repository**: https://github.com/Azure/azure-sdk-for-python

---

## 1. Correct Import Patterns

### 1.1 Client and Model Imports

#### ✅ CORRECT: All imports from azure.ai.projects

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    ImageBasedHostedAgentDefinition,
    ProtocolVersionRecord,
    AgentProtocol,
)
```

#### ✅ CORRECT: Async imports

```python
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    ImageBasedHostedAgentDefinition,
    ProtocolVersionRecord,
    AgentProtocol,
)
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Importing from azure.ai.agents

```python
# WRONG - ImageBasedHostedAgentDefinition is NOT in azure.ai.agents
from azure.ai.agents.models import ImageBasedHostedAgentDefinition
```

#### ❌ INCORRECT: Importing from azure.ai.agents directly

```python
# WRONG - These models are in azure.ai.projects.models
from azure.ai.agents import (
    ImageBasedHostedAgentDefinition,
    ProtocolVersionRecord,
)
```

#### ❌ INCORRECT: Wrong module path for AgentProtocol

```python
# WRONG - AgentProtocol is in azure.ai.projects.models
from azure.ai.projects import AgentProtocol
```

#### ❌ INCORRECT: Using AgentsClient instead of AIProjectClient

```python
# WRONG - Hosted agents use AIProjectClient, not AgentsClient
from azure.ai.agents import AgentsClient
```

---

## 2. Client Creation Patterns

### 2.1 Correct Client Creation

#### ✅ CORRECT: AIProjectClient with DefaultAzureCredential

```python
import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential()
)
```

#### ✅ CORRECT: Async client with context manager

```python
import os
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient

async with DefaultAzureCredential() as credential:
    async with AIProjectClient(
        endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        credential=credential
    ) as client:
        # Use client here
        pass
```

### 2.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using AgentsClient for hosted agents

```python
# WRONG - Hosted agents require AIProjectClient
from azure.ai.agents import AgentsClient

client = AgentsClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential()
)
```

#### ❌ INCORRECT: Hardcoded credentials

```python
# WRONG - Never hardcode credentials
client = AIProjectClient(
    endpoint="https://myresource.services.ai.azure.com/api/projects/myproject",
    credential=DefaultAzureCredential()
)
```

#### ❌ INCORRECT: Missing credential

```python
# WRONG - credential is required
client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"]
)
```

---

## 3. Hosted Agent Creation Patterns

### 3.1 Correct Agent Creation

#### ✅ CORRECT: Basic hosted agent with ImageBasedHostedAgentDefinition

```python
from azure.ai.projects.models import (
    ImageBasedHostedAgentDefinition,
    ProtocolVersionRecord,
    AgentProtocol,
)

agent = client.agents.create_version(
    agent_name="my-hosted-agent",
    definition=ImageBasedHostedAgentDefinition(
        container_protocol_versions=[
            ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES, version="v1")
        ],
        image="myregistry.azurecr.io/my-agent:latest"
    )
)
```

#### ✅ CORRECT: Agent with resource allocation

```python
agent = client.agents.create_version(
    agent_name="my-hosted-agent",
    definition=ImageBasedHostedAgentDefinition(
        container_protocol_versions=[
            ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES, version="v1")
        ],
        image="myregistry.azurecr.io/my-agent:latest",
        cpu="2",
        memory="4Gi"
    )
)
```

#### ✅ CORRECT: Agent with tools and environment variables

```python
agent = client.agents.create_version(
    agent_name="my-hosted-agent",
    definition=ImageBasedHostedAgentDefinition(
        container_protocol_versions=[
            ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES, version="v1")
        ],
        image="myregistry.azurecr.io/my-agent:latest",
        cpu="1",
        memory="2Gi",
        tools=[{"type": "code_interpreter"}],
        environment_variables={
            "AZURE_AI_PROJECT_ENDPOINT": os.environ["AZURE_AI_PROJECT_ENDPOINT"],
            "MODEL_NAME": "gpt-4o-mini"
        }
    )
)
```

### 3.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using create_agent instead of create_version

```python
# WRONG - Hosted agents use create_version, not create_agent
agent = client.agents.create_agent(
    name="wrong-agent-example",
    definition=ImageBasedHostedAgentDefinition(...)
)
```

#### ❌ INCORRECT: Missing container_protocol_versions

```python
# WRONG - container_protocol_versions is required
agent = client.agents.create_version(
    agent_name="missing-protocol-agent",
    definition=ImageBasedHostedAgentDefinition(
        image="wrong.azurecr.io/incomplete-agent:latest"
    )
)
```

#### ❌ INCORRECT: Missing image parameter

```python
# WRONG - image is required for ImageBasedHostedAgentDefinition
agent = client.agents.create_version(
    agent_name="missing-image-agent",
    definition=ImageBasedHostedAgentDefinition(
        container_protocol_versions=[
            ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES, version="v1")
        ]
    )
)
```

#### ❌ INCORRECT: Using wrong protocol enum

```python
# WRONG - Must use AgentProtocol enum, not string
agent = client.agents.create_version(
    agent_name="wrong-protocol-agent",
    definition=ImageBasedHostedAgentDefinition(
        container_protocol_versions=[
            ProtocolVersionRecord(protocol="responses", version="v1")
        ],
        image="wrong.azurecr.io/string-protocol-agent:latest"
    )
)
```

#### ❌ INCORRECT: Passing model parameter (not applicable to hosted agents)

```python
# WRONG - Hosted agents don't take model parameter in definition
agent = client.agents.create_version(
    agent_name="wrong-model-agent",
    definition=ImageBasedHostedAgentDefinition(
        container_protocol_versions=[...],
        image="wrong.azurecr.io/model-param-agent:latest",
        model="gpt-4o-mini"  # WRONG - use environment_variables instead
    )
)
```

---

## 4. Protocol Version Patterns

### 4.1 Correct Protocol Configuration

#### ✅ CORRECT: RESPONSES protocol with v1

```python
container_protocol_versions=[
    ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES, version="v1")
]
```

### 4.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using string instead of enum

```python
# WRONG - protocol must be AgentProtocol enum
container_protocol_versions=[
    ProtocolVersionRecord(protocol="RESPONSES", version="v1")
]
```

#### ❌ INCORRECT: Empty protocol versions list

```python
# WRONG - At least one protocol version required
container_protocol_versions=[]
```

#### ❌ INCORRECT: Missing version parameter

```python
# WRONG - version is required
container_protocol_versions=[
    ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES)
]
```

---

## 5. Resource Allocation Patterns

### 5.1 Correct Resource Specification

#### ✅ CORRECT: String format for CPU and memory

```python
ImageBasedHostedAgentDefinition(
    container_protocol_versions=[...],
    image="...",
    cpu="1",      # String format
    memory="2Gi"  # String format with unit
)
```

#### ✅ CORRECT: Higher resource allocation

```python
ImageBasedHostedAgentDefinition(
    container_protocol_versions=[...],
    image="...",
    cpu="4",
    memory="8Gi"
)
```

### 5.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Numeric values instead of strings

```python
# WRONG - cpu and memory must be strings
ImageBasedHostedAgentDefinition(
    container_protocol_versions=[...],
    image="...",
    cpu=1,        # WRONG - must be string "1"
    memory=2048   # WRONG - must be string "2Gi"
)
```

#### ❌ INCORRECT: Missing unit for memory

```python
# WRONG - memory needs unit suffix (Gi, Mi)
ImageBasedHostedAgentDefinition(
    container_protocol_versions=[...],
    image="...",
    memory="2"  # WRONG - should be "2Gi"
)
```

---

## 6. Tools Configuration Patterns

### 6.1 Correct Tools Specification

#### ✅ CORRECT: Code interpreter tool

```python
tools=[{"type": "code_interpreter"}]
```

#### ✅ CORRECT: Multiple tools

```python
tools=[
    {"type": "code_interpreter"},
    {"type": "file_search"}
]
```

#### ✅ CORRECT: MCP tool with server configuration

```python
tools=[
    {
        "type": "mcp",
        "server_label": "my-mcp-server",
        "server_url": "https://my-mcp-server.example.com"
    }
]
```

### 6.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using CodeInterpreterTool class

```python
# WRONG - tools should be dict format for hosted agents
from azure.ai.agents.models import CodeInterpreterTool

tools=[CodeInterpreterTool()]  # WRONG for hosted agents
```

#### ❌ INCORRECT: String instead of dict

```python
# WRONG - tools must be list of dicts
tools=["code_interpreter"]  # WRONG
```

---

## 7. Environment Variables Patterns

### 7.1 Correct Environment Variables

#### ✅ CORRECT: Using os.environ

```python
environment_variables={
    "AZURE_AI_PROJECT_ENDPOINT": os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    "MODEL_NAME": "gpt-4o-mini"
}
```

### 7.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded secrets

```python
# WRONG - Never hardcode secrets
environment_variables={
    "API_KEY": "sk-1234567890abcdef"  # NEVER DO THIS
}
```

---

## 8. Agent Lifecycle Patterns

### 8.1 Correct Lifecycle Management

#### ✅ CORRECT: List agent versions

```python
versions = client.agents.list_versions(agent_name="my-hosted-agent")
for version in versions:
    print(f"Version: {version.version}, State: {version.state}")
```

#### ✅ CORRECT: Delete agent version

```python
client.agents.delete_version(
    agent_name="my-hosted-agent",
    version=agent.version
)
```

### 8.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using delete_agent instead of delete_version

```python
# WRONG - Use delete_version for hosted agent versions
client.agents.delete_agent(agent_id="wrong-delete-agent")
```

---

## Summary Checklist

Before submitting code using hosted agents, verify:

- [ ] Imports use `azure.ai.projects` (NOT `azure.ai.agents`) for hosted agent models
- [ ] Client is `AIProjectClient` (NOT `AgentsClient`)
- [ ] Uses `create_version` method (NOT `create_agent`)
- [ ] `ImageBasedHostedAgentDefinition` has required `container_protocol_versions`
- [ ] `ImageBasedHostedAgentDefinition` has required `image` parameter
- [ ] `ProtocolVersionRecord` uses `AgentProtocol` enum (NOT string)
- [ ] `cpu` and `memory` are strings with proper units
- [ ] `tools` is a list of dicts (NOT model classes)
- [ ] No hardcoded credentials or secrets
- [ ] Uses `DefaultAzureCredential` for authentication
