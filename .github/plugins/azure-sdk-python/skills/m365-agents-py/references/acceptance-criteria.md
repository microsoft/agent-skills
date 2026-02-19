# Microsoft 365 Agents SDK Acceptance Criteria (Python)

**SDK**: `microsoft-agents-hosting-core`, `microsoft-agents-hosting-aiohttp`, `microsoft-agents-activity`, `microsoft-agents-authentication-msal`, `microsoft-agents-copilotstudio-client`
**Repository**: https://github.com/microsoft/Agents-for-python
**PyPI Packages**: https://pypi.org/search/?q=microsoft-agents
**Purpose**: Skill testing acceptance criteria for validating generated Python code correctness

---

## 1. Correct Import Patterns

### 1.1 Core Imports (Hosting)

#### CORRECT
```python
from microsoft_agents.hosting.core import (
    Authorization,
    AgentApplication,
    TurnState,
    TurnContext,
    MemoryStorage,
    MessageFactory,
)
from microsoft_agents.hosting.aiohttp import (
    CloudAdapter,
    start_agent_process,
    jwt_authorization_middleware,
)
```

### 1.2 Core Imports (Activity)

#### CORRECT
```python
from microsoft_agents.activity import (
    Activity,
    ActivityTypes,
    load_configuration_from_env,
    SensitivityUsageInfo,
)
```

### 1.3 Core Imports (Authentication)

#### CORRECT
```python
from microsoft_agents.authentication.msal import MsalConnectionManager
```

### 1.4 Core Imports (Copilot Studio Client)

#### CORRECT
```python
from microsoft_agents.copilotstudio.client import (
    ConnectionSettings,
    CopilotClient,
)
```

### 1.5 Anti-Patterns (ERRORS)

#### INCORRECT: Old dot-notation imports
```python
# WRONG - old import structure with dots
from microsoft.agents.hosting.core import AgentApplication
from microsoft.agents.activity import Activity
```

#### INCORRECT: Bot Framework imports
```python
# WRONG - Bot Framework SDK is not used with Microsoft 365 Agents SDK
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.integration.aiohttp import CloudAdapter
```

---

## 2. Hosting Pipeline

### 2.1 CORRECT: aiohttp registration with middleware
```python
from aiohttp.web import Request, Response, Application, run_app
from microsoft_agents.hosting.aiohttp import (
    start_agent_process,
    jwt_authorization_middleware,
    CloudAdapter,
)

async def entry_point(req: Request) -> Response:
    agent: AgentApplication = req.app["agent_app"]
    adapter: CloudAdapter = req.app["adapter"]
    return await start_agent_process(req, agent, adapter)

APP = Application(middlewares=[jwt_authorization_middleware])
APP.router.add_post("/api/messages", entry_point)
APP["agent_configuration"] = CONNECTION_MANAGER.get_default_connection_configuration()
APP["agent_app"] = AGENT_APP
APP["adapter"] = AGENT_APP.adapter
```

### 2.2 CORRECT: Configuration loading
```python
from os import environ
from dotenv import load_dotenv
from microsoft_agents.activity import load_configuration_from_env

load_dotenv()
agents_sdk_config = load_configuration_from_env(environ)
```

### 2.3 CORRECT: Storage and connection manager setup
```python
STORAGE = MemoryStorage()
CONNECTION_MANAGER = MsalConnectionManager(**agents_sdk_config)
ADAPTER = CloudAdapter(connection_manager=CONNECTION_MANAGER)
AUTHORIZATION = Authorization(STORAGE, CONNECTION_MANAGER, **agents_sdk_config)

AGENT_APP = AgentApplication[TurnState](
    storage=STORAGE, adapter=ADAPTER, authorization=AUTHORIZATION, **agents_sdk_config
)
```

### 2.4 INCORRECT: Missing middleware
```python
# WRONG - jwt_authorization_middleware should be included
APP = Application()  # Missing middlewares parameter
```

### 2.5 INCORRECT: Bot Framework adapter
```python
# WRONG - uses Bot Framework adapter
from botbuilder.integration.aiohttp import CloudAdapter
adapter = CloudAdapter()
```

---

## 3. AgentApplication Routing

### 3.1 CORRECT: Conversation update handler
```python
@AGENT_APP.conversation_update("membersAdded")
async def on_members_added(context: TurnContext, _state: TurnState):
    await context.send_activity("Welcome!")
```

### 3.2 CORRECT: Message handlers (string and regex)
```python
import re

@AGENT_APP.message("/status")
async def on_status(context: TurnContext, _state: TurnState):
    await context.send_activity("Status: OK")

@AGENT_APP.message(re.compile(r"^hello$", re.IGNORECASE))
async def on_hello(context: TurnContext, _state: TurnState):
    await context.send_activity("Hello!")
```

### 3.3 CORRECT: Activity type handler
```python
@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _state: TurnState):
    await context.send_activity(f"Echo: {context.activity.text}")

@AGENT_APP.activity(ActivityTypes.invoke)
async def on_invoke(context: TurnContext, _state: TurnState):
    invoke_response = Activity(
        type=ActivityTypes.invoke_response, value={"status": 200}
    )
    await context.send_activity(invoke_response)
```

### 3.4 CORRECT: Error handler
```python
@AGENT_APP.error
async def on_error(context: TurnContext, error: Exception):
    await context.send_activity("The agent encountered an error.")
```

### 3.5 INCORRECT: Bot Framework ActivityHandler
```python
# WRONG - Bot Framework ActivityHandler is not used
class MyBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        pass
```

---

## 4. OAuth / Auto Sign-In

### 4.1 CORRECT: Auth-protected message handler
```python
@AGENT_APP.message("/me", auth_handlers=["GRAPH"])
async def profile_request(context: TurnContext, state: TurnState):
    user_token_response = await AGENT_APP.auth.get_token(context, "GRAPH")
    if user_token_response and user_token_response.token:
        # Use token
        pass
```

### 4.2 CORRECT: Sign out
```python
@AGENT_APP.message("/logout")
async def logout(context: TurnContext, state: TurnState):
    await AGENT_APP.auth.sign_out(context, "GRAPH")
    await context.send_activity(MessageFactory.text("You have been logged out."))
```

### 4.3 CORRECT: Begin or continue OAuth flow
```python
token_response = await AGENT_APP.auth.begin_or_continue_flow(context, state, "GITHUB")
if token_response and token_response.token:
    # Token acquired
    pass
```

---

## 5. Streaming Responses

### 5.1 CORRECT: Streaming with Azure OpenAI
```python
from openai import AsyncAzureOpenAI
from microsoft_agents.activity import SensitivityUsageInfo

@AGENT_APP.message("poem")
async def on_poem_message(context: TurnContext, _state: TurnState):
    context.streaming_response.set_feedback_loop(True)
    context.streaming_response.set_generated_by_ai_label(True)
    context.streaming_response.set_sensitivity_label(
        SensitivityUsageInfo(
            type="https://schema.org/Message",
            schema_type="CreativeWork",
            name="Internal",
        )
    )
    context.streaming_response.queue_informative_update("Starting...")

    streamed_response = await CLIENT.chat.completions.create(
        model="gpt-4o",
        messages=[...],
        stream=True,
    )
    
    try:
        async for chunk in streamed_response:
            if chunk.choices and chunk.choices[0].delta.content:
                context.streaming_response.queue_text_chunk(
                    chunk.choices[0].delta.content
                )
    finally:
        await context.streaming_response.end_stream()
```

### 5.2 INCORRECT: Missing end_stream
```python
# WRONG - end_stream should always be called in finally block
async for chunk in streamed_response:
    context.streaming_response.queue_text_chunk(chunk)
# Missing: await context.streaming_response.end_stream()
```

---

## 6. Copilot Studio Client

### 6.1 CORRECT: ConnectionSettings and CopilotClient
```python
from microsoft_agents.copilotstudio.client import (
    ConnectionSettings,
    CopilotClient,
)

settings = ConnectionSettings(
    environment_id=environ.get("COPILOTSTUDIOAGENT__ENVIRONMENTID"),
    agent_identifier=environ.get("COPILOTSTUDIOAGENT__SCHEMANAME"),
)

token = acquire_token(...)  # MSAL token acquisition
copilot_client = CopilotClient(settings, token)
```

### 6.2 CORRECT: Start conversation and ask question
```python
# Start conversation
act = copilot_client.start_conversation(True)
async for action in act:
    if action.text:
        print(action.text)

# Ask question
replies = copilot_client.ask_question("Hello!", action.conversation.id)
async for reply in replies:
    if reply.type == ActivityTypes.message:
        print(reply.text)
```

### 6.3 INCORRECT: DirectLine usage
```python
# WRONG - DirectLine client is not part of Microsoft 365 Agents SDK
from botframework.directlineclient import DirectLineClient
```

---

## 7. Environment Variables

### 7.1 CORRECT: Configuration pattern
```bash
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID=<client-id>
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTSECRET=<client-secret>
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID=<tenant-id>
```

### 7.2 INCORRECT: Hardcoded secrets
```python
# WRONG - do not hardcode secrets
CLIENT_SECRET = "super-secret-value"
```

---

## 8. Logging Configuration

### 8.1 CORRECT: Enable SDK logging
```python
import logging

ms_agents_logger = logging.getLogger("microsoft_agents")
ms_agents_logger.addHandler(logging.StreamHandler())
ms_agents_logger.setLevel(logging.INFO)
```
