# Podcast Generation Acceptance Criteria

**Skill**: `podcast-generation`
**Purpose**: Generate AI-powered podcast-style audio narratives using Azure OpenAI's GPT Realtime Mini model
**Focus**: Script generation, text-to-speech, audio processing, WebSocket streaming

---

## 1. Environment Configuration

### 1.1 ✅ CORRECT: Environment Variables

```bash
AZURE_OPENAI_AUDIO_API_KEY=your_realtime_api_key
AZURE_OPENAI_AUDIO_ENDPOINT=https://your-resource.cognitiveservices.azure.com
AZURE_OPENAI_AUDIO_DEPLOYMENT=gpt-realtime-mini
```

### 1.2 ✅ CORRECT: Endpoint Format

```python
# Correct - base URL without path
endpoint = "https://my-resource.cognitiveservices.azure.com"
```

### 1.3 ❌ INCORRECT: Wrong Endpoint Format

```python
# WRONG - includes API path
endpoint = "https://my-resource.cognitiveservices.azure.com/openai/v1/"
```

---

## 2. WebSocket Connection

### 2.1 ✅ CORRECT: WebSocket URL Conversion

```python
from openai import AsyncOpenAI

# Convert HTTPS to WSS for Realtime API
endpoint = os.environ["AZURE_OPENAI_AUDIO_ENDPOINT"]
ws_url = endpoint.replace("https://", "wss://") + "/openai/v1"

client = AsyncOpenAI(
    websocket_base_url=ws_url,
    api_key=os.environ["AZURE_OPENAI_AUDIO_API_KEY"]
)
```

### 2.2 ❌ INCORRECT: Using HTTPS for Realtime

```python
# WRONG - Realtime API requires WebSocket, not HTTPS
client = AsyncOpenAI(
    base_url=endpoint + "/openai/v1",  # Should be websocket_base_url with wss://
    api_key=api_key
)
```

---

## 3. Session Configuration

### 3.1 ✅ CORRECT: Audio Output Configuration

```python
async with client.realtime.connect(model="gpt-realtime-mini") as conn:
    await conn.session.update(session={
        "output_modalities": ["audio"],
        "instructions": "You are a professional podcast narrator. Speak naturally and engagingly.",
        "voice": "alloy"
    })
```

### 3.2 ✅ CORRECT: Voice Selection

| Voice | Character | Best For |
|-------|-----------|----------|
| alloy | Neutral | General content |
| echo | Warm | Conversational |
| fable | Expressive | Storytelling |
| onyx | Deep | Authoritative |
| nova | Friendly | Casual content |
| shimmer | Clear | Educational |

### 3.3 ❌ INCORRECT: Missing Output Modality

```python
# WRONG - Must specify output_modalities for audio
await conn.session.update(session={
    "instructions": "Narrate this content"
    # Missing: "output_modalities": ["audio"]
})
```

---

## 4. Sending Content for Narration

### 4.1 ✅ CORRECT: Conversation Item Creation

```python
await conn.conversation.item.create(item={
    "type": "message",
    "role": "user",
    "content": [{
        "type": "input_text",
        "text": "Please narrate the following content: " + script
    }]
})

await conn.response.create()
```

### 4.2 ❌ INCORRECT: Wrong Content Type

```python
# WRONG - Should use "input_text" for text-to-audio
await conn.conversation.item.create(item={
    "type": "message",
    "role": "user",
    "content": [{
        "type": "text",  # Should be "input_text"
        "text": script
    }]
})
```

---

## 5. Event Handling

### 5.1 ✅ CORRECT: Streaming Event Processing

```python
audio_chunks = []
transcript_parts = []

async for event in conn:
    if event.type == "response.output_audio.delta":
        audio_chunks.append(base64.b64decode(event.delta))
    elif event.type == "response.output_audio_transcript.delta":
        transcript_parts.append(event.delta)
    elif event.type == "response.done":
        break
    elif event.type == "error":
        raise Exception(f"Realtime API error: {event.error.message}")
```

### 5.2 Event Types

| Event Type | Content | Usage |
|------------|---------|-------|
| `response.output_audio.delta` | Base64 audio chunk | Collect for PCM audio |
| `response.output_audio_transcript.delta` | Transcript text | Build text transcript |
| `response.done` | None | End of response |
| `error` | Error details | Handle failures |

### 5.3 ❌ INCORRECT: Missing Error Handling

```python
# WRONG - No error handling
async for event in conn:
    if event.type == "response.output_audio.delta":
        audio_chunks.append(base64.b64decode(event.delta))
    # Missing: error event handling
```

---

## 6. Audio Format Conversion

### 6.1 ✅ CORRECT: PCM to WAV Conversion

```python
import struct

def pcm_to_wav(pcm_data: bytes, sample_rate: int = 24000) -> bytes:
    """Convert raw PCM audio to WAV format.
    
    Args:
        pcm_data: Raw PCM audio bytes (16-bit, mono)
        sample_rate: Sample rate in Hz (24000 for Realtime API)
    
    Returns:
        WAV file bytes
    """
    num_channels = 1
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = len(pcm_data)
    
    wav_header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        36 + data_size,
        b'WAVE',
        b'fmt ',
        16,  # Subchunk1Size
        1,   # AudioFormat (PCM)
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b'data',
        data_size
    )
    
    return wav_header + pcm_data
```

### 6.2 ✅ CORRECT: Audio Assembly

```python
# Combine all audio chunks
pcm_audio = b''.join(audio_chunks)

# Convert to WAV
wav_audio = pcm_to_wav(pcm_audio, sample_rate=24000)

# Encode for transport
audio_base64 = base64.b64encode(wav_audio).decode('utf-8')
```

### 6.3 ❌ INCORRECT: Wrong Sample Rate

```python
# WRONG - Realtime API uses 24kHz, not 44.1kHz
wav_audio = pcm_to_wav(pcm_audio, sample_rate=44100)
```

---

## 7. Frontend Audio Playback

### 7.1 ✅ CORRECT: Base64 to Blob Conversion

```javascript
const base64ToBlob = (base64, mimeType) => {
  const bytes = atob(base64);
  const arr = new Uint8Array(bytes.length);
  for (let i = 0; i < bytes.length; i++) {
    arr[i] = bytes.charCodeAt(i);
  }
  return new Blob([arr], { type: mimeType });
};

// Usage
const audioBlob = base64ToBlob(response.audio_data, 'audio/wav');
const audioUrl = URL.createObjectURL(audioBlob);
const audio = new Audio(audioUrl);
audio.play();
```

### 7.2 ✅ CORRECT: React Audio Player Component

```typescript
const AudioPlayer: React.FC<{ audioData: string }> = ({ audioData }) => {
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  useEffect(() => {
    if (audioData) {
      const blob = base64ToBlob(audioData, 'audio/wav');
      const url = URL.createObjectURL(blob);
      setAudioUrl(url);
      
      return () => URL.revokeObjectURL(url);
    }
  }, [audioData]);

  return audioUrl ? <audio controls src={audioUrl} /> : null;
};
```

### 7.3 ❌ INCORRECT: Memory Leak

```javascript
// WRONG - Never revokes object URL
const playAudio = (base64) => {
  const blob = base64ToBlob(base64, 'audio/wav');
  const url = URL.createObjectURL(blob);  // Memory leak if not revoked
  new Audio(url).play();
  // Missing: URL.revokeObjectURL(url) after playback
};
```

---

## 8. FastAPI Backend Integration

### 8.1 ✅ CORRECT: Podcast Generation Endpoint

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["podcast"])

class PodcastRequest(BaseModel):
    script: str
    voice: str = "alloy"

class PodcastResponse(BaseModel):
    audio_data: str  # Base64 WAV
    transcript: str
    duration_seconds: float

@router.post("/podcast/generate", response_model=PodcastResponse)
async def generate_podcast(request: PodcastRequest) -> PodcastResponse:
    """Generate podcast audio from script."""
    try:
        audio_data, transcript = await generate_audio(
            script=request.script,
            voice=request.voice
        )
        
        return PodcastResponse(
            audio_data=audio_data,
            transcript=transcript,
            duration_seconds=calculate_duration(audio_data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 8.2 ❌ INCORRECT: No Error Handling

```python
# WRONG - No error handling for API failures
@router.post("/podcast/generate")
async def generate_podcast(request: PodcastRequest):
    return await generate_audio(request.script)
    # Missing: try/except, HTTPException
```

---

## 9. Script Generation

### 9.1 ✅ CORRECT: Podcast Script Prompt

```python
script_prompt = """
Create a podcast script about the following topic. The script should:
- Have a natural, conversational tone
- Include transitions between sections
- Be approximately 3-5 minutes when spoken
- Avoid technical jargon unless explained

Topic: {topic}

Format the script as plain text ready for narration.
"""
```

### 9.2 ✅ CORRECT: Multi-Voice Script

```python
class ScriptSection(BaseModel):
    speaker: str  # "host", "guest", "narrator"
    text: str
    voice: str  # "alloy", "echo", "nova", etc.

async def generate_multi_voice_podcast(sections: list[ScriptSection]) -> bytes:
    """Generate podcast with multiple voices."""
    all_audio = []
    
    for section in sections:
        audio = await generate_audio(
            script=section.text,
            voice=section.voice
        )
        all_audio.append(audio)
    
    return concatenate_audio(all_audio)
```

---

## 10. Complete Workflow

### 10.1 ✅ CORRECT: Full Generation Flow

```python
async def generate_podcast(script: str, voice: str = "alloy") -> tuple[str, str]:
    """Generate podcast audio from script.
    
    Args:
        script: Text to convert to speech
        voice: Voice selection (alloy, echo, fable, onyx, nova, shimmer)
    
    Returns:
        Tuple of (base64_audio, transcript)
    """
    endpoint = os.environ["AZURE_OPENAI_AUDIO_ENDPOINT"]
    api_key = os.environ["AZURE_OPENAI_AUDIO_API_KEY"]
    
    ws_url = endpoint.replace("https://", "wss://") + "/openai/v1"
    
    client = AsyncOpenAI(
        websocket_base_url=ws_url,
        api_key=api_key
    )
    
    audio_chunks = []
    transcript_parts = []
    
    async with client.realtime.connect(model="gpt-realtime-mini") as conn:
        await conn.session.update(session={
            "output_modalities": ["audio"],
            "voice": voice,
            "instructions": "You are a podcast narrator. Read the following content naturally."
        })
        
        await conn.conversation.item.create(item={
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": script}]
        })
        
        await conn.response.create()
        
        async for event in conn:
            if event.type == "response.output_audio.delta":
                audio_chunks.append(base64.b64decode(event.delta))
            elif event.type == "response.output_audio_transcript.delta":
                transcript_parts.append(event.delta)
            elif event.type == "response.done":
                break
            elif event.type == "error":
                raise Exception(f"Audio generation failed: {event.error.message}")
    
    pcm_audio = b''.join(audio_chunks)
    wav_audio = pcm_to_wav(pcm_audio, sample_rate=24000)
    audio_base64 = base64.b64encode(wav_audio).decode('utf-8')
    transcript = ''.join(transcript_parts)
    
    return audio_base64, transcript
```

---

## 11. Anti-Patterns Summary

| Anti-Pattern | Impact | Fix |
|--------------|--------|-----|
| HTTPS instead of WSS | Connection fails | Use `wss://` for Realtime API |
| Wrong sample rate | Audio distortion | Use 24000 Hz |
| Missing output_modalities | No audio generated | Set `["audio"]` in session |
| No error event handling | Silent failures | Handle error events |
| Object URL memory leak | Memory bloat | Call `revokeObjectURL` |
| Wrong content type | Request fails | Use `input_text` type |

---

## 12. Checklist for Podcast Generation

- [ ] Environment variables configured (endpoint, API key, deployment)
- [ ] WebSocket URL uses `wss://` protocol
- [ ] Session configured with `output_modalities: ["audio"]`
- [ ] Voice selected from available options
- [ ] Audio chunks collected from `response.output_audio.delta`
- [ ] Transcript captured from `response.output_audio_transcript.delta`
- [ ] Error events handled properly
- [ ] PCM converted to WAV with 24kHz sample rate
- [ ] Frontend revokes object URLs after playback
- [ ] API endpoint has proper error handling with HTTPException
