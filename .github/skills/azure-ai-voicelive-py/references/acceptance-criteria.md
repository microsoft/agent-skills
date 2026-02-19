# Azure AI Voice Live SDK Acceptance Criteria

**SDK**: `azure-ai-voicelive`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Commit**: `e7b5fa81aa188011fb4323382d1a32b32f54d55b`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Async connect (preferred)
```python
from azure.ai.voicelive.aio import connect
from azure.identity.aio import DefaultAzureCredential
```

#### ✅ CORRECT: Top-level connect (documented)
```python
from azure.ai.voicelive import connect
from azure.core.credentials import AzureKeyCredential
```

### 1.2 Model Imports

#### ✅ CORRECT: Session and VAD Models
```python
from azure.ai.voicelive.models import RequestSession, ServerVad, AzureStandardVoice
```

#### ✅ CORRECT: Tool Models
```python
from azure.ai.voicelive.models import FunctionTool, MCPTool
```

#### ✅ CORRECT: Enums
```python
from azure.ai.voicelive.models import Modality, InputAudioFormat, OutputAudioFormat
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong module paths
```python
# WRONG - models are not under aio
from azure.ai.voicelive.aio.models import RequestSession

# WRONG - models are not imported from package root
from azure.ai.voicelive import RequestSession
```

#### ❌ INCORRECT: Using OpenAI SDK
```python
# WRONG - use azure-ai-voicelive SDK instead
from openai import OpenAI
```

---

## 2. Authentication Patterns

### 2.1 ✅ CORRECT: DefaultAzureCredential (AAD)
```python
from azure.ai.voicelive.aio import connect
from azure.identity.aio import DefaultAzureCredential

async with connect(
    endpoint=os.environ["AZURE_COGNITIVE_SERVICES_ENDPOINT"],
    credential=DefaultAzureCredential(),
    model="gpt-4o-realtime-preview",
    credential_scopes=["https://cognitiveservices.azure.com/.default"],
) as conn:
    ...
```

### 2.2 ✅ CORRECT: API Key
```python
from azure.ai.voicelive.aio import connect
from azure.core.credentials import AzureKeyCredential

async with connect(
    endpoint=os.environ["AZURE_COGNITIVE_SERVICES_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["AZURE_COGNITIVE_SERVICES_KEY"]),
    model="gpt-4o-realtime-preview",
) as conn:
    ...
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Sync credential with async client
```python
from azure.ai.voicelive.aio import connect
from azure.identity import DefaultAzureCredential  # WRONG - async client requires azure.identity.aio

async with connect(
    endpoint=os.environ["AZURE_COGNITIVE_SERVICES_ENDPOINT"],
    credential=DefaultAzureCredential(),
    model="gpt-4o-realtime-preview",
) as conn:
    ...
```

#### ❌ INCORRECT: Hardcoded API key
```python
# WRONG - do not hardcode secrets
credential = AzureKeyCredential("my-secret-key")
```

---

## 3. Session Creation Patterns

### 3.1 ✅ CORRECT: RequestSession model
```python
from azure.ai.voicelive.models import RequestSession, Modality, ServerVad

session = RequestSession(
    instructions="You are a helpful assistant.",
    modalities=[Modality.TEXT, Modality.AUDIO],
    voice="alloy",
    turn_detection=ServerVad(
        threshold=0.5,
        prefix_padding_ms=300,
        silence_duration_ms=500,
    ),
)

await conn.session.update(session=session)
```

### 3.2 ✅ CORRECT: Dict-based session update
```python
await conn.session.update(session={
    "instructions": "Be concise.",
    "modalities": ["text", "audio"],
    "voice": "alloy",
    "turn_detection": {
        "type": "server_vad",
        "threshold": 0.5,
        "silence_duration_ms": 500,
    },
})
```

### 3.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Non-existent session methods
```python
# WRONG - session.create does not exist
await conn.session.create(session={"instructions": "..."})

# WRONG - update requires session= keyword
await conn.session.update({"instructions": "..."})
```

---

## 4. WebSocket/Event Loop Patterns

### 4.1 ✅ CORRECT: Async context manager and event loop
```python
from azure.ai.voicelive.aio import connect

async with connect(endpoint=endpoint, credential=credential, model=model) as conn:
    async for event in conn:
        if event.type == "response.done":
            break
```

### 4.2 ✅ CORRECT: Handling typed events
```python
from azure.ai.voicelive.models import ServerEventType

async for event in conn:
    if event.type == ServerEventType.RESPONSE_AUDIO_DELTA:
        ...
```

### 4.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using raw websockets library
```python
# WRONG - use azure-ai-voicelive connect() instead
import websockets
async with websockets.connect(endpoint) as ws:
    ...
```

#### ❌ INCORRECT: Missing async iteration
```python
# WRONG - async connection must be iterated with async for
for event in conn:
    ...
```

---

## 5. Audio Streaming Patterns

### 5.1 ✅ CORRECT: Append base64 audio
```python
import base64

audio_chunk = await read_microphone_chunk()
b64_audio = base64.b64encode(audio_chunk).decode()

await conn.input_audio_buffer.append(audio=b64_audio)
```

### 5.2 ✅ CORRECT: Receive audio deltas
```python
async for event in conn:
    if event.type == "response.audio.delta":
        audio_bytes = base64.b64decode(event.delta)
        await play_audio(audio_bytes)
```

### 5.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Sending raw bytes
```python
# WRONG - audio must be base64 encoded
await conn.input_audio_buffer.append(audio=audio_chunk)
```

#### ❌ INCORRECT: Wrong parameter name
```python
# WRONG - append expects audio= not data=
await conn.input_audio_buffer.append(data=b64_audio)
```

---

## 6. VAD (Voice Activity Detection) Patterns

### 6.1 ✅ CORRECT: Server VAD via dict
```python
await conn.session.update(session={
    "turn_detection": {
        "type": "server_vad",
        "threshold": 0.5,
        "prefix_padding_ms": 300,
        "silence_duration_ms": 500,
    }
})
```

### 6.2 ✅ CORRECT: Azure Semantic VAD
```python
await conn.session.update(session={
    "turn_detection": {"type": "azure_semantic_vad_en"}
})
```

### 6.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong field name or format
```python
# WRONG - "vad" is not a valid field
await conn.session.update(session={"vad": {"type": "server_vad"}})

# WRONG - "turn_detection" requires object, not string
await conn.session.update(session={"turn_detection": "server_vad"})
```

---

## 7. Turn-based Conversation Patterns

### 7.1 ✅ CORRECT: Manual turn control (no VAD)
```python
await conn.session.update(session={"turn_detection": None})

await conn.input_audio_buffer.append(audio=b64_audio)
await conn.input_audio_buffer.commit()
await conn.response.create()
```

### 7.2 ✅ CORRECT: Text-based turns via conversation items
```python
await conn.conversation.item.create(item={
    "type": "message",
    "role": "user",
    "content": [{"type": "input_text", "text": "Hello"}],
})

await conn.response.create()
```

### 7.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing commit in manual mode
```python
await conn.session.update(session={"turn_detection": None})

# WRONG - missing commit() before response
await conn.input_audio_buffer.append(audio=b64_audio)
await conn.response.create()
```
