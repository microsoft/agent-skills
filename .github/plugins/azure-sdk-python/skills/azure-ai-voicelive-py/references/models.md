# Azure AI Voice Live SDK - Models Reference

## Table of Contents
- [Enums](#enums)
- [Client Events](#client-events)
- [Server Events](#server-events)
- [Session Models](#session-models)
- [Conversation Items](#conversation-items)
- [Content Parts](#content-parts)
- [Tools](#tools)
- [Voice Models](#voice-models)
- [Turn Detection](#turn-detection)
- [Response Models](#response-models)
- [Avatar Models](#avatar-models)

---

## Enums

### Modality
```python
class Modality(str, Enum):
    TEXT = "text"
    AUDIO = "audio"
    ANIMATION = "animation"
    AVATAR = "avatar"
```

### OpenAIVoiceName
```python
class OpenAIVoiceName(str, Enum):
    ALLOY = "alloy"
    ASH = "ash"
    BALLAD = "ballad"
    CORAL = "coral"
    ECHO = "echo"
    SAGE = "sage"
    SHIMMER = "shimmer"
    VERSE = "verse"
    MARIN = "marin"
    CEDAR = "cedar"
```

### InputAudioFormat
```python
class InputAudioFormat(str, Enum):
    PCM16 = "pcm16"           # 24kHz default
    G711_ULAW = "g711_ulaw"   # 8kHz
    G711_ALAW = "g711_alaw"   # 8kHz
```

### OutputAudioFormat
```python
class OutputAudioFormat(str, Enum):
    PCM16 = "pcm16"               # 24kHz
    PCM16_8000_HZ = "pcm16-8000hz"
    PCM16_16000_HZ = "pcm16-16000hz"
    G711_ULAW = "g711_ulaw"       # 8kHz
    G711_ALAW = "g711_alaw"       # 8kHz
```

### TurnDetectionType
```python
class TurnDetectionType(str, Enum):
    SERVER_VAD = "server_vad"
    AZURE_SEMANTIC_VAD = "azure_semantic_vad"
    AZURE_SEMANTIC_VAD_EN = "azure_semantic_vad_en"
    AZURE_SEMANTIC_VAD_MULTILINGUAL = "azure_semantic_vad_multilingual"
```

### MessageRole
```python
class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
```

### ItemType
```python
class ItemType(str, Enum):
    MESSAGE = "message"
    FUNCTION_CALL = "function_call"
    FUNCTION_CALL_OUTPUT = "function_call_output"
    MCP_LIST_TOOLS = "mcp_list_tools"
    MCP_CALL = "mcp_call"
    MCP_APPROVAL_REQUEST = "mcp_approval_request"
    MCP_APPROVAL_RESPONSE = "mcp_approval_response"
```

### ContentPartType
```python
class ContentPartType(str, Enum):
    INPUT_TEXT = "input_text"
    INPUT_AUDIO = "input_audio"
    INPUT_IMAGE = "input_image"
    TEXT = "text"
    AUDIO = "audio"
```

### ToolType
```python
class ToolType(str, Enum):
    FUNCTION = "function"
    MCP = "mcp"
```

### ToolChoiceLiteral
```python
class ToolChoiceLiteral(str, Enum):
    AUTO = "auto"
    NONE = "none"
    REQUIRED = "required"
```

### ResponseStatus
```python
class ResponseStatus(str, Enum):
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    INCOMPLETE = "incomplete"
    IN_PROGRESS = "in_progress"
```

### ClientEventType
```python
class ClientEventType(str, Enum):
    SESSION_UPDATE = "session.update"
    INPUT_AUDIO_BUFFER_APPEND = "input_audio_buffer.append"
    INPUT_AUDIO_BUFFER_COMMIT = "input_audio_buffer.commit"
    INPUT_AUDIO_BUFFER_CLEAR = "input_audio_buffer.clear"
    INPUT_AUDIO_TURN_START = "input_audio.turn.start"
    INPUT_AUDIO_TURN_APPEND = "input_audio.turn.append"
    INPUT_AUDIO_TURN_END = "input_audio.turn.end"
    INPUT_AUDIO_TURN_CANCEL = "input_audio.turn.cancel"
    INPUT_AUDIO_CLEAR = "input_audio.clear"
    CONVERSATION_ITEM_CREATE = "conversation.item.create"
    CONVERSATION_ITEM_RETRIEVE = "conversation.item.retrieve"
    CONVERSATION_ITEM_TRUNCATE = "conversation.item.truncate"
    CONVERSATION_ITEM_DELETE = "conversation.item.delete"
    RESPONSE_CREATE = "response.create"
    RESPONSE_CANCEL = "response.cancel"
    SESSION_AVATAR_CONNECT = "session.avatar.connect"
    MCP_APPROVAL_RESPONSE = "mcp_approval_response"
```

### ServerEventType
```python
class ServerEventType(str, Enum):
    ERROR = "error"
    SESSION_AVATAR_CONNECTING = "session.avatar.connecting"
    SESSION_CREATED = "session.created"
    SESSION_UPDATED = "session.updated"
    CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED = "conversation.item.input_audio_transcription.completed"
    CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_DELTA = "conversation.item.input_audio_transcription.delta"
    CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_FAILED = "conversation.item.input_audio_transcription.failed"
    CONVERSATION_ITEM_CREATED = "conversation.item.created"
    CONVERSATION_ITEM_RETRIEVED = "conversation.item.retrieved"
    CONVERSATION_ITEM_TRUNCATED = "conversation.item.truncated"
    CONVERSATION_ITEM_DELETED = "conversation.item.deleted"
    INPUT_AUDIO_BUFFER_COMMITTED = "input_audio_buffer.committed"
    INPUT_AUDIO_BUFFER_CLEARED = "input_audio_buffer.cleared"
    INPUT_AUDIO_BUFFER_SPEECH_STARTED = "input_audio_buffer.speech_started"
    INPUT_AUDIO_BUFFER_SPEECH_STOPPED = "input_audio_buffer.speech_stopped"
    RESPONSE_CREATED = "response.created"
    RESPONSE_DONE = "response.done"
    RESPONSE_OUTPUT_ITEM_ADDED = "response.output_item.added"
    RESPONSE_OUTPUT_ITEM_DONE = "response.output_item.done"
    RESPONSE_CONTENT_PART_ADDED = "response.content_part.added"
    RESPONSE_CONTENT_PART_DONE = "response.content_part.done"
    RESPONSE_TEXT_DELTA = "response.text.delta"
    RESPONSE_TEXT_DONE = "response.text.done"
    RESPONSE_AUDIO_TRANSCRIPT_DELTA = "response.audio_transcript.delta"
    RESPONSE_AUDIO_TRANSCRIPT_DONE = "response.audio_transcript.done"
    RESPONSE_AUDIO_DELTA = "response.audio.delta"
    RESPONSE_AUDIO_DONE = "response.audio.done"
    RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA = "response.function_call_arguments.delta"
    RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE = "response.function_call_arguments.done"
    # MCP events
    MCP_LIST_TOOLS_IN_PROGRESS = "mcp_list_tools.in_progress"
    MCP_LIST_TOOLS_COMPLETED = "mcp_list_tools.completed"
    MCP_LIST_TOOLS_FAILED = "mcp_list_tools.failed"
    RESPONSE_MCP_CALL_ARGUMENTS_DELTA = "response.mcp_call_arguments.delta"
    RESPONSE_MCP_CALL_ARGUMENTS_DONE = "response.mcp_call_arguments.done"
    RESPONSE_MCP_CALL_IN_PROGRESS = "response.mcp_call.in_progress"
    RESPONSE_MCP_CALL_COMPLETED = "response.mcp_call.completed"
    RESPONSE_MCP_CALL_FAILED = "response.mcp_call.failed"
    # Animation events
    RESPONSE_ANIMATION_BLENDSHAPES_DELTA = "response.animation_blendshapes.delta"
    RESPONSE_ANIMATION_BLENDSHAPES_DONE = "response.animation_blendshapes.done"
    RESPONSE_ANIMATION_VISEME_DELTA = "response.animation_viseme.delta"
    RESPONSE_ANIMATION_VISEME_DONE = "response.animation_viseme.done"
    RESPONSE_AUDIO_TIMESTAMP_DELTA = "response.audio_timestamp.delta"
    RESPONSE_AUDIO_TIMESTAMP_DONE = "response.audio_timestamp.done"
```

---

## Client Events

### ClientEventSessionUpdate
```python
class ClientEventSessionUpdate(Model):
    type: Literal["session.update"]
    event_id: Optional[str]
    session: RequestSession
```

### ClientEventInputAudioBufferAppend
```python
class ClientEventInputAudioBufferAppend(Model):
    type: Literal["input_audio_buffer.append"]
    event_id: Optional[str]
    audio: str  # Base64-encoded audio
```

### ClientEventInputAudioBufferCommit
```python
class ClientEventInputAudioBufferCommit(Model):
    type: Literal["input_audio_buffer.commit"]
    event_id: Optional[str]
```

### ClientEventInputAudioBufferClear
```python
class ClientEventInputAudioBufferClear(Model):
    type: Literal["input_audio_buffer.clear"]
    event_id: Optional[str]
```

### ClientEventConversationItemCreate
```python
class ClientEventConversationItemCreate(Model):
    type: Literal["conversation.item.create"]
    event_id: Optional[str]
    previous_item_id: Optional[str]
    item: ConversationRequestItem
```

### ClientEventConversationItemDelete
```python
class ClientEventConversationItemDelete(Model):
    type: Literal["conversation.item.delete"]
    event_id: Optional[str]
    item_id: str
```

### ClientEventConversationItemTruncate
```python
class ClientEventConversationItemTruncate(Model):
    type: Literal["conversation.item.truncate"]
    event_id: Optional[str]
    item_id: str
    content_index: int
    audio_end_ms: int
```

### ClientEventResponseCreate
```python
class ClientEventResponseCreate(Model):
    type: Literal["response.create"]
    event_id: Optional[str]
    response: Optional[ResponseCreateParams]
    additional_instructions: Optional[str]
```

### ClientEventResponseCancel
```python
class ClientEventResponseCancel(Model):
    type: Literal["response.cancel"]
    event_id: Optional[str]
    response_id: Optional[str]
```

---

## Server Events

### ServerEventSessionCreated
```python
class ServerEventSessionCreated(Model):
    type: Literal["session.created"]
    event_id: str
    session: ResponseSession
```

### ServerEventSessionUpdated
```python
class ServerEventSessionUpdated(Model):
    type: Literal["session.updated"]
    event_id: str
    session: ResponseSession
```

### ServerEventError
```python
class ServerEventError(Model):
    type: Literal["error"]
    event_id: str
    error: ServerEventErrorDetails

class ServerEventErrorDetails(Model):
    type: str
    code: Optional[str]
    message: str
    param: Optional[str]
```

### ServerEventInputAudioBufferSpeechStarted
```python
class ServerEventInputAudioBufferSpeechStarted(Model):
    type: Literal["input_audio_buffer.speech_started"]
    event_id: str
    audio_start_ms: int
    item_id: str
```

### ServerEventInputAudioBufferSpeechStopped
```python
class ServerEventInputAudioBufferSpeechStopped(Model):
    type: Literal["input_audio_buffer.speech_stopped"]
    event_id: str
    audio_end_ms: int
    item_id: str
```

### ServerEventConversationItemInputAudioTranscriptionCompleted
```python
class ServerEventConversationItemInputAudioTranscriptionCompleted(Model):
    type: Literal["conversation.item.input_audio_transcription.completed"]
    event_id: str
    item_id: str
    content_index: int
    transcript: str
```

### ServerEventConversationItemInputAudioTranscriptionDelta
```python
class ServerEventConversationItemInputAudioTranscriptionDelta(Model):
    type: Literal["conversation.item.input_audio_transcription.delta"]
    event_id: str
    item_id: str
    content_index: int
    delta: str
```

### ServerEventResponseCreated
```python
class ServerEventResponseCreated(Model):
    type: Literal["response.created"]
    event_id: str
    response: Response
```

### ServerEventResponseDone
```python
class ServerEventResponseDone(Model):
    type: Literal["response.done"]
    event_id: str
    response: Response
```

### ServerEventResponseAudioDelta
```python
class ServerEventResponseAudioDelta(Model):
    type: Literal["response.audio.delta"]
    event_id: str
    response_id: str
    item_id: str
    output_index: int
    content_index: int
    delta: str  # Base64-encoded audio
```

### ServerEventResponseAudioTranscriptDelta
```python
class ServerEventResponseAudioTranscriptDelta(Model):
    type: Literal["response.audio_transcript.delta"]
    event_id: str
    response_id: str
    item_id: str
    output_index: int
    content_index: int
    delta: str
```

### ServerEventResponseAudioTranscriptDone
```python
class ServerEventResponseAudioTranscriptDone(Model):
    type: Literal["response.audio_transcript.done"]
    event_id: str
    response_id: str
    item_id: str
    output_index: int
    content_index: int
    transcript: str
```

### ServerEventResponseFunctionCallArgumentsDelta
```python
class ServerEventResponseFunctionCallArgumentsDelta(Model):
    type: Literal["response.function_call_arguments.delta"]
    event_id: str
    response_id: str
    item_id: str
    output_index: int
    call_id: str
    delta: str
```

### ServerEventResponseFunctionCallArgumentsDone
```python
class ServerEventResponseFunctionCallArgumentsDone(Model):
    type: Literal["response.function_call_arguments.done"]
    event_id: str
    response_id: str
    item_id: str
    output_index: int
    call_id: str
    name: str
    arguments: str
```

---

## Session Models

### RequestSession
```python
class RequestSession(Model):
    instructions: Optional[str]
    modalities: Optional[List[Modality]]
    voice: Optional[Voice]  # str, OpenAIVoiceName, OpenAIVoice, or AzureVoice
    input_audio_format: Optional[InputAudioFormat]
    output_audio_format: Optional[OutputAudioFormat]
    turn_detection: Optional[TurnDetection]
    tools: Optional[List[Tool]]
    tool_choice: Optional[ToolChoice]
    temperature: Optional[float]
    max_response_output_tokens: Optional[Union[int, Literal["inf"]]]
    input_audio_transcription: Optional[AudioInputTranscriptionOptions]
```

### ResponseSession
```python
class ResponseSession(Model):
    id: str
    object: str
    model: str
    expires_at: int
    modalities: List[Modality]
    instructions: Optional[str]
    voice: Optional[Voice]
    input_audio_format: InputAudioFormat
    output_audio_format: OutputAudioFormat
    turn_detection: Optional[TurnDetection]
    tools: List[Tool]
    tool_choice: ToolChoice
    temperature: float
    max_response_output_tokens: Optional[int]
```

### AudioInputTranscriptionOptions
```python
class AudioInputTranscriptionOptions(Model):
    model: str  # e.g., "whisper-1"
```

---

## Conversation Items

### ConversationRequestItem (Union Type)
```python
# Can be one of:
- SystemMessageItem
- UserMessageItem
- AssistantMessageItem
- FunctionCallItem
- FunctionCallOutputItem
```

### MessageItem Base
```python
class MessageItem(Model):
    type: Literal["message"]
    id: Optional[str]
    role: MessageRole
    content: List[ContentPart]
    status: Optional[ItemParamStatus]
```

### FunctionCallItem
```python
class FunctionCallItem(Model):
    type: Literal["function_call"]
    id: Optional[str]
    call_id: str
    name: str
    arguments: str
    status: Optional[ItemParamStatus]
```

### FunctionCallOutputItem
```python
class FunctionCallOutputItem(Model):
    type: Literal["function_call_output"]
    id: Optional[str]
    call_id: str
    output: str
```

---

## Content Parts

### InputTextContentPart
```python
class InputTextContentPart(Model):
    type: Literal["input_text"]
    text: str
```

### InputAudioContentPart
```python
class InputAudioContentPart(Model):
    type: Literal["input_audio"]
    audio: str  # Base64
    transcript: Optional[str]
```

### RequestTextContentPart
```python
class RequestTextContentPart(Model):
    type: Literal["text"]
    text: str
```

### RequestAudioContentPart
```python
class RequestAudioContentPart(Model):
    type: Literal["audio"]
    audio: str  # Base64
    transcript: Optional[str]
```

### RequestImageContentPart
```python
class RequestImageContentPart(Model):
    type: Literal["input_image"]
    url: Optional[str]
    base64: Optional[str]
    detail: Optional[RequestImageContentPartDetail]  # "auto", "low", "high"
```

---

## Tools

### FunctionTool
```python
class FunctionTool(Model):
    type: Literal["function"]
    name: str
    description: Optional[str]
    parameters: Optional[dict]  # JSON Schema
```

### MCPTool
```python
class MCPTool(Model):
    type: Literal["mcp"]
    server_label: str
    require_approval: Optional[MCPApprovalType]  # "never" or "always"
```

### MCPServer
```python
class MCPServer(Model):
    type: Literal["url"]
    url: str
    name: str
    tool_configuration: Optional[dict]
```

### ToolChoiceSelection
```python
class ToolChoiceSelection(Model):
    type: Literal["function"]
    name: str
```

---

## Voice Models

### OpenAIVoice
```python
class OpenAIVoice(Model):
    type: Literal["openai"]
    name: OpenAIVoiceName
```

### AzureStandardVoice
```python
class AzureStandardVoice(Model):
    type: Literal["azure-standard"]
    name: str  # e.g., "en-US-JennyNeural"
```

### AzureCustomVoice
```python
class AzureCustomVoice(Model):
    type: Literal["azure-custom"]
    endpoint_id: str
    name: str
```

### AzurePersonalVoice
```python
class AzurePersonalVoice(Model):
    type: Literal["azure-personal"]
    speaker_profile_id: str
    model: Optional[PersonalVoiceModels]
```

---

## Turn Detection

### ServerVad
```python
class ServerVad(Model):
    type: Literal["server_vad"]
    threshold: Optional[float]  # 0.0-1.0
    prefix_padding_ms: Optional[int]
    silence_duration_ms: Optional[int]
    create_response: Optional[bool]
```

### AzureSemanticVad
```python
class AzureSemanticVad(Model):
    type: Literal["azure_semantic_vad"]
    # Uses semantic understanding for better turn detection
```

### AzureSemanticVadEn
```python
class AzureSemanticVadEn(Model):
    type: Literal["azure_semantic_vad_en"]
    eou_detection: Optional[EouDetection]
```

### EouDetection
```python
class EouDetection(Model):
    threshold_level: Optional[EouThresholdLevel]  # "low", "medium", "high", "default"
```

---

## Response Models

### Response
```python
class Response(Model):
    id: str
    object: Literal["realtime.response"]
    status: ResponseStatus
    status_details: Optional[ResponseStatusDetails]
    output: List[ResponseItem]
    usage: Optional[TokenUsage]
```

### ResponseCreateParams
```python
class ResponseCreateParams(Model):
    modalities: Optional[List[Modality]]
    instructions: Optional[str]
    voice: Optional[Voice]
    output_audio_format: Optional[OutputAudioFormat]
    tools: Optional[List[Tool]]
    tool_choice: Optional[ToolChoice]
    temperature: Optional[float]
    max_response_output_tokens: Optional[Union[int, Literal["inf"]]]
    conversation: Optional[Literal["auto", "none"]]
    input: Optional[List[ConversationRequestItem]]
```

### TokenUsage
```python
class TokenUsage(Model):
    total_tokens: int
    input_tokens: int
    output_tokens: int
    input_token_details: Optional[InputTokenDetails]
    output_token_details: Optional[OutputTokenDetails]
```

---

## Avatar Models

### AvatarConfig
```python
class AvatarConfig(Model):
    type: AvatarConfigTypes  # "video-avatar" or "photo-avatar"
    character: str
    style: Optional[str]
    output_protocol: Optional[AvatarOutputProtocol]  # "webrtc" or "websocket"
    background: Optional[Background]
    video_params: Optional[VideoParams]
```

### IceServer
```python
class IceServer(Model):
    urls: List[str]
    username: Optional[str]
    credential: Optional[str]
```

### Background
```python
class Background(Model):
    color: Optional[str]  # Hex color
    image_url: Optional[str]
```

### VideoParams
```python
class VideoParams(Model):
    resolution: Optional[VideoResolution]
    crop: Optional[VideoCrop]
```
