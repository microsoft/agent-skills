# Azure AI Voice Live SDK - API Reference

## Table of Contents
- [connect() Function](#connect-function)
- [VoiceLiveConnection](#voiceliveconnection)
- [SessionResource](#sessionresource)
- [ResponseResource](#responseresource)
- [InputAudioBufferResource](#inputaudiobufferresource)
- [OutputAudioBufferResource](#outputaudiobufferresource)
- [ConversationResource](#conversationresource)
- [TranscriptionSessionResource](#transcriptionsessionresource)
- [WebsocketConnectionOptions](#websocketconnectionoptions)
- [Exceptions](#exceptions)

---

## connect() Function

Creates an async context manager for WebSocket connections.

```python
from azure.ai.voicelive.aio import connect

async with connect(
    credential: Union[AzureKeyCredential, AsyncTokenCredential],
    endpoint: str,
    api_version: str = "2025-10-01",
    model: Optional[str] = None,
    query: Optional[Mapping[str, Any]] = None,
    headers: Optional[Mapping[str, Any]] = None,
    connection_options: Optional[WebsocketConnectionOptions] = None,
    credential_scopes: Optional[List[str]] = None,
    **kwargs
) -> VoiceLiveConnection:
    ...
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `credential` | `AzureKeyCredential` or `AsyncTokenCredential` | Yes | Authentication credential |
| `endpoint` | `str` | Yes | Service endpoint URL |
| `api_version` | `str` | No | API version (default: "2025-10-01") |
| `model` | `str` | Sometimes | Model identifier (required unless using Agent scenario) |
| `query` | `Mapping[str, Any]` | No | Additional URL query parameters |
| `headers` | `Mapping[str, Any]` | No | Additional HTTP headers |
| `connection_options` | `WebsocketConnectionOptions` | No | WebSocket transport options |
| `credential_scopes` | `List[str]` | No | OAuth scopes (default: `["https://ai.azure.com/.default"]`) |

---

## VoiceLiveConnection

Main connection class with resource accessors.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `session` | `SessionResource` | Session configuration |
| `response` | `ResponseResource` | Response management |
| `input_audio_buffer` | `InputAudioBufferResource` | Audio input buffer |
| `output_audio_buffer` | `OutputAudioBufferResource` | Audio output buffer |
| `conversation` | `ConversationResource` | Conversation items |
| `transcription_session` | `TranscriptionSessionResource` | Transcription config |

### Methods

```python
async def recv() -> ServerEvent:
    """Receive and parse the next typed server event."""

async def recv_bytes() -> bytes:
    """Receive raw bytes from the connection."""

async def send(event: Union[Mapping[str, Any], ClientEvent]) -> None:
    """Send an event to the server."""

async def close(*, code: int = 1000, reason: str = "") -> None:
    """Close the WebSocket connection."""

async def __aiter__() -> AsyncIterator[ServerEvent]:
    """Iterate over server events until connection closes."""
```

---

## SessionResource

Manage session configuration.

### Methods

```python
async def update(
    *,
    session: Union[Mapping[str, Any], RequestSession],
    event_id: Optional[str] = None
) -> None:
    """Update session configuration."""
```

### RequestSession Fields

| Field | Type | Description |
|-------|------|-------------|
| `instructions` | `str` | System prompt for the model |
| `modalities` | `List[Modality]` | `["text"]`, `["audio"]`, or `["text", "audio"]` |
| `voice` | `Voice` | Voice for audio output |
| `input_audio_format` | `InputAudioFormat` | Audio input format |
| `output_audio_format` | `OutputAudioFormat` | Audio output format |
| `turn_detection` | `TurnDetection` | VAD configuration or `None` for manual |
| `tools` | `List[Tool]` | Function tools |
| `tool_choice` | `ToolChoice` | `"auto"`, `"none"`, `"required"`, or specific function |
| `temperature` | `float` | Model temperature (0.6-1.2) |
| `max_response_output_tokens` | `int` or `"inf"` | Max tokens per response |
| `input_audio_transcription` | `AudioInputTranscriptionOptions` | Transcription settings |

---

## ResponseResource

Manage model responses.

### Methods

```python
async def create(
    *,
    response: Optional[Union[ResponseCreateParams, Mapping[str, Any]]] = None,
    event_id: Optional[str] = None,
    additional_instructions: Optional[str] = None
) -> None:
    """Create a response (trigger inference)."""

async def cancel(
    *,
    response_id: Optional[str] = None,
    event_id: Optional[str] = None
) -> None:
    """Cancel an in-progress response."""
```

### ResponseCreateParams Fields

| Field | Type | Description |
|-------|------|-------------|
| `modalities` | `List[Modality]` | Override session modalities |
| `instructions` | `str` | Override session instructions |
| `voice` | `Voice` | Override session voice |
| `temperature` | `float` | Override temperature |
| `max_response_output_tokens` | `int` | Override max tokens |
| `conversation` | `str` | `"auto"` or `"none"` |

---

## InputAudioBufferResource

Manage audio input buffer.

### Methods

```python
async def append(
    *,
    audio: str,  # Base64-encoded audio
    event_id: Optional[str] = None
) -> None:
    """Append audio data to the input buffer."""

async def commit(
    *,
    event_id: Optional[str] = None
) -> None:
    """Commit the buffer as a user message."""

async def clear(
    *,
    event_id: Optional[str] = None
) -> None:
    """Clear the input buffer without committing."""
```

---

## OutputAudioBufferResource

Manage audio output buffer.

### Methods

```python
async def clear(
    *,
    event_id: Optional[str] = None
) -> None:
    """Clear pending audio output (for interrupts)."""
```

---

## ConversationResource

Manage conversation state.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `item` | `ConversationItemResource` | Item operations |

---

## ConversationItemResource

CRUD operations on conversation items.

### Methods

```python
async def create(
    *,
    item: Union[ConversationRequestItem, Mapping[str, Any]],
    previous_item_id: Optional[str] = None,
    event_id: Optional[str] = None
) -> None:
    """Create a new conversation item."""

async def delete(
    *,
    item_id: str,
    event_id: Optional[str] = None
) -> None:
    """Delete a conversation item."""

async def retrieve(
    *,
    item_id: str,
    event_id: Optional[str] = None
) -> None:
    """Retrieve item details (server responds with event)."""

async def truncate(
    *,
    item_id: str,
    audio_end_ms: int,
    content_index: int,
    event_id: Optional[str] = None
) -> None:
    """Truncate audio at specified time."""
```

### ConversationRequestItem Types

```python
# User/Assistant/System message
{
    "type": "message",
    "role": "user" | "assistant" | "system",
    "content": [
        {"type": "input_text", "text": "..."},
        {"type": "input_audio", "audio": "base64..."},
        {"type": "text", "text": "..."},
        {"type": "audio", "audio": "base64...", "transcript": "..."}
    ]
}

# Function call (from model)
{
    "type": "function_call",
    "call_id": "...",
    "name": "function_name",
    "arguments": "{...}"
}

# Function output (from client)
{
    "type": "function_call_output",
    "call_id": "...",
    "output": "{...}"
}
```

---

## TranscriptionSessionResource

Configure input transcription.

### Methods

```python
async def update(
    *,
    session: Mapping[str, Any],
    event_id: Optional[str] = None
) -> None:
    """Update transcription session configuration."""
```

---

## WebsocketConnectionOptions

Transport configuration for the WebSocket connection.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `compression` | `bool` or `int` | None | Enable per-message compression |
| `max_msg_size` | `int` | 4MB | Maximum message size |
| `heartbeat` | `float` | 30 | Keep-alive ping interval (seconds) |
| `autoclose` | `bool` | True | Auto-close on close frame |
| `autoping` | `bool` | True | Auto-respond to pings |
| `receive_timeout` | `float` | None | Message receive timeout |
| `close_timeout` | `float` | None | Close handshake timeout |
| `handshake_timeout` | `float` | None | Connection establishment timeout |
| `vendor_options` | `Mapping` | None | Implementation-specific options |

---

## Exceptions

```python
from azure.ai.voicelive.aio import ConnectionError, ConnectionClosed

class ConnectionError(AzureError):
    """Base WebSocket connection error."""

class ConnectionClosed(ConnectionError):
    """WebSocket connection was closed."""
    code: int      # Close code
    reason: str    # Close reason
```

### Common Close Codes

| Code | Meaning |
|------|---------|
| 1000 | Normal closure |
| 1001 | Going away |
| 1006 | Abnormal closure |
| 1008 | Policy violation |
| 1011 | Server error |
