# Azure AI Projects SDK Acceptance Criteria

**SDK**: `azure-ai-projects`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 ✅ CORRECT: Client Imports (Sync)
```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
```

### 1.2 ✅ CORRECT: Client Imports (Async)
```python
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
```

### 1.3 ✅ CORRECT: Project-Level Model Imports
```python
from azure.ai.projects.models import (
    # Agent models
    PromptAgentDefinition,
    AgentKind,
    # Connection models
    ConnectionType,
    # Deployment models
    ModelDeployment,
    # Evaluation models
    DataSourceConfigCustom,
    # Dataset/Index models
    DatasetVersion,
    AzureAISearchIndex,
    # Bing grounding (project-level)
    BingGroundingAgentTool,
    BingGroundingSearchToolParameters,
    BingGroundingSearchConfiguration,
    # Azure AI Search (project-level)
    AzureAISearchAgentTool,
    AzureAISearchToolResource,
    AISearchIndexResource,
    AzureAISearchQueryType,
    # Function tool (explicit definition)
    FunctionTool,
)
```

### 1.4 ✅ CORRECT: Low-Level Tool Imports (from azure.ai.agents.models)
```python
from azure.ai.agents.models import (
    # Core tools
    CodeInterpreterTool,
    FileSearchTool,
    FunctionTool,
    ToolSet,
    # File handling
    FilePurpose,
    MessageAttachment,
    # Bing grounding (low-level)
    BingGroundingTool,
    # OpenAPI
    OpenApiTool,
    OpenApiAnonymousAuthDetails,
    # MCP
    McpTool,
    # Multi-agent
    ConnectedAgentTool,
    # Enterprise tools
    SharepointTool,
    FabricTool,
)
```

### 1.5 ✅ CORRECT: Streaming Handler Import
```python
# Sync handler
from azure.ai.agents.models import AgentEventHandler

# Async handler
from azure.ai.agents.aio import AsyncAgentEventHandler
```

### 1.6 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Importing from wrong module
```python
# WRONG - AIProjectClient is not in azure.ai.projects.models
from azure.ai.projects.models import AIProjectClient

# WRONG - tools are in azure.ai.agents.models, not azure.ai.projects
from azure.ai.projects import CodeInterpreterTool

# WRONG - PromptAgentDefinition is in azure.ai.projects.models
from azure.ai.agents.models import PromptAgentDefinition
```

#### ❌ INCORRECT: Using deprecated/non-existent classes
```python
# WRONG - AgentsClient is from azure.ai.agents, not azure.ai.projects
from azure.ai.projects import AgentsClient

# WRONG - These don't exist
from azure.ai.projects.models import Agent, Thread, Message, Run
```

#### ❌ INCORRECT: Mixing async and sync imports
```python
# WRONG - mixing sync client with async credential
from azure.ai.projects import AIProjectClient  # sync
from azure.identity.aio import DefaultAzureCredential  # async - wrong!
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Sync Client with Context Manager
```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import os

project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:
    # Use project_client for all operations
    agent = project_client.agents.create_agent(...)
```

### 2.2 ✅ CORRECT: Async Client with Context Manager
```python
import os
import asyncio
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

async def main():
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(
            endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
            credential=credential,
        ) as client,
    ):
        agent = await client.agents.create_agent(...)

asyncio.run(main())
```

### 2.3 ✅ CORRECT: Get OpenAI Client
```python
# Get OpenAI-compatible client from project
openai_client = project_client.get_openai_client(
    api_version="2024-10-21",
)

# Use for chat completions
response = openai_client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

### 2.4 ✅ CORRECT: Get OpenAI Client with Specific Connection
```python
openai_client = project_client.get_openai_client(
    api_version="2024-10-21",
    connection_name="my-aoai-connection",
)
```

### 2.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong parameter names
```python
# WRONG - using 'url' instead of 'endpoint'
client = AIProjectClient(url=endpoint, credential=cred)

# WRONG - using 'project_endpoint' instead of 'endpoint'
client = AIProjectClient(project_endpoint=endpoint, credential=cred)

# WRONG - using positional arguments
client = AIProjectClient(endpoint, credential)  # Must use keyword args
```

#### ❌ INCORRECT: Not using context manager
```python
# WRONG - client should be used with context manager or explicitly closed
client = AIProjectClient(endpoint=endpoint, credential=credential)
agent = client.agents.create_agent(...)
# Missing: client.close() or using 'with' statement
```

#### ❌ INCORRECT: Mixing sync credential with async client
```python
# WRONG - sync credential with async client
from azure.ai.projects.aio import AIProjectClient
from azure.identity import DefaultAzureCredential  # Should be from azure.identity.aio

async with AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),  # Wrong! Need async credential
):
    ...
```

---

## 3. Agent Operations

### 3.1 ✅ CORRECT: Basic Agent Creation
```python
agent = project_client.agents.create_agent(
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="You are a helpful assistant.",
)
print(f"Created agent, ID: {agent.id}")

# Clean up when done
project_client.agents.delete_agent(agent.id)
```

### 3.2 ✅ CORRECT: Versioned Agent with PromptAgentDefinition
```python
from azure.ai.projects.models import PromptAgentDefinition

agent = project_client.agents.create_version(
    agent_name="customer-support-agent",
    definition=PromptAgentDefinition(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        instructions="You are a customer support specialist.",
        tools=[],  # Add tools as needed
    ),
    version_label="v1.0",
    description="Initial version",
)
print(f"Agent: id={agent.id}, name={agent.name}, version={agent.version}")
```

### 3.3 ✅ CORRECT: Agent with Tools (Versioned)
```python
from azure.ai.agents.models import CodeInterpreterTool, FileSearchTool
from azure.ai.projects.models import PromptAgentDefinition

agent = project_client.agents.create_version(
    agent_name="tool-agent",
    definition=PromptAgentDefinition(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        instructions="You can execute code and search files.",
        tools=[CodeInterpreterTool(), FileSearchTool()],
    ),
)
```

### 3.4 ✅ CORRECT: Agent with JSON Response Format
```python
# JSON mode
agent = project_client.agents.create_agent(
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    name="json-agent",
    instructions="Always respond in JSON format.",
    response_format={"type": "json_object"},
)
```

### 3.5 ✅ CORRECT: Agent with JSON Schema Response Format
```python
agent = project_client.agents.create_agent(
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    name="schema-agent",
    instructions="Respond with weather data.",
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "weather_response",
            "schema": {
                "type": "object",
                "properties": {
                    "temperature": {"type": "number"},
                    "conditions": {"type": "string"},
                    "humidity": {"type": "number"},
                },
                "required": ["temperature", "conditions"],
            },
        },
    },
)
```

### 3.6 ✅ CORRECT: List Agents by Kind
```python
from azure.ai.projects.models import AgentKind

# Filter agents by kind
agents = project_client.agents.list(kind=AgentKind.PROMPT)
for agent in agents:
    print(f"Agent: {agent.name}")
```

### 3.7 ✅ CORRECT: Delete Agent
```python
project_client.agents.delete_agent(agent.id)
```

### 3.8 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing required parameters
```python
# WRONG - missing model parameter
agent = project_client.agents.create_agent(
    name="my-agent",
    instructions="You are helpful.",
)
```

#### ❌ INCORRECT: Using wrong method for versioned agents
```python
# WRONG - create_agent doesn't support versioning
agent = project_client.agents.create_agent(
    model="gpt-4o",
    name="my-agent",
    version_label="v1.0",  # This parameter doesn't exist on create_agent
)

# CORRECT - use create_version for versioned agents
agent = project_client.agents.create_version(
    agent_name="my-agent",
    definition=PromptAgentDefinition(...),
    version_label="v1.0",
)
```

---

## 4. Thread, Message, and Run Operations

### 4.1 ✅ CORRECT: Create Thread
```python
thread = project_client.agents.threads.create()
print(f"Created thread, ID: {thread.id}")
```

### 4.2 ✅ CORRECT: Create Thread with Tool Resources
```python
from azure.ai.agents.models import FileSearchTool

file_search = FileSearchTool(vector_store_ids=[vector_store.id])

thread = project_client.agents.threads.create(
    tool_resources=file_search.resources
)
```

### 4.3 ✅ CORRECT: Create Message
```python
message = project_client.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content="What is the weather in Seattle?",
)
print(f"Created message, ID: {message.id}")
```

### 4.4 ✅ CORRECT: Create Message with Attachment
```python
from azure.ai.agents.models import MessageAttachment, FileSearchTool

attachment = MessageAttachment(
    file_id=file.id,
    tools=FileSearchTool().definitions
)

message = project_client.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content="What feature does Smart Eyewear offer?",
    attachments=[attachment],
)
```

### 4.5 ✅ CORRECT: List Messages
```python
messages = project_client.agents.messages.list(thread_id=thread.id)
for msg in messages:
    print(f"Role: {msg.role}")
    for content in msg.content:
        if hasattr(content, 'text'):
            print(f"Content: {content.text.value}")
```

### 4.6 ✅ CORRECT: Create and Process Run
```python
run = project_client.agents.runs.create_and_process(
    thread_id=thread.id,
    agent_id=agent.id,
)
print(f"Run finished with status: {run.status}")

if run.status == "failed":
    print(f"Run failed: {run.last_error}")
```

### 4.7 ✅ CORRECT: Create and Process Run with ToolSet
```python
from azure.ai.agents.models import FunctionTool, ToolSet

def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: 72F, sunny"

functions = FunctionTool(functions=[get_weather])
toolset = ToolSet()
toolset.add(functions)

# Enable auto function calls
project_client.agents.enable_auto_function_calls(toolset)

run = project_client.agents.runs.create_and_process(
    thread_id=thread.id,
    agent_id=agent.id,
    toolset=toolset,  # Pass toolset for auto-execution
)
```

### 4.8 ✅ CORRECT: Streaming Run with Event Handler
```python
from azure.ai.agents.models import AgentEventHandler

class MyHandler(AgentEventHandler):
    def on_message_delta(self, delta):
        if delta.text:
            print(delta.text.value, end="", flush=True)

    def on_error(self, data):
        print(f"Error: {data}")

with project_client.agents.runs.stream(
    thread_id=thread.id,
    agent_id=agent.id,
    event_handler=MyHandler(),
) as stream:
    stream.until_done()
```

### 4.9 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong role value
```python
# WRONG - role must be "user" for messages from user
message = project_client.agents.messages.create(
    thread_id=thread.id,
    role="human",  # Wrong! Should be "user"
    content="Hello",
)
```

#### ❌ INCORRECT: Not checking run status
```python
# WRONG - not handling failed runs
run = project_client.agents.runs.create_and_process(
    thread_id=thread.id,
    agent_id=agent.id,
)
# Immediately accessing messages without checking status

# CORRECT - always check run status
if run.status == "completed":
    messages = project_client.agents.messages.list(thread_id=thread.id)
elif run.status == "failed":
    print(f"Run failed: {run.last_error}")
```

#### ❌ INCORRECT: Using wrong streaming handler
```python
# WRONG - using sync handler with async client
from azure.ai.agents.models import AgentEventHandler  # This is sync

async with client.agents.runs.stream(...) as stream:  # This is async
    await stream.until_done()

# CORRECT - use AsyncAgentEventHandler with async client
from azure.ai.agents.aio import AsyncAgentEventHandler
```

---

## 5. Connections Operations

### 5.1 ✅ CORRECT: List All Connections
```python
connections = project_client.connections.list()
for conn in connections:
    print(f"Name: {conn.name}")
    print(f"Type: {conn.connection_type}")
    print(f"ID: {conn.id}")
```

### 5.2 ✅ CORRECT: List Connections by Type
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

### 5.3 ✅ CORRECT: Get Connection by Name
```python
connection = project_client.connections.get(connection_name="my-search-connection")
print(f"Name: {connection.name}")
print(f"Type: {connection.connection_type}")
```

### 5.4 ✅ CORRECT: Get Connection with Credentials
```python
connection = project_client.connections.get(
    connection_name="my-search-connection",
    include_credentials=True,
)
print(f"Endpoint: {connection.endpoint_url}")
```

### 5.5 ✅ CORRECT: Get Default Connection
```python
from azure.ai.projects.models import ConnectionType

# Get default Azure OpenAI connection
default_aoai = project_client.connections.get_default(
    connection_type=ConnectionType.AZURE_OPEN_AI
)
print(f"Default Azure OpenAI: {default_aoai.name}")

# Get default with credentials
default_aoai = project_client.connections.get_default(
    connection_type=ConnectionType.AZURE_OPEN_AI,
    include_credentials=True,
)
```

### 5.6 ✅ CORRECT: Available ConnectionType Values
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

### 5.7 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong ConnectionType values
```python
# WRONG - using string instead of enum
connections = project_client.connections.list(connection_type="AzureOpenAI")

# CORRECT - use ConnectionType enum
from azure.ai.projects.models import ConnectionType
connections = project_client.connections.list(
    connection_type=ConnectionType.AZURE_OPEN_AI
)
```

#### ❌ INCORRECT: Using wrong parameter name
```python
# WRONG - parameter is connection_name, not name
connection = project_client.connections.get(name="my-connection")

# CORRECT
connection = project_client.connections.get(connection_name="my-connection")
```

---

## 6. Deployments Operations

### 6.1 ✅ CORRECT: List All Deployments
```python
deployments = project_client.deployments.list()
for deployment in deployments:
    print(f"Name: {deployment.name}")
    print(f"Model: {deployment.model_name}")
    print(f"Publisher: {deployment.model_publisher}")
```

### 6.2 ✅ CORRECT: Filter Deployments by Publisher
```python
# List only OpenAI model deployments
for deployment in project_client.deployments.list(model_publisher="OpenAI"):
    print(f"{deployment.name}: {deployment.model_name}")
```

### 6.3 ✅ CORRECT: Filter Deployments by Model Name
```python
# List deployments of a specific model
for deployment in project_client.deployments.list(model_name="gpt-4o"):
    print(f"{deployment.name}: {deployment.model_version}")
```

### 6.4 ✅ CORRECT: Get Deployment
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

### 6.5 ✅ CORRECT: Dynamic Model Selection
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

### 6.6 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong property access
```python
# WRONG - model property doesn't exist
deployment = project_client.deployments.get("my-deployment")
print(deployment.model)  # Wrong! Use model_name

# CORRECT
print(deployment.model_name)
```

---

## 7. OpenAI Client and Evaluations

### 7.1 ✅ CORRECT: Get OpenAI Client
```python
openai_client = project_client.get_openai_client()
```

### 7.2 ✅ CORRECT: Define Data Source Configuration
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

### 7.3 ✅ CORRECT: Define Testing Criteria (Evaluators)
```python
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

### 7.4 ✅ CORRECT: Create Evaluation
```python
eval_object = openai_client.evals.create(
    name="Agent Quality Evaluation",
    data_source_config=data_source_config,
    testing_criteria=testing_criteria,
)
print(f"Created evaluation: {eval_object.id}")
```

### 7.5 ✅ CORRECT: Run Evaluation
```python
# Define test data
data_source = {
    "type": "azure_ai_target_completions",
    "source": {
        "type": "file_content",
        "content": [
            {"item": {"query": "What is the capital of France?"}},
            {"item": {"query": "How do I reverse a string in Python?"}},
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

# Execute evaluation run
eval_run = openai_client.evals.runs.create(
    eval_id=eval_object.id,
    name=f"Evaluation Run for Agent {agent.name}",
    data_source=data_source,
)
print(f"Evaluation run created: {eval_run.id}")
```

### 7.6 ✅ CORRECT: Built-in Evaluators Reference
```python
# Available built-in evaluators:
# - builtin.violence: Detects violent content
# - builtin.fluency: Measures response fluency
# - builtin.task_adherence: Checks if response follows instructions
# - builtin.groundedness: Checks factual grounding
# - builtin.relevance: Measures response relevance
# - builtin.coherence: Checks logical coherence
# - builtin.similarity: Compares to expected response
```

### 7.7 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Creating evaluation on wrong client
```python
# WRONG - evals are on openai_client, not project_client
eval_object = project_client.evals.create(...)

# CORRECT
openai_client = project_client.get_openai_client()
eval_object = openai_client.evals.create(...)
```

#### ❌ INCORRECT: Wrong data_source_config type
```python
# WRONG - type must be "custom"
data_source_config = DataSourceConfigCustom(
    type="json",  # Wrong!
    item_schema={...},
)

# CORRECT
data_source_config = DataSourceConfigCustom(
    type="custom",
    item_schema={...},
)
```

---

## 8. Tools

### 8.1 ✅ CORRECT: CodeInterpreterTool
```python
from azure.ai.agents.models import CodeInterpreterTool

code_interpreter = CodeInterpreterTool()

agent = project_client.agents.create_agent(
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    name="code-agent",
    instructions="You can execute Python code.",
    tools=code_interpreter.definitions,
    tool_resources=code_interpreter.resources,
)
```

### 8.2 ✅ CORRECT: CodeInterpreterTool with File Upload
```python
from azure.ai.agents.models import CodeInterpreterTool, FilePurpose

# Upload file for code interpreter
file = project_client.agents.files.upload_and_poll(
    file_path="data.csv",
    purpose=FilePurpose.AGENTS,
)

code_interpreter = CodeInterpreterTool()

agent = project_client.agents.create_agent(
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    name="data-agent",
    instructions="Analyze the uploaded data file.",
    tools=code_interpreter.definitions,
    tool_resources={"code_interpreter": {"file_ids": [file.id]}},
)
```

### 8.3 ✅ CORRECT: FileSearchTool with Vector Store
```python
from azure.ai.agents.models import FileSearchTool, FilePurpose

# Upload and create vector store
file = project_client.agents.files.upload_and_poll(
    file_path="./data/product_info.md",
    purpose=FilePurpose.AGENTS,
)
vector_store = project_client.agents.vector_stores.create_and_poll(
    file_ids=[file.id],
    name="product-docs",
)

# Create file search tool
file_search = FileSearchTool(vector_store_ids=[vector_store.id])

agent = project_client.agents.create_agent(
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    name="search-agent",
    instructions="Search uploaded files to answer questions.",
    tools=file_search.definitions,
    tool_resources=file_search.resources,
)
```

### 8.4 ✅ CORRECT: FunctionTool
```python
from azure.ai.agents.models import FunctionTool

def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: Sunny, 72F"

def get_stock_price(symbol: str) -> str:
    """Get current stock price."""
    return f"{symbol}: $150.00"

functions = FunctionTool(functions=[get_weather, get_stock_price])

agent = project_client.agents.create_agent(
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    name="function-agent",
    instructions="Help with weather and stock queries.",
    tools=functions.definitions,
)
```

### 8.5 ✅ CORRECT: FunctionTool with ToolSet and Auto-Execution
```python
from azure.ai.agents.models import FunctionTool, ToolSet

def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: Sunny, 72F"

functions = FunctionTool(functions=[get_weather])
toolset = ToolSet()
toolset.add(functions)

# Enable auto function calls
project_client.agents.enable_auto_function_calls(toolset)

agent = project_client.agents.create_agent(
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    name="auto-function-agent",
    instructions="Help with weather queries.",
    toolset=toolset,
)

# Process run - functions auto-execute
run = project_client.agents.runs.create_and_process(
    thread_id=thread.id,
    agent_id=agent.id,
    toolset=toolset,
)
```

### 8.6 ✅ CORRECT: BingGroundingTool (Low-Level)
```python
from azure.ai.agents.models import BingGroundingTool

conn_id = os.environ["BING_CONNECTION_NAME"]
bing = BingGroundingTool(connection_id=conn_id)

agent = project_client.agents.create_agent(
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    name="bing-agent",
    instructions="Use web search to find current information.",
    tools=bing.definitions,
)
```

### 8.7 ✅ CORRECT: BingGroundingAgentTool (Project-Level)
```python
from azure.ai.projects.models import (
    PromptAgentDefinition,
    BingGroundingAgentTool,
    BingGroundingSearchToolParameters,
    BingGroundingSearchConfiguration,
)

bing_connection = project_client.connections.get(
    os.environ["BING_PROJECT_CONNECTION_NAME"]
)

agent = project_client.agents.create_version(
    agent_name="bing-search-agent",
    definition=PromptAgentDefinition(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        instructions="You are a helpful assistant with web search capabilities.",
        tools=[
            BingGroundingAgentTool(
                bing_grounding=BingGroundingSearchToolParameters(
                    search_configurations=[
                        BingGroundingSearchConfiguration(
                            project_connection_id=bing_connection.id
                        )
                    ]
                )
            )
        ],
    ),
)
```

### 8.8 ✅ CORRECT: AzureAISearchAgentTool (Project-Level)
```python
from azure.ai.projects.models import (
    AzureAISearchAgentTool,
    AzureAISearchToolResource,
    AISearchIndexResource,
    AzureAISearchQueryType,
    PromptAgentDefinition,
)

# Get search connection
search_connection = project_client.connections.get(
    os.environ["AI_SEARCH_PROJECT_CONNECTION_NAME"]
)

agent = project_client.agents.create_version(
    agent_name="enterprise-search-agent",
    definition=PromptAgentDefinition(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        instructions="""You are a helpful assistant. Always provide citations 
        using format: [message_idx:search_idx source].""",
        tools=[
            AzureAISearchAgentTool(
                azure_ai_search=AzureAISearchToolResource(
                    indexes=[
                        AISearchIndexResource(
                            project_connection_id=search_connection.id,
                            index_name=os.environ["AI_SEARCH_INDEX_NAME"],
                            query_type=AzureAISearchQueryType.SIMPLE,
                        ),
                    ]
                )
            )
        ],
    ),
)
```

### 8.9 ✅ CORRECT: AzureAISearchQueryType Values
```python
from azure.ai.projects.models import AzureAISearchQueryType

# Available query types:
# - AzureAISearchQueryType.SIMPLE: Simple keyword search
# - AzureAISearchQueryType.SEMANTIC: Semantic ranking
# - AzureAISearchQueryType.VECTOR: Vector search
# - AzureAISearchQueryType.VECTOR_SIMPLE_HYBRID: Vector + keyword hybrid
# - AzureAISearchQueryType.VECTOR_SEMANTIC_HYBRID: Vector + semantic hybrid
```

### 8.10 ✅ CORRECT: OpenApiTool
```python
from azure.ai.agents.models import OpenApiTool, OpenApiAnonymousAuthDetails

openapi_spec = """
openapi: 3.0.0
info:
  title: Weather API
  version: 1.0.0
paths:
  /weather:
    get:
      summary: Get weather
      parameters:
        - name: location
          in: query
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Weather data
"""

openapi_tool = OpenApiTool(
    name="weather_api",
    spec=openapi_spec,
    description="Get weather information",
    auth=OpenApiAnonymousAuthDetails(),
)

agent = project_client.agents.create_agent(
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    name="api-agent",
    instructions="Use the weather API to get weather data.",
    tools=openapi_tool.definitions,
)
```

### 8.11 ✅ CORRECT: McpTool
```python
from azure.ai.agents.models import McpTool

mcp_tool = McpTool(
    server_label="my-mcp-server",
    server_url="http://localhost:3000",
    allowed_tools=["search", "calculate"],
)

agent = project_client.agents.create_agent(
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    name="mcp-agent",
    instructions="Use MCP tools for specialized operations.",
    tools=mcp_tool.definitions,
)
```

### 8.12 ✅ CORRECT: ConnectedAgentTool
```python
from azure.ai.agents.models import ConnectedAgentTool

# Connect to another agent
connected_agent = ConnectedAgentTool(
    agent_id=other_agent.id,
    name="specialist-agent",
    description="A specialist agent for complex queries",
)

orchestrator = project_client.agents.create_agent(
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    name="orchestrator",
    instructions="Delegate complex tasks to the specialist agent.",
    tools=connected_agent.definitions,
)
```

### 8.13 ✅ CORRECT: ToolSet with Multiple Tools
```python
from azure.ai.agents.models import ToolSet, FunctionTool, CodeInterpreterTool

def my_function(x: int) -> int:
    """Double a number."""
    return x * 2

toolset = ToolSet()
toolset.add(FunctionTool(functions=[my_function]))
toolset.add(CodeInterpreterTool())

# Enable auto function calls
project_client.agents.enable_auto_function_calls(toolset)

agent = project_client.agents.create_agent(
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    name="multi-tool-agent",
    instructions="You have multiple tools available.",
    toolset=toolset,
)

# Pass toolset to run for auto-execution
run = project_client.agents.runs.create_and_process(
    thread_id=thread.id,
    agent_id=agent.id,
    toolset=toolset,
)
```

### 8.14 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong tool import path
```python
# WRONG - CodeInterpreterTool is in azure.ai.agents.models
from azure.ai.projects.models import CodeInterpreterTool

# CORRECT
from azure.ai.agents.models import CodeInterpreterTool
```

#### ❌ INCORRECT: Missing tool_resources for File Search
```python
# WRONG - FileSearchTool requires tool_resources
agent = project_client.agents.create_agent(
    model=model,
    name="search-agent",
    tools=file_search.definitions,
    # Missing: tool_resources=file_search.resources
)

# CORRECT
agent = project_client.agents.create_agent(
    model=model,
    name="search-agent",
    tools=file_search.definitions,
    tool_resources=file_search.resources,  # Required!
)
```

#### ❌ INCORRECT: Passing FunctionTool object instead of definitions
```python
# WRONG - pass .definitions, not the tool object
functions = FunctionTool(functions=[my_func])
agent = project_client.agents.create_agent(
    model=model,
    tools=functions,  # Wrong! Should be functions.definitions
)

# CORRECT
agent = project_client.agents.create_agent(
    model=model,
    tools=functions.definitions,
)
```

---

## 9. Async Patterns

### 9.1 ✅ CORRECT: Async Client Setup
```python
import os
import asyncio
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

# Requires: pip install aiohttp

async def main():
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(
            endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
            credential=credential,
        ) as client,
    ):
        # Use async operations
        agent = await client.agents.create_agent(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            name="async-agent",
            instructions="You are helpful.",
        )
        print(f"Created agent: {agent.id}")
        
        # Clean up
        await client.agents.delete_agent(agent.id)

asyncio.run(main())
```

### 9.2 ✅ CORRECT: Async Full Conversation Flow
```python
import os
import asyncio
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

async def async_conversation():
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(
            endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
            credential=credential,
        ) as client,
    ):
        # Create agent
        agent = await client.agents.create_agent(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            name="async-agent",
            instructions="You are a helpful assistant.",
        )
        
        # Create thread
        thread = await client.agents.threads.create()
        
        # Add message
        await client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content="What is the capital of Japan?",
        )
        
        # Create and process run
        run = await client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id,
        )
        
        # Get messages
        if run.status == "completed":
            messages = await client.agents.messages.list(thread_id=thread.id)
            async for msg in messages:
                if msg.role == "assistant":
                    print(f"Response: {msg.content[0].text.value}")
        
        # Clean up
        await client.agents.delete_agent(agent.id)

asyncio.run(async_conversation())
```

### 9.3 ✅ CORRECT: Async Iteration over Connections/Deployments
```python
async with AIProjectClient(...) as client:
    # List connections
    connections = client.connections.list()
    async for conn in connections:
        print(f"Connection: {conn.name}")
    
    # List deployments
    deployments = client.deployments.list()
    async for deployment in deployments:
        print(f"Deployment: {deployment.name}")
```

### 9.4 ✅ CORRECT: Async Streaming with AsyncAgentEventHandler
```python
from azure.ai.agents.aio import AsyncAgentEventHandler

class AsyncHandler(AsyncAgentEventHandler):
    async def on_message_delta(self, delta):
        if delta.text:
            print(delta.text.value, end="", flush=True)
    
    async def on_error(self, data):
        print(f"Error: {data}")

async with AIProjectClient(...) as client:
    async with client.agents.runs.stream(
        thread_id=thread.id,
        agent_id=agent.id,
        event_handler=AsyncHandler(),
    ) as stream:
        await stream.until_done()
```

### 9.5 ✅ CORRECT: Concurrent Operations with asyncio.gather
```python
import asyncio

async def process_multiple_queries(client, agent_id, queries):
    """Process multiple queries concurrently."""
    
    async def process_query(query):
        thread = await client.agents.threads.create()
        await client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=query,
        )
        run = await client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent_id,
        )
        if run.status == "completed":
            messages = await client.agents.messages.list(thread_id=thread.id)
            async for msg in messages:
                if msg.role == "assistant":
                    return msg.content[0].text.value
        return None
    
    # Process all queries concurrently
    results = await asyncio.gather(*[process_query(q) for q in queries])
    return results

# Usage
async with AIProjectClient(...) as client:
    queries = ["What is Python?", "What is JavaScript?", "What is Rust?"]
    results = await process_multiple_queries(client, agent.id, queries)
```

### 9.6 ✅ CORRECT: Async Error Handling
```python
from azure.core.exceptions import HttpResponseError

async with AIProjectClient(...) as client:
    try:
        agent = await client.agents.create_agent(...)
    except HttpResponseError as e:
        print(f"HTTP Error: {e.status_code}")
        print(f"Message: {e.message}")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

### 9.7 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using sync credential with async client
```python
# WRONG - sync credential with async client
from azure.ai.projects.aio import AIProjectClient
from azure.identity import DefaultAzureCredential  # Should be from azure.identity.aio

async with AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),  # Wrong!
) as client:
    ...
```

#### ❌ INCORRECT: Forgetting await
```python
# WRONG - missing await
async with AIProjectClient(...) as client:
    agent = client.agents.create_agent(...)  # Missing await!
    
# CORRECT
async with AIProjectClient(...) as client:
    agent = await client.agents.create_agent(...)
```

#### ❌ INCORRECT: Using sync handler with async client
```python
# WRONG - using sync AgentEventHandler with async client
from azure.ai.agents.models import AgentEventHandler  # This is sync!

async with client.agents.runs.stream(
    thread_id=thread.id,
    agent_id=agent.id,
    event_handler=AgentEventHandler(),  # Wrong!
) as stream:
    await stream.until_done()

# CORRECT - use AsyncAgentEventHandler
from azure.ai.agents.aio import AsyncAgentEventHandler
```

---

## 10. Datasets and Indexes

### 10.1 ✅ CORRECT: Upload Dataset File
```python
from azure.ai.projects.models import DatasetVersion

dataset = project_client.datasets.upload_file(
    name="my-dataset",
    version="1.0",
    file_path="./data/training_data.csv",
    connection_name="my-storage-connection",
)
print(f"Dataset uploaded: {dataset.name} v{dataset.version}")
```

### 10.2 ✅ CORRECT: Upload Dataset Folder
```python
import re
from azure.ai.projects.models import DatasetVersion

dataset = project_client.datasets.upload_folder(
    name="document-collection",
    version="2.0",
    folder="./data/documents/",
    connection_name="my-storage-connection",
    file_pattern=re.compile(r"\.(txt|csv|md|json)$", re.IGNORECASE),
)
print(f"Folder uploaded: {dataset.name} v{dataset.version}")
```

### 10.3 ✅ CORRECT: Get Dataset
```python
dataset = project_client.datasets.get(name="my-dataset", version="1.0")
print(f"Name: {dataset.name}")
print(f"Version: {dataset.version}")
```

### 10.4 ✅ CORRECT: Get Dataset Credentials
```python
credentials = project_client.datasets.get_credentials(
    name="my-dataset",
    version="1.0",
)
# Use credentials to access dataset storage
```

### 10.5 ✅ CORRECT: List Datasets
```python
# List all datasets
for dataset in project_client.datasets.list():
    print(f"{dataset.name}: {dataset.version}")

# List versions of a specific dataset
for dataset in project_client.datasets.list_versions(name="my-dataset"):
    print(f"Version: {dataset.version}")
```

### 10.6 ✅ CORRECT: Delete Dataset
```python
project_client.datasets.delete(name="my-dataset", version="1.0")
```

### 10.7 ✅ CORRECT: Create or Update Index
```python
from azure.ai.projects.models import AzureAISearchIndex

index = project_client.indexes.create_or_update(
    name="my-index",
    version="1.0",
    index=AzureAISearchIndex(
        connection_name="my-ai-search-connection",
        index_name="products-index",
    ),
)
print(f"Index created: {index.name} v{index.version}")
```

### 10.8 ✅ CORRECT: Get Index
```python
index = project_client.indexes.get(name="my-index", version="1.0")
print(f"Name: {index.name}")
print(f"Version: {index.version}")
```

### 10.9 ✅ CORRECT: List Indexes
```python
# List all indexes
for index in project_client.indexes.list():
    print(f"{index.name}: {index.version}")

# List versions of a specific index
for index in project_client.indexes.list_versions(name="my-index"):
    print(f"Version: {index.version}")
```

### 10.10 ✅ CORRECT: Delete Index
```python
project_client.indexes.delete(name="my-index", version="1.0")
```

### 10.11 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing version parameter
```python
# WRONG - version is required
dataset = project_client.datasets.upload_file(
    name="my-dataset",
    file_path="./data.csv",
    connection_name="storage",
)

# CORRECT
dataset = project_client.datasets.upload_file(
    name="my-dataset",
    version="1.0",  # Required!
    file_path="./data.csv",
    connection_name="storage",
)
```

#### ❌ INCORRECT: Using wrong parameter name for folders
```python
# WRONG - parameter is folder, not folder_path
dataset = project_client.datasets.upload_folder(
    name="docs",
    version="1.0",
    folder_path="./docs/",  # Wrong! Should be folder
    connection_name="storage",
)

# CORRECT
dataset = project_client.datasets.upload_folder(
    name="docs",
    version="1.0",
    folder="./docs/",  # Correct parameter name
    connection_name="storage",
)
```

---

## 11. File and Vector Store Operations

### 11.1 ✅ CORRECT: Upload File
```python
from azure.ai.agents.models import FilePurpose

file = project_client.agents.files.upload_and_poll(
    file_path="./data/document.pdf",
    purpose=FilePurpose.AGENTS,
)
print(f"Uploaded file, ID: {file.id}")
```

### 11.2 ✅ CORRECT: Create Vector Store
```python
vector_store = project_client.agents.vector_stores.create_and_poll(
    file_ids=[file.id],
    name="my-vector-store",
)
print(f"Created vector store, ID: {vector_store.id}")
```

### 11.3 ✅ CORRECT: File with Code Interpreter
```python
from azure.ai.agents.models import FilePurpose, CodeInterpreterTool

file = project_client.agents.files.upload_and_poll(
    file_path="data.csv",
    purpose=FilePurpose.AGENTS,
)

code_interpreter = CodeInterpreterTool()

agent = project_client.agents.create_agent(
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    name="data-agent",
    instructions="Analyze the data.",
    tools=code_interpreter.definitions,
    tool_resources={"code_interpreter": {"file_ids": [file.id]}},
)
```

### 11.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong FilePurpose
```python
# WRONG - FilePurpose.ASSISTANTS doesn't exist
from azure.ai.agents.models import FilePurpose

file = project_client.agents.files.upload_and_poll(
    file_path="doc.pdf",
    purpose=FilePurpose.ASSISTANTS,  # Wrong!
)

# CORRECT - use FilePurpose.AGENTS
file = project_client.agents.files.upload_and_poll(
    file_path="doc.pdf",
    purpose=FilePurpose.AGENTS,
)
```

#### ❌ INCORRECT: Missing purpose parameter
```python
# WRONG - purpose is required
file = project_client.agents.files.upload_and_poll(
    file_path="doc.pdf",
)

# CORRECT
from azure.ai.agents.models import FilePurpose

file = project_client.agents.files.upload_and_poll(
    file_path="doc.pdf",
    purpose=FilePurpose.AGENTS,
)
```

---

## 12. Complete Example: Full Workflow

### 12.1 ✅ CORRECT: Complete Agent Workflow
```python
import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.ai.agents.models import CodeInterpreterTool, FilePurpose
from azure.identity import DefaultAzureCredential

# Setup
project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:
    # Upload file
    file = project_client.agents.files.upload_and_poll(
        file_path="./data/sales_data.csv",
        purpose=FilePurpose.AGENTS,
    )
    
    # Create agent with code interpreter
    code_interpreter = CodeInterpreterTool()
    
    agent = project_client.agents.create_version(
        agent_name="data-analyst",
        definition=PromptAgentDefinition(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            instructions="You are a data analyst. Analyze CSV data and provide insights.",
            tools=[code_interpreter],
            tool_resources={"code_interpreter": {"file_ids": [file.id]}},
        ),
        version_label="v1.0",
    )
    
    # Create thread and add message
    thread = project_client.agents.threads.create()
    project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content="Analyze the sales data and create a summary with key insights.",
    )
    
    # Run agent
    run = project_client.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id,
    )
    
    # Get response
    if run.status == "completed":
        messages = project_client.agents.messages.list(thread_id=thread.id)
        for msg in messages:
            if msg.role == "assistant":
                for content in msg.content:
                    if hasattr(content, 'text'):
                        print(content.text.value)
    elif run.status == "failed":
        print(f"Run failed: {run.last_error}")
    
    # Clean up
    project_client.agents.delete_agent(agent.id)
```

---

## Quick Reference Tables

### Import Sources

| Import | Source |
|--------|--------|
| `AIProjectClient` | `azure.ai.projects` (sync) / `azure.ai.projects.aio` (async) |
| `PromptAgentDefinition`, `ConnectionType`, `ModelDeployment`, `DataSourceConfigCustom` | `azure.ai.projects.models` |
| `BingGroundingAgentTool`, `AzureAISearchAgentTool` | `azure.ai.projects.models` |
| `CodeInterpreterTool`, `FileSearchTool`, `FunctionTool`, `ToolSet` | `azure.ai.agents.models` |
| `BingGroundingTool` (low-level), `OpenApiTool`, `McpTool` | `azure.ai.agents.models` |
| `AgentEventHandler` | `azure.ai.agents.models` (sync) / `azure.ai.agents.aio` (async) |
| `DefaultAzureCredential` | `azure.identity` (sync) / `azure.identity.aio` (async) |

### Client Access Patterns

| Operation | Access Path |
|-----------|-------------|
| Agent operations | `project_client.agents.create_agent()`, `project_client.agents.create_version()` |
| Thread operations | `project_client.agents.threads.create()` |
| Message operations | `project_client.agents.messages.create()` |
| Run operations | `project_client.agents.runs.create_and_process()`, `project_client.agents.runs.stream()` |
| File operations | `project_client.agents.files.upload_and_poll()` |
| Vector store operations | `project_client.agents.vector_stores.create_and_poll()` |
| Connection operations | `project_client.connections.list()`, `project_client.connections.get()` |
| Deployment operations | `project_client.deployments.list()`, `project_client.deployments.get()` |
| Dataset operations | `project_client.datasets.upload_file()`, `project_client.datasets.list()` |
| Index operations | `project_client.indexes.create_or_update()`, `project_client.indexes.list()` |
| OpenAI client | `project_client.get_openai_client()` |
| Evaluations | `openai_client.evals.create()`, `openai_client.evals.runs.create()` |

### Key Differences: azure-ai-projects vs azure-ai-agents

| Aspect | azure-ai-agents | azure-ai-projects |
|--------|-----------------|-------------------|
| Package | `azure-ai-agents` | `azure-ai-projects` |
| Client | `AgentsClient` | `AIProjectClient` |
| Agent access | Direct on client | Via `client.agents` property |
| Versioned agents | Not available | `create_version()` with `PromptAgentDefinition` |
| Connections | Not available | `client.connections` |
| Deployments | Not available | `client.deployments` |
| Datasets/Indexes | Not available | `client.datasets`, `client.indexes` |
| OpenAI client | Not available | `client.get_openai_client()` |
| Evaluations | Not available | Via OpenAI client `evals` API |
