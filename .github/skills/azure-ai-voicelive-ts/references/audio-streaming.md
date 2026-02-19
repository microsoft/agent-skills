# Audio Streaming Reference

Real-time audio capture and playback patterns for Azure AI Voice Live using the @azure/ai-voicelive TypeScript SDK.

## Overview

Voice Live requires bidirectional audio streaming over WebSocket. This reference covers browser microphone capture, PCM format conversion, and audio playback patterns for voice assistants.

## Audio Format Requirements

| Property | Default Value | Options |
|----------|---------------|---------|
| `inputAudioFormat` | `"pcm16"` | `"pcm16"`, `"g711_alaw"`, `"g711_ulaw"` |
| `outputAudioFormat` | `"pcm16"` | `"pcm16"` |
| Sample Rate (pcm16) | 24000 Hz | 8000, 16000, 24000 |
| Channels | Mono (1) | - |

### Sample Rate Inference

```typescript
function inferPcmSampleRateFromOutputFormat(outputAudioFormat: string | undefined): number {
  if (!outputAudioFormat) return 24000;
  const fmt = outputAudioFormat.toLowerCase();
  if (fmt === "pcm16") return 24000;
  if (fmt === "pcm16-16000hz") return 16000;
  if (fmt === "pcm16-8000hz") return 8000;
  return 24000;
}
```

## Browser Microphone Capture

### Pattern A: ScriptProcessorNode (Simple)

Simpler implementation but uses deprecated Web Audio API.

```typescript
export class SimpleAudioCapture {
  private audioContext?: AudioContext;
  private mediaStream?: MediaStream;
  private scriptProcessor?: ScriptProcessorNode;
  private dataCallback: (data: ArrayBuffer) => void;
  
  private readonly targetSampleRate = 24000;

  constructor(onData: (data: ArrayBuffer) => void) {
    this.dataCallback = onData;
  }

  async initialize(): Promise<void> {
    // Request microphone access
    this.mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        sampleRate: this.targetSampleRate,
        echoCancellation: true,
        noiseSuppression: true,
      },
    });

    // Create audio context at target sample rate
    this.audioContext = new AudioContext({ sampleRate: this.targetSampleRate });
    
    // Create processing chain
    const source = this.audioContext.createMediaStreamSource(this.mediaStream);
    this.scriptProcessor = this.audioContext.createScriptProcessor(4096, 1, 1);
    
    // Connect nodes
    source.connect(this.scriptProcessor);
    this.scriptProcessor.connect(this.audioContext.destination);
    
    // Process audio data
    this.scriptProcessor.onaudioprocess = (event) => {
      const inputData = event.inputBuffer.getChannelData(0);
      const pcm16Data = this.convertToPCM16(inputData);
      this.dataCallback(pcm16Data.buffer);
    };
  }

  private convertToPCM16(floatData: Float32Array): Int16Array {
    const pcm16 = new Int16Array(floatData.length);
    for (let i = 0; i < floatData.length; i++) {
      const sample = Math.max(-1, Math.min(1, floatData[i]));
      pcm16[i] = sample < 0 ? sample * 0x8000 : sample * 0x7fff;
    }
    return pcm16;
  }

  stop(): void {
    this.scriptProcessor?.disconnect();
    this.mediaStream?.getTracks().forEach((track) => track.stop());
    this.audioContext?.close();
  }
}
```

### Pattern B: AudioWorklet (Modern, Recommended)

Uses modern AudioWorklet API with better performance.

```typescript
// Main thread code
export class AudioWorkletCapture {
  private audioContext?: AudioContext;
  private mediaStream?: MediaStream;
  private workletNode?: AudioWorkletNode;
  private onAudioData: (data: Uint8Array) => void;

  constructor(onData: (data: Uint8Array) => void) {
    this.onAudioData = onData;
  }

  async start(): Promise<void> {
    const ac = new AudioContext();
    this.audioContext = ac;

    // Load AudioWorklet module
    const workletUrl = new URL("worklets/pcm16-downsampler.js", document.baseURI).toString();
    await ac.audioWorklet.addModule(workletUrl);

    // Get microphone stream
    // Disable browser processing - server handles VAD
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: false,
        noiseSuppression: false,
        autoGainControl: false,
      },
    });
    this.mediaStream = stream;

    // Create processing chain
    const source = ac.createMediaStreamSource(stream);
    const worklet = new AudioWorkletNode(ac, "pcm16-downsampler");
    this.workletNode = worklet;

    // Receive processed PCM16 data from worklet
    worklet.port.onmessage = (e) => {
      const buffer = e.data as ArrayBuffer;
      const pcm16Bytes = new Uint8Array(buffer);
      this.onAudioData(pcm16Bytes);
    };

    // Connect with muted output to prevent feedback
    const gain = ac.createGain();
    gain.gain.value = 0;
    source.connect(worklet);
    worklet.connect(gain);
    gain.connect(ac.destination);
  }

  stop(): void {
    this.workletNode?.disconnect();
    this.mediaStream?.getTracks().forEach((track) => track.stop());
    this.audioContext?.close();
  }
}
```

### AudioWorklet Processor (pcm16-downsampler.js)

Save this file in `/public/worklets/pcm16-downsampler.js`:

```javascript
class Pcm16DownsamplerProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this._targetSampleRate = 24000;
    this._inputSampleRate = sampleRate;  // Browser's native rate (e.g., 48000)
    this._ratio = this._inputSampleRate / this._targetSampleRate;
    this._carry = 0;
  }

  process(inputs) {
    const input = inputs[0];
    if (!input || input.length === 0) return true;

    const channel0 = input[0];
    if (!channel0 || channel0.length === 0) return true;

    // Downsample by averaging
    const outLength = Math.max(0, Math.floor((channel0.length - this._carry) / this._ratio));
    if (outLength === 0) return true;

    const pcm16 = new Int16Array(outLength);
    let outIndex = 0;
    let i = this._carry;

    while (outIndex < outLength) {
      const start = Math.floor(i);
      const end = Math.floor(i + this._ratio);

      let sum = 0, count = 0;
      for (let j = start; j < end && j < channel0.length; j++) {
        sum += channel0[j];
        count++;
      }

      const sample = count > 0 ? sum / count : 0;
      const clamped = Math.max(-1, Math.min(1, sample));
      pcm16[outIndex] = clamped < 0 ? clamped * 0x8000 : clamped * 0x7fff;

      outIndex++;
      i += this._ratio;
    }

    this._carry = i - channel0.length;
    if (this._carry < 0) this._carry = 0;

    // Transfer buffer to main thread
    this.port.postMessage(pcm16.buffer, [pcm16.buffer]);
    return true;
  }
}

registerProcessor("pcm16-downsampler", Pcm16DownsamplerProcessor);
```

## Audio Playback

### Pattern A: AudioBufferSourceNode Queue

Simple queue-based playback using AudioBufferSourceNode.

```typescript
export class Pcm16Player {
  private readonly audioContext: AudioContext;
  private nextStartTime = 0;
  private sources: AudioBufferSourceNode[] = [];
  private sampleRate: number;

  constructor(sampleRate = 24000) {
    this.audioContext = new AudioContext();
    this.sampleRate = sampleRate;
  }

  async resume(): Promise<void> {
    if (this.audioContext.state !== "running") {
      await this.audioContext.resume();
    }
  }

  enqueuePcm16(bytes: Uint8Array): void {
    // Convert PCM16 bytes to Float32 for Web Audio API
    const floatData = this.pcm16BytesToFloat32(bytes);
    
    // Create audio buffer
    const buffer = this.audioContext.createBuffer(1, floatData.length, this.sampleRate);
    buffer.getChannelData(0).set(floatData);

    // Create and schedule source
    const src = this.audioContext.createBufferSource();
    src.buffer = buffer;
    src.connect(this.audioContext.destination);

    // Schedule seamless playback
    const now = this.audioContext.currentTime;
    if (this.nextStartTime < now) {
      this.nextStartTime = now;
    }
    const startAt = this.nextStartTime;
    this.nextStartTime += buffer.duration;

    // Track for cleanup
    src.onended = () => {
      this.sources = this.sources.filter((s) => s !== src);
    };
    this.sources.push(src);
    src.start(startAt);
  }

  private pcm16BytesToFloat32(bytes: Uint8Array): Float32Array {
    const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
    const sampleCount = Math.floor(bytes.byteLength / 2);
    const out = new Float32Array(sampleCount);
    for (let i = 0; i < sampleCount; i++) {
      const s = view.getInt16(i * 2, true);  // Little-endian
      out[i] = s / 0x8000;
    }
    return out;
  }

  stop(): void {
    for (const s of this.sources) {
      try {
        s.stop();
      } catch {
        /* ignore */
      }
    }
    this.sources = [];
    this.nextStartTime = 0;
  }
}
```

### Pattern B: AudioWorklet Playback

Better for handling barge-in (user interrupts assistant).

```javascript
// audio-playback-worklet.js
class AudioPlaybackWorklet extends AudioWorkletProcessor {
  constructor() {
    super();
    this.port.onmessage = this.handleMessage.bind(this);
    this.buffer = [];
  }

  handleMessage(event) {
    if (event.data === null) {
      // Clear buffer on barge-in
      this.buffer = [];
      return;
    }
    // Append Int16 samples
    this.buffer.push(...event.data);
  }

  process(inputs, outputs) {
    const output = outputs[0];
    const channel = output[0];

    if (this.buffer.length > channel.length) {
      const toProcess = this.buffer.slice(0, channel.length);
      this.buffer = this.buffer.slice(channel.length);
      channel.set(toProcess.map((v) => v / 32768));  // Int16 to Float32
    } else {
      channel.set(this.buffer.map((v) => v / 32768));
      this.buffer = [];
    }

    return true;
  }
}

registerProcessor("audio-playback-worklet", AudioPlaybackWorklet);
```

## PCM16 Conversion Utilities

```typescript
// Float32 to PCM16 (for sending to server)
export function floatTo16BitPCM(input: Float32Array): Int16Array {
  const output = new Int16Array(input.length);
  for (let i = 0; i < input.length; i++) {
    const s = Math.max(-1, Math.min(1, input[i] ?? 0));
    output[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }
  return output;
}

// PCM16 bytes to Float32 (for playback)
export function pcm16BytesToFloat32LE(bytes: Uint8Array): Float32Array {
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const sampleCount = Math.floor(bytes.byteLength / 2);
  const out = new Float32Array(sampleCount);
  for (let i = 0; i < sampleCount; i++) {
    const s = view.getInt16(i * 2, true);  // Little-endian
    out[i] = s / 0x8000;
  }
  return out;
}

// Int16Array to Uint8Array (for sendAudio)
export function int16ToUint8(int16Array: Int16Array): Uint8Array {
  return new Uint8Array(int16Array.buffer);
}
```

## Integration with VoiceLiveSession

```typescript
import { VoiceLiveClient } from "@azure/ai-voicelive";
import { DefaultAzureCredential } from "@azure/identity";

const client = new VoiceLiveClient(endpoint, new DefaultAzureCredential());
const session = await client.startSession("gpt-4o-mini-realtime-preview");

// Configure audio formats
await session.updateSession({
  modalities: ["audio", "text"],
  inputAudioFormat: "pcm16",
  outputAudioFormat: "pcm16",
  turnDetection: {
    type: "server_vad",
    threshold: 0.5,
    silenceDurationMs: 500,
  },
});

// Initialize audio capture and playback
const player = new Pcm16Player(24000);
const capture = new AudioWorkletCapture((data) => {
  session.sendAudio(data);
});

// Handle audio output from assistant
const subscription = session.subscribe({
  onResponseAudioDelta: async (event) => {
    player.enqueuePcm16(event.delta);
  },
  onInputAudioBufferSpeechStarted: async () => {
    // User started speaking - stop playback (barge-in)
    player.stop();
  },
});

// Start capture
await capture.start();
await player.resume();

// Cleanup
async function cleanup() {
  capture.stop();
  player.stop();
  await subscription.close();
  await session.close();
}
```

## Best Practices

1. **Use AudioWorklet over ScriptProcessorNode** - Better performance and officially supported
2. **Disable browser audio processing** - Set `echoCancellation: false` when server handles VAD
3. **Handle barge-in** - Clear playback buffer when user starts speaking
4. **Match sample rates** - Ensure capture matches server expectation (usually 24kHz)
5. **Use transferable objects** - Pass `ArrayBuffer` with transfer list for efficiency
6. **Resume AudioContext on user gesture** - Browser policy requires user interaction

## See Also

- [Function Calling Reference](./function-calling.md)
- [SKILL.md](../SKILL.md) - Main skill documentation
- [Azure Voice Live Samples](https://github.com/microsoft-foundry/voicelive-samples)
