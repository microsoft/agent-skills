# Azure AI Projects SDK - Complete API Reference

**Package**: `azure-ai-projects` v2.0.0b4  
**Repository**: [Azure/azure-sdk-for-python](https://github.com/Azure/azure-sdk-for-python)  
**Path**: `sdk/ai/azure-ai-projects/`  
**Commit**: `7e86ab0076297173aae290c11fa14660bed2b125`

---

## Table of Contents

1. [Client Classes](#1-client-classes)
2. [Agent Classes](#2-agent-classes)
3. [Tool Classes](#3-tool-classes)
4. [ItemResource Classes](#4-itemresource-classes)
5. [InputItem Classes](#5-inputitem-classes)
6. [Index Classes](#6-index-classes)
7. [Evaluation Classes](#7-evaluation-classes)
8. [Memory Classes](#8-memory-classes)
9. [Schedule & Trigger Classes](#9-schedule--trigger-classes)
10. [Credential Classes](#10-credential-classes)
11. [ComputerAction Classes](#11-computeraction-classes)
12. [WebSearch Classes](#12-websearch-classes)
13. [Insight Classes](#13-insight-classes)
14. [Filter Classes](#14-filter-classes)
15. [Annotation Classes](#15-annotation-classes)
16. [Response & Output Classes](#16-response--output-classes)
17. [All Enums](#17-all-enums)

---

## 1. Client Classes

### AIProjectClient (Sync)

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

client = AIProjectClient(
    endpoint="https://<resource>.services.ai.azure.com/api/projects/<project>",
    credential=DefaultAzureCredential(),
)

# Operations
client.agents          # AgentsOperations
client.connections     # ConnectionsOperations
client.deployments     # DeploymentsOperations
client.datasets        # DatasetsOperations
client.indexes         # IndexesOperations
client.evaluations     # EvaluationsOperations
client.red_teams       # RedTeamsOperations
client.get_openai_client()  # Returns OpenAI-compatible client
```

### AIProjectClient (Async)

```python
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

async with AIProjectClient(
    endpoint="https://<resource>.services.ai.azure.com/api/projects/<project>",
    credential=DefaultAzureCredential(),
) as client:
    agent = await client.agents.create_agent(...)
```

---

## 2. Agent Classes

### Agent Definition Hierarchy

```
AgentDefinition (base)
├── PromptAgentDefinition         # AgentKind.PROMPT
├── HostedAgentDefinition         # AgentKind.HOSTED
├── ImageBasedHostedAgentDefinition  # AgentKind.IMAGE_BASED_HOSTED
├── ContainerAppAgentDefinition   # AgentKind.CONTAINER_APP
└── WorkflowAgentDefinition       # AgentKind.WORKFLOW
```

### PromptAgentDefinition

```python
from azure.ai.projects.models import PromptAgentDefinition

definition = PromptAgentDefinition(
    model="gpt-4o-mini",                           # Required
    instructions="You are helpful.",               # Optional
    name="my-agent",                               # Optional
    description="Agent description",               # Optional
    tools=[CodeInterpreterTool()],                 # Optional[List[Tool]]
    tool_resources={...},                          # Optional[Dict]
    response_format={"type": "json_object"},       # Optional
    temperature=0.7,                               # Optional[float]
    top_p=1.0,                                     # Optional[float]
    metadata={"key": "value"},                     # Optional[Dict]
)
```

### HostedAgentDefinition

```python
from azure.ai.projects.models import HostedAgentDefinition

definition = HostedAgentDefinition(
    model="gpt-4o-mini",
    instructions="You are helpful.",
    protocol_version="2025-05-01",  # Hosted agent protocol version
)
```

### ImageBasedHostedAgentDefinition

```python
from azure.ai.projects.models import ImageBasedHostedAgentDefinition

definition = ImageBasedHostedAgentDefinition(
    image_id="acr.azurecr.io/my-agent:latest",
    environment_variables={"KEY": "value"},
    protocol_version="2025-05-01",
)
```

### ContainerAppAgentDefinition

```python
from azure.ai.projects.models import ContainerAppAgentDefinition

definition = ContainerAppAgentDefinition(
    container_app_id="/subscriptions/.../containerApps/my-app",
)
```

### WorkflowAgentDefinition

```python
from azure.ai.projects.models import WorkflowAgentDefinition

definition = WorkflowAgentDefinition(
    csdl="<workflow CSDL definition>",  # Common Schema Definition Language
)
```

### AgentKind Enum

```python
from azure.ai.projects.models import AgentKind

AgentKind.PROMPT              # "prompt"
AgentKind.HOSTED              # "hosted"
AgentKind.IMAGE_BASED_HOSTED  # "image_based_hosted"
AgentKind.CONTAINER_APP       # "container_app"
AgentKind.WORKFLOW            # "workflow"
```

---

## 3. Tool Classes

### Tool Type Hierarchy

```
Tool (base)
├── CodeInterpreterTool
├── FileSearchTool
├── FunctionTool
├── AzureAISearchTool
├── AzureFunctionTool
├── BingGroundingTool
├── BingCustomSearchPreviewTool
├── OpenApiTool
├── MCPTool
├── ImageGenTool
├── ComputerUsePreviewTool
├── WebSearchTool
├── WebSearchPreviewTool
├── A2APreviewTool
├── BrowserAutomationPreviewTool
├── CaptureStructuredOutputsTool
├── MicrosoftFabricPreviewTool
├── SharepointPreviewTool
├── MemorySearchPreviewTool
├── LocalShellToolParam
├── FunctionShellToolParam
├── ApplyPatchToolParam
└── CustomToolParam
```

### CodeInterpreterTool

```python
from azure.ai.projects.models import CodeInterpreterTool

tool = CodeInterpreterTool(
    container=CodeInterpreterContainerAuto(),  # Optional: auto-managed container
)
```

### FileSearchTool

```python
from azure.ai.projects.models import FileSearchTool

tool = FileSearchTool(
    vector_store_ids=["vs_abc123"],           # Optional[List[str]]
    ranking_options=RankingOptions(...),       # Optional
    max_num_results=10,                        # Optional[int]
)
```

### FunctionTool

```python
from azure.ai.projects.models import FunctionTool

def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: 72F"

tool = FunctionTool(functions=[get_weather])
```

### AzureAISearchTool

```python
from azure.ai.projects.models import (
    AzureAISearchTool,
    AzureAISearchToolResource,
    AISearchIndexResource,
)

tool = AzureAISearchTool(
    resources=[
        AzureAISearchToolResource(
            index=AISearchIndexResource(
                index_connection_id="conn_id",
                index_name="my-index",
            ),
            query_type=AzureAISearchQueryType.VECTOR,
        )
    ]
)
```

### AzureFunctionTool

```python
from azure.ai.projects.models import (
    AzureFunctionTool,
    AzureFunctionDefinition,
    AzureFunctionBinding,
    AzureFunctionStorageQueue,
)

tool = AzureFunctionTool(
    function=AzureFunctionDefinition(
        function=AzureFunctionDefinitionFunction(
            name="my-function",
            description="Processes data",
            parameters={
                "type": "object",
                "properties": {"input": {"type": "string"}},
            },
        ),
        input_binding=AzureFunctionBinding(
            storage_queue=AzureFunctionStorageQueue(
                queue_service_uri="https://...",
                queue_name="input-queue",
            )
        ),
        output_binding=AzureFunctionBinding(...),
    )
)
```

### BingGroundingTool

```python
from azure.ai.projects.models import (
    BingGroundingTool,
    BingGroundingSearchConfiguration,
    BingGroundingSearchToolParameters,
)

tool = BingGroundingTool(
    bing_grounding=BingGroundingSearchToolParameters(
        connection_id="bing_connection_id",
        configuration=BingGroundingSearchConfiguration(
            market="en-US",
            set_lang="en",
        ),
    )
)
```

### OpenApiTool

```python
from azure.ai.projects.models import (
    OpenApiTool,
    OpenApiFunctionDefinition,
    OpenApiAnonymousAuthDetails,
)

tool = OpenApiTool(
    openapi=OpenApiFunctionDefinition(
        name="weather-api",
        description="Get weather data",
        spec={"openapi": "3.0.0", ...},
        auth=OpenApiAnonymousAuthDetails(),
    )
)
```

### MCPTool

```python
from azure.ai.projects.models import (
    MCPTool,
    MCPToolFilter,
    MCPToolRequireApproval,
)

tool = MCPTool(
    server_label="my-mcp-server",
    server_url="http://localhost:8000/mcp",
    allowed_tools=MCPToolFilter(tool_names=["search", "fetch"]),
    require_approval=MCPToolRequireApproval.ALWAYS,
)
```

### ComputerUsePreviewTool

```python
from azure.ai.projects.models import ComputerUsePreviewTool, ComputerEnvironment

tool = ComputerUsePreviewTool(
    display_width=1920,
    display_height=1080,
    environment=ComputerEnvironment.BROWSER,
)
```

### ToolType Enum (23 values)

```python
from azure.ai.projects.models import ToolType

ToolType.CODE_INTERPRETER           # "code_interpreter"
ToolType.FILE_SEARCH                # "file_search"
ToolType.FUNCTION                   # "function"
ToolType.BING_GROUNDING             # "bing_grounding"
ToolType.AZURE_AI_SEARCH            # "azure_ai_search"
ToolType.AZURE_FUNCTION             # "azure_function"
ToolType.OPENAPI                    # "openapi"
ToolType.MCP                        # "mcp"
ToolType.IMAGE_GEN                  # "image_gen"
ToolType.COMPUTER_USE_PREVIEW       # "computer_use_preview"
ToolType.WEB_SEARCH                 # "web_search"
ToolType.WEB_SEARCH_PREVIEW         # "web_search_preview"
ToolType.A2A_PREVIEW                # "a2a_preview"
ToolType.BROWSER_AUTOMATION_PREVIEW # "browser_automation_preview"
ToolType.CAPTURE_STRUCTURED_OUTPUTS # "capture_structured_outputs"
ToolType.MICROSOFT_FABRIC_PREVIEW   # "microsoft_fabric_preview"
ToolType.SHAREPOINT_PREVIEW         # "sharepoint_preview"
ToolType.MEMORY_SEARCH_PREVIEW      # "memory_search_preview"
ToolType.BING_CUSTOM_SEARCH_PREVIEW # "bing_custom_search_preview"
ToolType.LOCAL_SHELL                # "local_shell"
ToolType.FUNCTION_SHELL             # "function_shell"
ToolType.APPLY_PATCH                # "apply_patch"
ToolType.CUSTOM                     # "custom"
```

---

## 4. ItemResource Classes

Output item types returned from agent runs:

| Class | ItemResourceType | Description |
|-------|------------------|-------------|
| `ItemResourceFunctionToolCallResource` | `FUNCTION_CALL` | Function call result |
| `ItemResourceCodeInterpreterToolCall` | `CODE_INTERPRETER_CALL` | Code execution |
| `ItemResourceFileSearchToolCall` | `FILE_SEARCH_CALL` | File search result |
| `ItemResourceMcpToolCall` | `MCP_CALL` | MCP tool call |
| `ItemResourceComputerToolCall` | `COMPUTER_CALL` | Computer action |
| `ItemResourceWebSearchToolCall` | `WEB_SEARCH_CALL` | Web search result |
| `ItemResourceImageGenToolCall` | `IMAGE_GEN_CALL` | Image generation |
| `ItemResourceApplyPatchToolCall` | `APPLY_PATCH_CALL` | Patch application |
| `ItemResourceLocalShellToolCall` | `LOCAL_SHELL_CALL` | Shell command |
| `ItemResourceFunctionShellCall` | `FUNCTION_SHELL_CALL` | Function shell |
| `ItemResourceOutputMessage` | `MESSAGE` | Output message |
| `StructuredOutputsItemResource` | `STRUCTURED_OUTPUTS` | Structured output |
| `WorkflowActionOutputItemResource` | `WORKFLOW_ACTION_OUTPUT` | Workflow output |
| `OAuthConsentRequestItemResource` | `OAUTH_CONSENT_REQUEST` | OAuth consent |
| `ItemResourceMcpApprovalRequest` | `MCP_APPROVAL_REQUEST` | MCP approval |
| `ItemResourceMcpListTools` | `MCP_LIST_TOOLS` | MCP tools list |

---

## 5. InputItem Classes

Input item types for agent interactions:

| Class | InputItemType | Description |
|-------|---------------|-------------|
| `InputItemFunctionToolCall` | `FUNCTION_CALL` | Function call input |
| `InputItemCodeInterpreterToolCall` | `CODE_INTERPRETER_CALL` | Code input |
| `InputItemFileSearchToolCall` | `FILE_SEARCH_CALL` | Search input |
| `InputItemMcpToolCall` | `MCP_CALL` | MCP input |
| `InputItemComputerToolCall` | `COMPUTER_CALL` | Computer input |
| `InputItemWebSearchToolCall` | `WEB_SEARCH_CALL` | Web search input |
| `InputItemOutputMessage` | `MESSAGE` | Message input |
| `InputItemReasoningItem` | `REASONING` | Reasoning input |
| `InputItemMcpApprovalRequest` | `MCP_APPROVAL_REQUEST` | Approval input |
| `InputItemMcpApprovalResponse` | `MCP_APPROVAL_RESPONSE` | Approval response |
| `InputItemCustomToolCall` | `CUSTOM_TOOL_CALL` | Custom tool input |
| `InputItemCustomToolCallOutput` | `CUSTOM_TOOL_CALL_OUTPUT` | Custom output |

---

## 6. Index Classes

```python
from azure.ai.projects.models import (
    Index,
    AISearchIndexResource,
    ManagedAzureAISearchIndex,
    CosmosDBIndex,
    AzureAISearchIndex,
    IndexType,
)

# Azure AI Search Index
index = AzureAISearchIndex(
    connection_id="search_connection_id",
    index_name="my-index",
)

# Managed Azure AI Search Index
managed_index = ManagedAzureAISearchIndex(
    embedding_model_connection="embedding_conn",
    embedding_model_deployment="text-embedding-ada-002",
)

# Cosmos DB Index
cosmos_index = CosmosDBIndex(
    connection_id="cosmos_connection_id",
    database_name="my-db",
    container_name="my-container",
)
```

### IndexType Enum

```python
IndexType.AZURE_AI_SEARCH          # "azure_ai_search"
IndexType.MANAGED_AZURE_AI_SEARCH  # "managed_azure_ai_search"
IndexType.COSMOS_DB                # "cosmos_db"
```

---

## 7. Evaluation Classes

```python
from azure.ai.projects.models import (
    # Core evaluation
    Evaluator,
    EvaluatorDefinition,
    EvaluatorVersion,
    EvaluatorMetric,
    EvalResult,
    
    # Rules and actions
    EvaluationRule,
    EvaluationRuleAction,
    ContinuousEvaluationRuleAction,
    HumanEvaluationRuleAction,
    
    # Comparison reports
    EvalCompareReport,
    EvalRunResultComparison,
    EvalRunResultSummary,
    EvalRunResultCompareItem,
    EvaluationResultSample,
    
    # Evaluator definitions
    CodeBasedEvaluatorDefinition,
    PromptBasedEvaluatorDefinition,
    
    # Taxonomy
    EvaluationTaxonomy,
    EvaluationTaxonomyInput,
    TaxonomyCategory,
    TaxonomySubCategory,
)
```

### EvaluatorType Enum

```python
from azure.ai.projects.models import EvaluatorType

EvaluatorType.GROUNDEDNESS
EvaluatorType.RELEVANCE
EvaluatorType.COHERENCE
EvaluatorType.FLUENCY
EvaluatorType.SIMILARITY
EvaluatorType.F1_SCORE
EvaluatorType.RETRIEVAL_SCORE
EvaluatorType.HATE_UNFAIRNESS
EvaluatorType.VIOLENCE
EvaluatorType.SELF_HARM
EvaluatorType.SEXUAL
EvaluatorType.PROTECTED_MATERIAL_TEXT
EvaluatorType.INDIRECT_ATTACK
EvaluatorType.CODE_VULNERABILITY
EvaluatorType.CUSTOM
```

---

## 8. Memory Classes

```python
from azure.ai.projects.models import (
    # Memory items
    MemoryItem,
    ChatSummaryMemoryItem,
    UserProfileMemoryItem,
    
    # Memory stores
    MemoryStoreDefinition,
    MemoryStoreDefaultDefinition,
    MemoryStoreDefaultOptions,
    MemoryStoreDetails,
    
    # Memory operations
    MemoryOperation,
    MemorySearchItem,
    MemorySearchOptions,
    MemorySearchPreviewTool,
    
    # Results
    MemoryStoreSearchResult,
    MemoryStoreUpdateResult,
    MemoryStoreDeleteScopeResult,
)
```

### MemoryItemKind Enum

```python
from azure.ai.projects.models import MemoryItemKind

MemoryItemKind.CHAT_SUMMARY    # "chat_summary"
MemoryItemKind.USER_PROFILE    # "user_profile"
```

### MemoryStoreKind Enum

```python
from azure.ai.projects.models import MemoryStoreKind

MemoryStoreKind.DEFAULT        # "default"
```

### MemoryOperationKind Enum

```python
from azure.ai.projects.models import MemoryOperationKind

MemoryOperationKind.ADD        # "add"
MemoryOperationKind.REMOVE     # "remove"
```

---

## 9. Schedule & Trigger Classes

### Schedule Classes

```python
from azure.ai.projects.models import (
    Schedule,
    ScheduleRun,
    ScheduleTask,
    EvaluationScheduleTask,
    InsightScheduleTask,
)

# Create a schedule
schedule = Schedule(
    name="daily-eval",
    trigger=CronTrigger(expression="0 0 * * *"),
    task=EvaluationScheduleTask(
        evaluation_id="eval_123",
    ),
)
```

### Trigger Classes

```python
from azure.ai.projects.models import (
    Trigger,
    CronTrigger,
    RecurrenceTrigger,
    OneTimeTrigger,
)

# Cron trigger
cron = CronTrigger(
    expression="0 9 * * MON-FRI",  # 9 AM weekdays
    time_zone="America/Los_Angeles",
)

# Recurrence trigger
recurrence = RecurrenceTrigger(
    frequency=RecurrenceType.DAILY,
    interval=1,
    schedule=DailyRecurrenceSchedule(hours=[9, 17], minutes=[0]),
)

# One-time trigger
one_time = OneTimeTrigger(
    run_at="2026-02-01T09:00:00Z",
)
```

### RecurrenceSchedule Classes

```python
from azure.ai.projects.models import (
    RecurrenceSchedule,
    HourlyRecurrenceSchedule,
    DailyRecurrenceSchedule,
    WeeklyRecurrenceSchedule,
    MonthlyRecurrenceSchedule,
    DayOfWeek,
)

# Hourly
hourly = HourlyRecurrenceSchedule(minutes=[0, 30])

# Daily
daily = DailyRecurrenceSchedule(hours=[9, 17], minutes=[0])

# Weekly
weekly = WeeklyRecurrenceSchedule(
    days=[DayOfWeek.MONDAY, DayOfWeek.WEDNESDAY, DayOfWeek.FRIDAY],
    hours=[9],
    minutes=[0],
)

# Monthly
monthly = MonthlyRecurrenceSchedule(
    month_days=[1, 15],
    hours=[9],
    minutes=[0],
)
```

### TriggerType Enum

```python
from azure.ai.projects.models import TriggerType

TriggerType.CRON        # "cron"
TriggerType.RECURRENCE  # "recurrence"
TriggerType.ONE_TIME    # "one_time"
```

### RecurrenceType Enum

```python
from azure.ai.projects.models import RecurrenceType

RecurrenceType.HOURLY   # "hourly"
RecurrenceType.DAILY    # "daily"
RecurrenceType.WEEKLY   # "weekly"
RecurrenceType.MONTHLY  # "monthly"
```

---

## 10. Credential Classes

```python
from azure.ai.projects.models import (
    BaseCredentials,
    ApiKeyCredentials,
    EntraIDCredentials,
    SASCredentials,
    NoAuthenticationCredentials,
    AgenticIdentityCredentials,
    CustomCredential,
    CredentialType,
)

# API Key
api_key_cred = ApiKeyCredentials(key="sk-...")

# Entra ID (Azure AD)
entra_cred = EntraIDCredentials(
    client_id="...",
    client_secret="...",
    tenant_id="...",
)

# SAS Token
sas_cred = SASCredentials(sas_token="?sv=...")

# No authentication
no_auth = NoAuthenticationCredentials()

# Agentic Identity
agentic_cred = AgenticIdentityCredentials()
```

### CredentialType Enum

```python
from azure.ai.projects.models import CredentialType

CredentialType.API_KEY              # "api_key"
CredentialType.ENTRA_ID             # "entra_id"
CredentialType.SAS                  # "sas"
CredentialType.NO_AUTH              # "no_auth"
CredentialType.AGENTIC_IDENTITY     # "agentic_identity"
CredentialType.CUSTOM               # "custom"
```

---

## 11. ComputerAction Classes

```python
from azure.ai.projects.models import (
    ComputerAction,
    ClickParam,
    DoubleClickAction,
    Drag,
    DragPoint,
    KeyPressAction,
    Move,
    Screenshot,
    Scroll,
    Type,
    Wait,
    ComputerActionType,
)

# Click
click = ClickParam(
    x=100,
    y=200,
    button=ClickButtonType.LEFT,
)

# Double click
dbl_click = DoubleClickAction(x=100, y=200)

# Drag
drag = Drag(
    path=[DragPoint(x=0, y=0), DragPoint(x=100, y=100)],
)

# Key press
key = KeyPressAction(keys=["ctrl", "c"])

# Move
move = Move(x=300, y=400)

# Screenshot
screenshot = Screenshot()

# Scroll
scroll = Scroll(x=0, y=500, delta_x=0, delta_y=-100)

# Type text
type_text = Type(text="Hello, World!")

# Wait
wait = Wait(ms=1000)
```

### ComputerActionType Enum

```python
from azure.ai.projects.models import ComputerActionType

ComputerActionType.CLICK          # "click"
ComputerActionType.DOUBLE_CLICK   # "double_click"
ComputerActionType.DRAG           # "drag"
ComputerActionType.KEY_PRESS      # "keypress"
ComputerActionType.MOVE           # "move"
ComputerActionType.SCREENSHOT     # "screenshot"
ComputerActionType.SCROLL         # "scroll"
ComputerActionType.TYPE           # "type"
ComputerActionType.WAIT           # "wait"
```

---

## 12. WebSearch Classes

```python
from azure.ai.projects.models import (
    WebSearchTool,
    WebSearchPreviewTool,
    WebSearchToolFilters,
    WebSearchApproximateLocation,
    WebSearchConfiguration,
    SearchContextSize,
)

# Web Search Tool
tool = WebSearchTool(
    user_location=WebSearchApproximateLocation(
        city="Seattle",
        region="Washington",
        country="US",
    ),
    search_context_size=SearchContextSize.MEDIUM,
)

# Web Search Preview Tool
preview_tool = WebSearchPreviewTool(
    configuration=WebSearchConfiguration(
        filters=WebSearchToolFilters(
            domains=["docs.microsoft.com", "learn.microsoft.com"],
        ),
    ),
)
```

### Web Search Action Classes

```python
from azure.ai.projects.models import (
    WebSearchActionFind,
    WebSearchActionOpenPage,
    WebSearchActionSearch,
    WebSearchActionSearchSources,
)
```

### SearchContextSize Enum

```python
from azure.ai.projects.models import SearchContextSize

SearchContextSize.LOW     # "low"
SearchContextSize.MEDIUM  # "medium"
SearchContextSize.HIGH    # "high"
```

---

## 13. Insight Classes

```python
from azure.ai.projects.models import (
    # Core
    Insight,
    InsightRequest,
    InsightResult,
    InsightCluster,
    InsightSummary,
    InsightsMetadata,
    InsightSample,
    
    # Model configuration
    InsightModelConfiguration,
    
    # Specialized results
    ClusterInsightResult,
    ClusterTokenUsage,
    AgentClusterInsightResult,
    AgentClusterInsightsRequest,
    EvaluationRunClusterInsightResult,
    EvaluationRunClusterInsightsRequest,
)
```

### InsightType Enum

```python
from azure.ai.projects.models import InsightType

InsightType.CLUSTER  # "cluster"
```

---

## 14. Filter Classes

```python
from azure.ai.projects.models import (
    ComparisonFilter,
    CompoundFilter,
    MCPToolFilter,
    MCPToolRequireApproval,
)

# Comparison filter
comparison = ComparisonFilter(
    field="category",
    operator="eq",
    value="documentation",
)

# Compound filter
compound = CompoundFilter(
    logical_operator="and",
    filters=[comparison1, comparison2],
)

# MCP tool filter
mcp_filter = MCPToolFilter(
    tool_names=["search", "fetch", "analyze"],
)
```

---

## 15. Annotation Classes

```python
from azure.ai.projects.models import (
    Annotation,
    FileCitationBody,
    ContainerFileCitationBody,
    UrlCitationBody,
    AnnotationType,
)
```

### AnnotationType Enum

```python
from azure.ai.projects.models import AnnotationType

AnnotationType.FILE_CITATION           # "file_citation"
AnnotationType.CONTAINER_FILE_CITATION # "container_file_citation"
AnnotationType.URL_CITATION            # "url_citation"
AnnotationType.FILE_PATH               # "file_path"
```

---

## 16. Response & Output Classes

```python
from azure.ai.projects.models import (
    # Output content
    OutputContent,
    OutputMessageContent,
    OutputMessageContentOutputTextContent,
    OutputMessageContentRefusalContent,
    
    # Usage details
    ResponseUsageInputTokensDetails,
    ResponseUsageOutputTokensDetails,
    
    # Delete responses
    DeleteAgentResponse,
    DeleteAgentVersionResponse,
    DeleteMemoryStoreResult,
)
```

---

## 17. All Enums (67 Total)

### Agent & Protocol Enums
```python
AgentKind              # PROMPT, HOSTED, IMAGE_BASED_HOSTED, CONTAINER_APP, WORKFLOW
AgentProtocol          # Protocol versions
```

### Tool Enums
```python
ToolType               # 23 tool types
ComputerActionType     # CLICK, DOUBLE_CLICK, DRAG, KEY_PRESS, MOVE, SCREENSHOT, SCROLL, TYPE, WAIT
ClickButtonType        # LEFT, RIGHT, MIDDLE, WHEEL
ComputerEnvironment    # BROWSER, DESKTOP, ...
OpenApiAuthType        # ANONYMOUS, MANAGED, PROJECT_CONNECTION
MCPToolCallStatus      # PENDING, APPROVED, REJECTED
```

### Item Type Enums
```python
ItemResourceType       # 26 output item types
InputItemType          # 20+ input item types
InputContentType       # TEXT, IMAGE, FILE
OutputContentType      # TEXT, REFUSAL
OutputMessageContentType  # OUTPUT_TEXT, REFUSAL
```

### Index & Data Enums
```python
IndexType              # AZURE_AI_SEARCH, MANAGED_AZURE_AI_SEARCH, COSMOS_DB
DatasetType            # FILE, FOLDER
AzureAISearchQueryType # SIMPLE, FULL, SEMANTIC, VECTOR, VECTOR_SIMPLE_HYBRID, ...
```

### Evaluation Enums
```python
EvaluatorType          # GROUNDEDNESS, RELEVANCE, COHERENCE, FLUENCY, etc.
EvaluatorCategory      # QUALITY, SAFETY, CUSTOM
EvaluatorDefinitionType # CODE_BASED, PROMPT_BASED
EvaluatorMetricType    # NUMERIC, BOOLEAN, STRING
EvaluatorMetricDirection # HIGHER_IS_BETTER, LOWER_IS_BETTER
RiskCategory           # HATE_UNFAIRNESS, VIOLENCE, SELF_HARM, SEXUAL, etc.
SampleType             # GOOD, BAD, NEUTRAL
```

### Memory Enums
```python
MemoryItemKind         # CHAT_SUMMARY, USER_PROFILE
MemoryStoreKind        # DEFAULT
MemoryOperationKind    # ADD, REMOVE
MemoryStoreUpdateStatus # COMPLETED, PENDING, FAILED
```

### Schedule & Trigger Enums
```python
TriggerType            # CRON, RECURRENCE, ONE_TIME
RecurrenceType         # HOURLY, DAILY, WEEKLY, MONTHLY
DayOfWeek              # MONDAY through SUNDAY
ScheduleTaskType       # EVALUATION, INSIGHT
ScheduleProvisioningStatus # PROVISIONING, PROVISIONED, FAILED
```

### Credential Enums
```python
CredentialType         # API_KEY, ENTRA_ID, SAS, NO_AUTH, AGENTIC_IDENTITY, CUSTOM
```

### Connection Enums
```python
ConnectionType         # AZURE_OPEN_AI, AZURE_AI_SEARCH, AZURE_BLOB, etc.
DeploymentType         # MODEL, EMBEDDING, etc.
```

### Annotation Enums
```python
AnnotationType         # FILE_CITATION, CONTAINER_FILE_CITATION, URL_CITATION, FILE_PATH
```

### Status Enums
```python
OperationState         # PENDING, IN_PROGRESS, COMPLETED, FAILED
FunctionCallItemStatus # IN_PROGRESS, COMPLETED, INCOMPLETE
LocalShellCallStatus   # PENDING, COMPLETED, ERROR
ApplyPatchCallStatus   # PENDING, COMPLETED, FAILED
```

### Miscellaneous Enums
```python
PageOrder              # ASC, DESC
ImageDetail            # LOW, HIGH, AUTO
InputFidelity          # LOW, MEDIUM, HIGH
SearchContextSize      # LOW, MEDIUM, HIGH
RankerVersionType      # V1, V2
GrammarSyntax1         # BNF, EBNF
TextResponseFormatConfigurationType  # TEXT, JSON_OBJECT, JSON_SCHEMA
ContainerLogKind       # STDOUT, STDERR
ContainerMemoryLimit   # 256MB, 512MB, 1GB, etc.
DetailEnum             # LOW, HIGH, AUTO
AttackStrategy         # Various attack strategies for red teaming
TreatmentEffectType    # POSITIVE, NEGATIVE, NEUTRAL
```

---

## Quick Reference: Common Import Patterns

### Client Initialization
```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import os

client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
```

### Agent with Tools
```python
from azure.ai.projects.models import (
    PromptAgentDefinition,
    CodeInterpreterTool,
    FileSearchTool,
    FunctionTool,
    AzureAISearchTool,
    BingGroundingTool,
)
```

### All Tool Imports
```python
from azure.ai.projects.models import (
    # Core tools
    CodeInterpreterTool,
    FileSearchTool,
    FunctionTool,
    # Azure tools
    AzureAISearchTool,
    AzureFunctionTool,
    BingGroundingTool,
    BingCustomSearchPreviewTool,
    # External tools
    OpenApiTool,
    MCPTool,
    # Computer use
    ComputerUsePreviewTool,
    # Web & preview
    WebSearchTool,
    WebSearchPreviewTool,
    A2APreviewTool,
    BrowserAutomationPreviewTool,
    # Enterprise
    MicrosoftFabricPreviewTool,
    SharepointPreviewTool,
    # Memory
    MemorySearchPreviewTool,
    # Utility
    ImageGenTool,
    CaptureStructuredOutputsTool,
    LocalShellToolParam,
    FunctionShellToolParam,
    ApplyPatchToolParam,
    CustomToolParam,
)
```

---

*Document generated from azure-ai-projects v2.0.0b4 source code analysis.*
*Last updated: February 2026*
