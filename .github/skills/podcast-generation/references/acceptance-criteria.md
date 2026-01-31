# Podcast Generation Acceptance Criteria

**Tool**: Azure OpenAI GPT Realtime Mini
**Repository**: https://github.com/openai/openai-python
**Purpose**: Skill testing acceptance criteria for validating podcast generation code

---

## 1. Environment Configuration

### 1.1 Required Environment Variables

#### ✅ CORRECT: Proper environment configuration
```python
import os

api_key = os.environ["AZURE_OPENAI_AUDIO_API_KEY"]
endpoint = os.environ["AZURE_OPENAI_AUDIO_ENDPOINT"]  # Base URL only
deployment = os.environ.get("AZURE_OPENAI_AUDIO_DEPLOYMENT", "gpt-realtime-mini")
```

#### ❌ INCORRECT: Hardcoded credentials
```python
api_key = "sk-hardcoded-key"
endpoint = "https://my-resource.cognitiveservices.azure.com"
```

---

## 2. WebSocket Connection

### 2.1 URL Construction

#### ✅ CORRECT: Convert HTTPS to WSS
```python
ws_url = endpoint.replace("https://", "wss://") + "/openai/v1"
```

#### ❌ INCORRECT: Using HTTPS for WebSocket
```python
ws_url = endpoint + "/openai/v1"  # Wrong - needs wss://
```

---

## 3. Client Initialization

### 3.1 AsyncOpenAI Setup

#### ✅ CORRECT: Proper async client setup
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    websocket_base_url=ws_url,
    api_key=api_key
)
```

#### ❌ INCORRECT: Using sync client for realtime
```python
from openai import OpenAI

client = OpenAI(api_key=api_key)  # Wrong - need AsyncOpenAI for realtime
```

---

## 4. Session Configuration

### 4.1 Audio Output Configuration

#### ✅ CORRECT: Configure for audio-only output
```python
async with client.realtime.connect(model="gpt-realtime-mini") as conn:
    await conn.session.update(session={
        "output_modalities": ["audio"],
        "instructions": "You are a narrator. Speak naturally and clearly."
    })
```

#### ✅ CORRECT: With voice selection
```python
await conn.session.update(session={
    "output_modalities": ["audio"],
    "voice": "alloy",  # or echo, fable, onyx, nova, shimmer
    "instructions": "You are a podcast host."
})
```

#### ❌ INCORRECT: Missing output modalities
```python
await conn.session.update(session={
    "instructions": "Narrate this."
    # Missing output_modalities - may not get audio
})
```

---

## 5. Message Sending

### 5.1 Conversation Item Creation

#### ✅ CORRECT: Send text for narration
```python
await conn.conversation.item.create(item={
    "type": "message",
    "role": "user",
    "content": [{"type": "input_text", "text": prompt}]
})

await conn.response.create()
```

#### ❌ INCORRECT: Wrong message format
```python
await conn.send_message(prompt)  # Wrong method
```

---

## 6. Event Handling

### 6.1 Streaming Event Types

#### ✅ CORRECT: Handle audio and transcript events
```python
import base64

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

#### ❌ INCORRECT: Missing error handling
```python
async for event in conn:
    if event.type == "response.output_audio.delta":
        audio_chunks.append(event.delta)  # Missing base64 decode
    # Missing error event handling
```

---

## 7. Audio Processing

### 7.1 PCM to WAV Conversion

#### ✅ CORRECT: Convert PCM to WAV format
```python
import struct
import io

def pcm_to_wav(pcm_data: bytes, sample_rate: int = 24000, channels: int = 1, bits_per_sample: int = 16) -> bytes:
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    data_size = len(pcm_data)
    
    buffer = io.BytesIO()
    
    # RIFF header
    buffer.write(b'RIFF')
    buffer.write(struct.pack('<I', 36 + data_size))
    buffer.write(b'WAVE')
    
    # fmt chunk
    buffer.write(b'fmt ')
    buffer.write(struct.pack('<I', 16))  # Chunk size
    buffer.write(struct.pack('<H', 1))   # Audio format (PCM)
    buffer.write(struct.pack('<H', channels))
    buffer.write(struct.pack('<I', sample_rate))
    buffer.write(struct.pack('<I', byte_rate))
    buffer.write(struct.pack('<H', block_align))
    buffer.write(struct.pack('<H', bits_per_sample))
    
    # data chunk
    buffer.write(b'data')
    buffer.write(struct.pack('<I', data_size))
    buffer.write(pcm_data)
    
    return buffer.getvalue()
```

#### ❌ INCORRECT: Missing WAV header
```python
def save_audio(pcm_data, filename):
    with open(filename, 'wb') as f:
        f.write(pcm_data)  # Wrong - raw PCM won't play without WAV header
```

---

## 8. Frontend Audio Playback

### 8.1 Base64 to Blob Conversion

#### ✅ CORRECT: Convert and play audio
```javascript
const base64ToBlob = (base64, mimeType) => {
  const bytes = atob(base64);
  const arr = new Uint8Array(bytes.length);
  for (let i = 0; i < bytes.length; i++) {
    arr[i] = bytes.charCodeAt(i);
  }
  return new Blob([arr], { type: mimeType });
};

const audioBlob = base64ToBlob(response.audio_data, 'audio/wav');
const audioUrl = URL.createObjectURL(audioBlob);
const audio = new Audio(audioUrl);
audio.play();
```

#### ❌ INCORRECT: Direct base64 as src
```javascript
const audio = new Audio(`data:audio/wav;base64,${response.audio_data}`);
// May fail for large files - use Blob instead
```

---

## 9. Voice Options

### 9.1 Available Voices

#### ✅ CORRECT: Valid voice names
```python
valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

await conn.session.update(session={
    "voice": "alloy",  # Neutral voice
    "output_modalities": ["audio"]
})
```

#### ❌ INCORRECT: Invalid voice name
```python
await conn.session.update(session={
    "voice": "custom-voice",  # Invalid - not a supported voice
})
```

---

## 10. Audio Format Specifications

### 10.1 Output Format

#### ✅ CORRECT: Format parameters
```python
# Realtime API output format
SAMPLE_RATE = 24000      # 24 kHz
BITS_PER_SAMPLE = 16     # 16-bit
CHANNELS = 1             # Mono

pcm_audio = b''.join(audio_chunks)
wav_audio = pcm_to_wav(pcm_audio, sample_rate=SAMPLE_RATE)
```

#### ❌ INCORRECT: Wrong sample rate
```python
wav_audio = pcm_to_wav(pcm_audio, sample_rate=44100)  # Wrong - API outputs 24kHz
```
