# Azure AI Agents SDK Acceptance Criteria

**SDK**: `azure-ai-agents`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Commit**: `e7b5fa81aa188011fb4323382d1a32b32f54d55b`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Sync Client via AIProjectClient (Recommended)
```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
```

#### ✅ CORRECT: Async Client via AIProjectClient
```python
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
```

#### ✅ CORRECT: Direct AgentsClient (Alternative)
```python
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential
```

#### ✅ CORRECT: Direct Async AgentsClient
```python
from azure.ai.agents.aio import AgentsClient
from azure.identity.aio import DefaultAzureCredential
```

### 1.2 Model Imports

#### ✅ CORRECT: Tool Classes
```python
from azure.ai.agents.models import (
    FunctionTool,
    AsyncFunctionTool,
    ToolSet,
    CodeInterpreterTool,
    FileSearchTool,
    AzureAISearchTool,
    BingGroundingTool,
    BingCustomSearchTool,
    McpTool,
    OpenApiTool,
    ConnectedAgentTool,
    AzureFunctionTool,
    SharepointTool,
    FabricTool,
    DeepResearchTool,
    BrowserAutomationTool,
    ComputerUseTool,
)
```

#### ✅ CORRECT: Options & Enums
```python
from azure.ai.agents.models import (
    AgentThreadCreationOptions,
    ThreadMessageOptions,
    ListSortOrder,
    FilePurpose,
    MessageRole,
    RunStatus,
)
```

#### ✅ CORRECT: Function Calling Models
```python
from azure.ai.agents.models import (
    RequiredFunctionToolCall,
    SubmitToolOutputsAction,
    ToolOutput,
    FunctionDefinition,
)
```

#### ✅ CORRECT: Streaming Models
```python
from azure.ai.agents.models import (
    AgentEventHandler,
    AgentStreamEvent,
    MessageDeltaChunk,
    ThreadMessage,
    ThreadRun,
    RunStep,
    RunStepDeltaChunk,
)
```

#### ✅ CORRECT: MCP Tool Models
```python
from azure.ai.agents.models import (
    McpTool,
    RequiredMcpToolCall,
    SubmitToolApprovalAction,
    ToolApproval,
)
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Importing from wrong module
```python
# WRONG - FunctionTool is not in azure.ai.agents directly
from azure.ai.agents import FunctionTool

# WRONG - AgentEventHandler is in models
from azure.ai.agents import AgentEventHandler

# WRONG - Old/non-existent import paths
from azure.ai.agents.tools import FunctionTool
from azure.ai.projects.agents import AgentsClient
```

#### ❌ INCORRECT: Using deprecated/non-existent classes
```python
# WRONG - These don't exist
from azure.ai.agents.models import Agent, Thread, Message, Run
# CORRECT equivalents:
# Agent response is just a dict-like object
# ThreadMessage, ThreadRun are the correct types
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Via AIProjectClient (Recommended)
```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:
    agents_client = project_client.agents
    # Use agents_client for all operations
```

### 2.2 ✅ CORRECT: Async with AIProjectClient
```python
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

async with project_client:
    agents_client = project_client.agents
    agent = await agents_client.create_agent(...)
```

### 2.3 ✅ CORRECT: Direct AgentsClient
```python
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with agents_client:
    agent = agents_client.create_agent(...)
```

### 2.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong parameter names
```python
# WRONG - using 'url' instead of 'endpoint'
client = AIProjectClient(url=endpoint, credential=cred)

# WRONG - using 'project_endpoint' instead of 'endpoint'
client = AIProjectClient(project_endpoint=endpoint, credential=cred)
```

#### ❌ INCORRECT: Not using context manager
```python
# WRONG - client should be used with context manager or explicitly closed
client = AIProjectClient(endpoint=endpoint, credential=credential)
agents_client = client.agents
agent = agents_client.create_agent(...)
# Missing: client.close() or using 'with' statement
```

#### ❌ INCORRECT: Mixing sync and async
```python
# WRONG - using sync credential with async client
from azure.ai.projects.aio import AIProjectClient
from azure.identity import DefaultAzureCredential  # Should be from azure.identity.aio

async with AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential()):
    ...
```

---

## 3. Agent Creation Patterns

### 3.1 ✅ CORRECT: Basic Agent
```python
agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="You are a helpful assistant",
)
```

### 3.2 ✅ CORRECT: Agent with Function Tools
```python
from azure.ai.agents.models import FunctionTool

def my_function(param: str) -> str:
    """Description of function.
    :param param: Description of param.
    :return: Result
    :rtype: str
    """
    return json.dumps({"result": param})

functions = FunctionTool(functions={my_function})

agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="You are helpful",
    tools=functions.definitions,  # Pass .definitions, not the FunctionTool object
)
```

### 3.3 ✅ CORRECT: Agent with ToolSet
```python
from azure.ai.agents.models import FunctionTool, CodeInterpreterTool, ToolSet

functions = FunctionTool({func1, func2})
code_interpreter = CodeInterpreterTool()

toolset = ToolSet()
toolset.add(functions)
toolset.add(code_interpreter)

agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="You are helpful",
    toolset=toolset,  # Pass toolset, SDK handles definitions
)
```

### 3.4 ✅ CORRECT: Agent with Code Interpreter
```python
from azure.ai.agents.models import CodeInterpreterTool, FilePurpose

# Upload file first
file = agents_client.files.upload_and_poll(
    file_path="data.csv",
    purpose=FilePurpose.AGENTS
)

code_interpreter = CodeInterpreterTool(file_ids=[file.id])

agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="You are helpful",
    tools=code_interpreter.definitions,
    tool_resources=code_interpreter.resources,  # Required for code interpreter
)
```

### 3.5 ✅ CORRECT: Agent with File Search
```python
from azure.ai.agents.models import FileSearchTool, FilePurpose

# Upload file and create vector store
file = agents_client.files.upload_and_poll(
    file_path="document.md",
    purpose=FilePurpose.AGENTS
)
vector_store = agents_client.vector_stores.create_and_poll(
    file_ids=[file.id],
    name="my_vectorstore"
)

file_search = FileSearchTool(vector_store_ids=[vector_store.id])

agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="Search uploaded files",
    tools=file_search.definitions,
    tool_resources=file_search.resources,  # Required for file search
)
```

### 3.6 ✅ CORRECT: Agent with Azure AI Search
```python
from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType
from azure.ai.projects.models import ConnectionType

# Get connection ID from project
conn_id = project_client.connections.get_default(ConnectionType.AZURE_AI_SEARCH).id

ai_search = AzureAISearchTool(
    index_connection_id=conn_id,
    index_name="sample_index",
    query_type=AzureAISearchQueryType.SIMPLE,  # or SEMANTIC, VECTOR, HYBRID
    top_k=3,
    filter="",
)

agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="You are helpful",
    tools=ai_search.definitions,
    tool_resources=ai_search.resources,
)
```

### 3.7 ✅ CORRECT: Agent with Bing Grounding
```python
from azure.ai.agents.models import BingGroundingTool

conn_id = project_client.connections.get(os.environ["BING_CONNECTION_NAME"]).id

bing = BingGroundingTool(connection_id=conn_id)

agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="You are helpful",
    tools=bing.definitions,
)
```

### 3.8 ✅ CORRECT: Agent with MCP Tool
```python
from azure.ai.agents.models import McpTool

mcp_tool = McpTool(
    server_label="my-mcp",
    server_url="https://mcp.example.com",
    allowed_tools=[],  # Optional: specify allowed tools
)

# Dynamically allow/disallow tools
mcp_tool.allow_tool("search_tool")
mcp_tool.disallow_tool("dangerous_tool")

agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="Use MCP tools",
    tools=mcp_tool.definitions,
)
```

### 3.9 ✅ CORRECT: Agent with OpenAPI Tool
```python
from azure.ai.agents.models import OpenApiTool, OpenApiAnonymousAuthDetails
import jsonref

with open("openapi_spec.json", "r") as f:
    openapi_spec = jsonref.loads(f.read())

auth = OpenApiAnonymousAuthDetails()

openapi_tool = OpenApiTool(
    name="weather_api",
    spec=openapi_spec,
    description="Get weather information",
    auth=auth
)

# Add additional definitions
openapi_tool.add_definition(
    name="another_api",
    spec=another_spec,
    description="Another API",
    auth=auth
)

agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="You are helpful",
    tools=openapi_tool.definitions,
)
```

### 3.10 ✅ CORRECT: Agent with Connected Agent
```python
from azure.ai.agents.models import ConnectedAgentTool

# First create the sub-agent
sub_agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="specialist-agent",
    instructions="You are a specialist",
)

# Create connected agent tool
connected_agent = ConnectedAgentTool(
    id=sub_agent.id,
    name="specialist-agent",
    description="A specialist for specific tasks"
)

# Create main agent with connected agent tool
main_agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="main-agent",
    instructions="Delegate to specialists",
    tools=connected_agent.definitions,
)
```

### 3.11 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Passing FunctionTool directly instead of definitions
```python
# WRONG
functions = FunctionTool({my_func})
agent = agents_client.create_agent(
    model=model,
    tools=functions,  # WRONG - should be functions.definitions
)

# CORRECT
agent = agents_client.create_agent(
    model=model,
    tools=functions.definitions,
)
```

#### ❌ INCORRECT: Missing tool_resources for file-based tools
```python
# WRONG - code interpreter needs tool_resources
code_interpreter = CodeInterpreterTool(file_ids=[file.id])
agent = agents_client.create_agent(
    model=model,
    tools=code_interpreter.definitions,
    # Missing: tool_resources=code_interpreter.resources
)
```

#### ❌ INCORRECT: Wrong function signature for FunctionTool
```python
# WRONG - functions must return JSON strings
def bad_function(param: str) -> dict:  # Should return str
    return {"result": param}  # Should return json.dumps({"result": param})

# WRONG - no docstring (SDK uses it for description)
def no_docs(param: str) -> str:
    return json.dumps({"result": param})

# CORRECT
def good_function(param: str) -> str:
    """Description for the AI model.
    :param param: Description of param.
    :return: Result
    :rtype: str
    """
    return json.dumps({"result": param})
```

---

## 4. Thread & Message Patterns

### 4.1 ✅ CORRECT: Create Thread and Message
```python
thread = agents_client.threads.create()

message = agents_client.messages.create(
    thread_id=thread.id,
    role="user",  # or MessageRole.USER
    content="Hello, help me with something",
)
```

### 4.2 ✅ CORRECT: Async Thread and Message
```python
thread = await agents_client.threads.create()

message = await agents_client.messages.create(
    thread_id=thread.id,
    role="user",
    content="Hello",
)
```

### 4.3 ✅ CORRECT: List Messages
```python
from azure.ai.agents.models import ListSortOrder

messages = agents_client.messages.list(
    thread_id=thread.id,
    order=ListSortOrder.ASCENDING  # or DESCENDING
)

for msg in messages:
    if msg.text_messages:
        last_text = msg.text_messages[-1]
        print(f"{msg.role}: {last_text.text.value}")
```

### 4.4 ✅ CORRECT: Get Last Message by Role
```python
from azure.ai.agents.models import MessageRole

# Get last text message from agent
last_msg = agents_client.messages.get_last_message_text_by_role(
    thread_id=thread.id,
    role=MessageRole.AGENT
)
if last_msg:
    print(last_msg.text.value)

# Or get full message
response_message = agents_client.messages.get_last_message_by_role(
    thread_id=thread.id,
    role=MessageRole.AGENT
)
```

### 4.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong role values
```python
# WRONG - role should be "user" or "assistant" or MessageRole enum
message = agents_client.messages.create(
    thread_id=thread.id,
    role="agent",  # WRONG - should be "user" or use MessageRole.USER
    content="Hello",
)
```

#### ❌ INCORRECT: Accessing message content directly
```python
# WRONG - messages have structured content
for msg in messages:
    print(msg.content)  # WRONG - content is a list of content objects

# CORRECT
for msg in messages:
    if msg.text_messages:
        last_text = msg.text_messages[-1]
        print(last_text.text.value)
```

---

## 5. Run Execution Patterns

### 5.1 ✅ CORRECT: Manual Polling
```python
import time

run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)

while run.status in ["queued", "in_progress", "requires_action"]:
    time.sleep(1)
    run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)

if run.status == "failed":
    print(f"Run failed: {run.last_error}")
elif run.status == "completed":
    print("Run completed successfully")
```

### 5.2 ✅ CORRECT: Auto-Polling with create_and_process
```python
run = agents_client.runs.create_and_process(
    thread_id=thread.id,
    agent_id=agent.id
)

if run.status == "failed":
    print(f"Run failed: {run.last_error}")
```

### 5.3 ✅ CORRECT: Combined Thread and Run
```python
from azure.ai.agents.models import AgentThreadCreationOptions, ThreadMessageOptions

run = agents_client.create_thread_and_process_run(
    agent_id=agent.id,
    thread=AgentThreadCreationOptions(
        messages=[
            ThreadMessageOptions(role="user", content="Hello, tell me a joke")
        ]
    ),
)

# Access thread_id from run
thread_id = run.thread_id
```

### 5.4 ✅ CORRECT: Enable Auto Function Calls
```python
from azure.ai.agents.models import FunctionTool

functions = FunctionTool({my_func1, my_func2})

# Enable auto function calling - SDK handles tool execution
agents_client.enable_auto_function_calls(functions)
# Or with set of functions directly:
# agents_client.enable_auto_function_calls({my_func1, my_func2})
# Or with ToolSet:
# agents_client.enable_auto_function_calls(toolset)

agent = agents_client.create_agent(
    model=model,
    tools=functions.definitions,
)

# Now runs will auto-execute function calls
run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
```

### 5.5 ✅ CORRECT: Manual Tool Output Submission
```python
from azure.ai.agents.models import (
    RequiredFunctionToolCall,
    SubmitToolOutputsAction,
    ToolOutput,
)

run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)

while run.status in ["queued", "in_progress", "requires_action"]:
    time.sleep(1)
    run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)

    if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []
        
        for tool_call in tool_calls:
            if isinstance(tool_call, RequiredFunctionToolCall):
                try:
                    output = functions.execute(tool_call)  # FunctionTool.execute()
                    tool_outputs.append(
                        ToolOutput(tool_call_id=tool_call.id, output=output)
                    )
                except Exception as e:
                    print(f"Error: {e}")
        
        if tool_outputs:
            agents_client.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
```

### 5.6 ✅ CORRECT: MCP Tool Approval Handling
```python
from azure.ai.agents.models import (
    McpTool,
    RequiredMcpToolCall,
    SubmitToolApprovalAction,
    ToolApproval,
)

mcp_tool = McpTool(server_label="my-mcp", server_url="https://...")

run = agents_client.runs.create(
    thread_id=thread.id,
    agent_id=agent.id,
    tool_resources=mcp_tool.resources
)

while run.status in ["queued", "in_progress", "requires_action"]:
    time.sleep(1)
    run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)

    if run.status == "requires_action" and isinstance(run.required_action, SubmitToolApprovalAction):
        tool_calls = run.required_action.submit_tool_approval.tool_calls
        tool_approvals = []
        
        for tool_call in tool_calls:
            if isinstance(tool_call, RequiredMcpToolCall):
                tool_approvals.append(
                    ToolApproval(
                        tool_call_id=tool_call.id,
                        approve=True,
                        headers=mcp_tool.headers,
                    )
                )
        
        if tool_approvals:
            agents_client.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_approvals=tool_approvals
            )
```

### 5.7 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not checking run status
```python
# WRONG - not handling failure
run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
messages = agents_client.messages.list(thread_id=thread.id)  # May fail if run failed

# CORRECT
run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
if run.status == "failed":
    print(f"Run failed: {run.last_error}")
else:
    messages = agents_client.messages.list(thread_id=thread.id)
```

#### ❌ INCORRECT: Wrong status values in polling
```python
# WRONG - missing "requires_action"
while run.status in ["queued", "in_progress"]:  # Missing requires_action
    time.sleep(1)
    run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)

# CORRECT - include all non-terminal states
while run.status in ["queued", "in_progress", "requires_action"]:
    ...
```

#### ❌ INCORRECT: Not handling tool calls when requires_action
```python
# WRONG - polling without handling requires_action
while run.status in ["queued", "in_progress", "requires_action"]:
    time.sleep(1)
    run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)
    # Missing: check for requires_action and submit tool outputs
```

---

## 6. Streaming Patterns

### 6.1 ✅ CORRECT: Basic Streaming with Context Manager
```python
with agents_client.runs.stream(thread_id=thread.id, agent_id=agent.id) as stream:
    for event_type, event_data, func_return in stream:
        if isinstance(event_data, MessageDeltaChunk):
            print(f"Text: {event_data.text}")
        elif isinstance(event_data, ThreadRun):
            print(f"Status: {event_data.status}")
```

### 6.2 ✅ CORRECT: Streaming with Event Handler
```python
from azure.ai.agents.models import (
    AgentEventHandler,
    MessageDeltaChunk,
    ThreadMessage,
    ThreadRun,
    RunStep,
)
from typing import Optional

class MyEventHandler(AgentEventHandler[str]):
    def on_message_delta(self, delta: MessageDeltaChunk) -> Optional[str]:
        return f"Text: {delta.text}"

    def on_thread_message(self, message: ThreadMessage) -> Optional[str]:
        return f"Message ID: {message.id}"

    def on_thread_run(self, run: ThreadRun) -> Optional[str]:
        return f"Run status: {run.status}"

    def on_run_step(self, step: RunStep) -> Optional[str]:
        return f"Step: {step.type}"

    def on_error(self, data: str) -> Optional[str]:
        return f"Error: {data}"

    def on_done(self) -> Optional[str]:
        return "Completed"

with agents_client.runs.stream(
    thread_id=thread.id,
    agent_id=agent.id,
    event_handler=MyEventHandler()
) as stream:
    for event_type, event_data, func_return in stream:
        if func_return:
            print(func_return)
```

### 6.3 ✅ CORRECT: Streaming with Function Tool Handling
```python
from azure.ai.agents.models import (
    AgentStreamEvent,
    MessageDeltaChunk,
    ThreadRun,
    SubmitToolOutputsAction,
    RequiredFunctionToolCall,
    ToolOutput,
)

with agents_client.runs.stream(thread_id=thread.id, agent_id=agent.id) as stream:
    for event_type, event_data, _ in stream:
        if isinstance(event_data, MessageDeltaChunk):
            print(event_data.text, end="")
        
        elif isinstance(event_data, ThreadRun):
            if event_data.status == "requires_action" and isinstance(
                event_data.required_action, SubmitToolOutputsAction
            ):
                tool_calls = event_data.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                
                for tool_call in tool_calls:
                    if isinstance(tool_call, RequiredFunctionToolCall):
                        output = functions.execute(tool_call)
                        tool_outputs.append(
                            ToolOutput(tool_call_id=tool_call.id, output=output)
                        )
                
                if tool_outputs:
                    # Re-use the same stream's event handler
                    agents_client.runs.submit_tool_outputs_stream(
                        thread_id=event_data.thread_id,
                        run_id=event_data.id,
                        tool_outputs=tool_outputs,
                        event_handler=stream,  # Pass the stream to continue
                    )
        
        elif event_type == AgentStreamEvent.ERROR:
            print(f"Error: {event_data}")
        
        elif event_type == AgentStreamEvent.DONE:
            print("\nStream completed")
```

### 6.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not using context manager for streaming
```python
# WRONG - stream should be used with context manager
stream = agents_client.runs.stream(thread_id=thread.id, agent_id=agent.id)
for event_type, event_data, _ in stream:
    print(event_data)
# Missing: stream cleanup

# CORRECT
with agents_client.runs.stream(...) as stream:
    for event_type, event_data, _ in stream:
        print(event_data)
```

#### ❌ INCORRECT: Wrong event handler method signatures
```python
# WRONG - methods must return Optional[T] where T is the type parameter
class BadHandler(AgentEventHandler[str]):
    def on_message_delta(self, delta: MessageDeltaChunk):  # Missing return type
        print(delta.text)  # Should return Optional[str]
```

---

## 7. Cleanup Patterns

### 7.1 ✅ CORRECT: Delete Agent
```python
agents_client.delete_agent(agent.id)
```

### 7.2 ✅ CORRECT: Full Cleanup
```python
# Delete vector store if created
agents_client.vector_stores.delete(vector_store.id)

# Delete uploaded files
agents_client.files.delete(file_id=file.id)

# Delete agent
agents_client.delete_agent(agent.id)

# Delete connected agents if created
agents_client.delete_agent(sub_agent.id)
```

### 7.3 ✅ CORRECT: Save Generated Files
```python
from pathlib import Path

messages = agents_client.messages.list(thread_id=thread.id)

for msg in messages:
    # Save image files
    for img in msg.image_contents:
        file_id = img.image_file.file_id
        file_name = f"{file_id}_image.png"
        agents_client.files.save(file_id=file_id, file_name=file_name)
    
    # Handle file path annotations
    for ann in msg.file_path_annotations:
        print(f"File: {ann.file_path.file_id}")
```

---

## 8. Async Patterns

### 8.1 ✅ CORRECT: Full Async Example
```python
import asyncio
from azure.ai.projects.aio import AIProjectClient
from azure.ai.agents.models import (
    AgentThreadCreationOptions,
    ThreadMessageOptions,
    ListSortOrder,
    MessageTextContent,
)
from azure.identity.aio import DefaultAzureCredential

async def main():
    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )
    
    async with project_client:
        agents_client = project_client.agents
        
        agent = await agents_client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="my-agent",
            instructions="You are helpful",
        )
        
        run = await agents_client.create_thread_and_process_run(
            agent_id=agent.id,
            thread=AgentThreadCreationOptions(
                messages=[ThreadMessageOptions(role="user", content="Hello")]
            ),
        )
        
        if run.status == "failed":
            print(f"Error: {run.last_error}")
        
        # Async iteration over messages
        messages = agents_client.messages.list(
            thread_id=run.thread_id,
            order=ListSortOrder.ASCENDING,
        )
        async for msg in messages:
            last_part = msg.content[-1]
            if isinstance(last_part, MessageTextContent):
                print(f"{msg.role}: {last_part.text.value}")
        
        await agents_client.delete_agent(agent.id)

if __name__ == "__main__":
    asyncio.run(main())
```

### 8.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing await
```python
# WRONG - missing await for async operations
async def bad_example():
    agent = agents_client.create_agent(...)  # Missing await
    thread = agents_client.threads.create()  # Missing await
```

#### ❌ INCORRECT: Wrong credential type
```python
# WRONG - using sync credential with async client
from azure.ai.projects.aio import AIProjectClient
from azure.identity import DefaultAzureCredential  # Should be from .aio

# CORRECT
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
```

#### ❌ INCORRECT: Not using async iteration
```python
# WRONG - messages.list returns async iterator in async mode
messages = agents_client.messages.list(thread_id=thread.id)
for msg in messages:  # Wrong - should use async for
    print(msg)

# CORRECT
async for msg in messages:
    print(msg)
```

---

## 9. Run Status Reference

### Valid Run Status Values
| Status | Description | Terminal |
|--------|-------------|----------|
| `queued` | Run is queued for processing | No |
| `in_progress` | Run is actively processing | No |
| `requires_action` | Run needs tool output/approval | No |
| `completed` | Run finished successfully | Yes |
| `failed` | Run encountered an error | Yes |
| `cancelled` | Run was cancelled | Yes |
| `expired` | Run timed out | Yes |

### Correct Polling Pattern
```python
NON_TERMINAL_STATUSES = ["queued", "in_progress", "requires_action"]

while run.status in NON_TERMINAL_STATUSES:
    time.sleep(1)
    run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)
    
    if run.status == "requires_action":
        # Handle tool calls
        pass

if run.status == "failed":
    print(f"Error: {run.last_error}")
```

---

## 10. Function Definition Requirements

### ✅ CORRECT: Properly Documented Function
```python
def my_function(param1: str, param2: int, optional_param: Optional[str] = None) -> str:
    """Brief description of what this function does.
    
    :param param1: Description of param1.
    :param param2: Description of param2.
    :param optional_param: Optional description.
    :return: Description of return value.
    :rtype: str
    """
    result = {"param1": param1, "param2": param2}
    if optional_param:
        result["optional"] = optional_param
    return json.dumps(result)
```

### Requirements:
1. **Return type must be `str`** - Return JSON string via `json.dumps()`
2. **Docstring required** - SDK extracts description from docstring
3. **Type hints required** - SDK uses them for parameter types
4. **`:param` format** - Use `:param name: description` for parameter docs

### ❌ INCORRECT Patterns:
```python
# WRONG - returns dict instead of str
def bad_return(x: str) -> dict:
    return {"result": x}

# WRONG - no docstring
def no_docs(x: str) -> str:
    return json.dumps({"result": x})

# WRONG - no type hints
def no_types(x) -> str:
    return json.dumps({"result": x})
```

---

## 11. Environment Variables

### Required Variables
```bash
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
MODEL_DEPLOYMENT_NAME=gpt-4o-mini
```

### Optional Variables (for specific tools)
```bash
BING_CONNECTION_NAME=my-bing-connection
MCP_SERVER_URL=https://mcp.example.com
MCP_SERVER_LABEL=my-mcp
```

---

## 12. Test Scenarios Checklist

### Basic Operations
- [ ] Client creation with context manager
- [ ] Agent creation with basic parameters
- [ ] Thread creation
- [ ] Message creation
- [ ] Run with auto-polling (`create_and_process`)
- [ ] Message retrieval after run
- [ ] Agent deletion

### Tool Usage
- [ ] FunctionTool with proper function signatures
- [ ] ToolSet with multiple tools
- [ ] CodeInterpreterTool with file upload
- [ ] FileSearchTool with vector store
- [ ] AzureAISearchTool with connection
- [ ] BingGroundingTool with connection
- [ ] ConnectedAgentTool with sub-agent
- [ ] McpTool with approval handling
- [ ] OpenApiTool with spec

### Run Patterns
- [ ] Manual polling with status checks
- [ ] Auto function calling enabled
- [ ] Manual tool output submission
- [ ] MCP tool approval flow

### Streaming
- [ ] Basic streaming with context manager
- [ ] Custom event handler implementation
- [ ] Streaming with tool calls

### Async
- [ ] Async client creation
- [ ] Async agent/thread/message creation
- [ ] Async message iteration
- [ ] Proper await usage

### Error Handling
- [ ] Check run.status == "failed"
- [ ] Access run.last_error
- [ ] Handle requires_action status
- [ ] Cancel runs when needed

---

## 13. Quick Reference: Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `AttributeError: 'FunctionTool' has no attribute 'definitions'` | Wrong import | Import from `azure.ai.agents.models` |
| `Tools not being called` | Missing definitions | Use `tools=func_tool.definitions` |
| `File search not working` | Missing resources | Add `tool_resources=file_search.resources` |
| `Run stuck in requires_action` | Not handling tool calls | Submit tool outputs |
| `Async operation not awaited` | Missing await | Add `await` to all async calls |
| `Wrong credential type` | Sync cred with async client | Use `azure.identity.aio` |
| `Function not recognized` | No docstring | Add docstring with `:param` |
| `Invalid tool output` | Wrong return type | Return `json.dumps()` string |
