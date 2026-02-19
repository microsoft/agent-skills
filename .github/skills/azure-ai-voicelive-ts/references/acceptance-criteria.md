# Azure AI Voice Live SDK Acceptance Criteria (TypeScript)

**SDK**: `@azure/ai-voicelive`
**Repository**: https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/ai/ai-voicelive
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 ✅ CORRECT: Client Import
```typescript
import { VoiceLiveClient } from "@azure/ai-voicelive";
import { DefaultAzureCredential } from "@azure/identity";
```

### 1.2 ✅ CORRECT: With API Key
```typescript
import { VoiceLiveClient } from "@azure/ai-voicelive";
import { AzureKeyCredential } from "@azure/core-auth";
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong import paths
```typescript
// WRONG - VoiceLiveClient is the main export
import { Client } from "@azure/ai-voicelive";

// WRONG - no connect function like Python
import { connect } from "@azure/ai-voicelive";

// WRONG - models are not imported separately
import { ServerVad, RequestSession } from "@azure/ai-voicelive/models";
```

#### ❌ INCORRECT: Using OpenAI directly
```typescript
// WRONG - use azure-ai-voicelive SDK instead
import { OpenAI } from "openai";
```

---

## 2. Authentication Patterns

### 2.1 ✅ CORRECT: DefaultAzureCredential (AAD)
```typescript
import { VoiceLiveClient } from "@azure/ai-voicelive";
import { DefaultAzureCredential } from "@azure/identity";

const credential = new DefaultAzureCredential();
const endpoint = process.env.AZURE_COGNITIVE_SERVICES_ENDPOINT!;

const client = new VoiceLiveClient(endpoint, credential);
```

### 2.2 ✅ CORRECT: API Key Credential
```typescript
import { VoiceLiveClient } from "@azure/ai-voicelive";
import { AzureKeyCredential } from "@azure/core-auth";

const endpoint = process.env.AZURE_COGNITIVE_SERVICES_ENDPOINT!;
const credential = new AzureKeyCredential(process.env.AZURE_COGNITIVE_SERVICES_KEY!);

const client = new VoiceLiveClient(endpoint, credential);
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded API key
```typescript
// WRONG - do not hardcode secrets
const credential = new AzureKeyCredential("my-secret-key");
```

#### ❌ INCORRECT: Missing 'new' keyword
```typescript
// WRONG - VoiceLiveClient is a class
const client = VoiceLiveClient(endpoint, credential);
```

---

## 3. Session Creation Patterns

### 3.1 ✅ CORRECT: Start Session with Model
```typescript
const client = new VoiceLiveClient(endpoint, credential);
const session = await client.startSession("gpt-4o-mini-realtime-preview");
```

### 3.2 ✅ CORRECT: Configure Session
```typescript
const session = await client.startSession("gpt-4o-realtime-preview");

await session.updateSession({
  modalities: ["text", "audio"],
  instructions: "You are a helpful AI assistant. Respond naturally and conversationally.",
  voice: {
    type: "azure-standard",
    name: "en-US-AvaNeural",
  },
  turnDetection: {
    type: "server_vad",
    threshold: 0.5,
    prefixPaddingMs: 300,
    silenceDurationMs: 500,
  },
  inputAudioFormat: "pcm16",
  outputAudioFormat: "pcm16",
});
```

### 3.3 ✅ CORRECT: Custom Voice Configuration
```typescript
await session.updateSession({
  modalities: ["audio", "text"],
  instructions: "You are a customer service representative.",
  voice: {
    type: "azure-custom",
    name: "your-custom-voice-name",
    endpointId: "your-custom-voice-endpoint",
  },
  turnDetection: {
    type: "server_vad",
    threshold: 0.6,
    prefixPaddingMs: 200,
    silenceDurationMs: 300,
  },
  inputAudioFormat: "pcm16",
  outputAudioFormat: "pcm16",
});
```

### 3.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Non-existent methods
```typescript
// WRONG - session.create does not exist
await session.create({ instructions: "..." });

// WRONG - connect is not a function in TypeScript SDK
const conn = await connect(endpoint, credential, "gpt-4o-realtime-preview");
```

---

## 4. Event Handling Patterns

### 4.1 ✅ CORRECT: Subscribe to Events
```typescript
const subscription = session.subscribe({
  onResponseAudioDelta: async (event, context) => {
    // Handle incoming audio chunks
    const audioData = event.delta;
    playAudioChunk(audioData);
  },

  onResponseTextDelta: async (event, context) => {
    // Handle incoming text deltas
    console.log("Assistant:", event.delta);
  },

  onInputAudioTranscriptionCompleted: async (event, context) => {
    // Handle user speech transcription
    console.log("User said:", event.transcript);
  },
});
```

### 4.2 ✅ CORRECT: Response Done Handler
```typescript
const subscription = session.subscribe({
  onResponseDone: async (event, context) => {
    console.log("Response completed");
  },

  onError: async (event, context) => {
    console.error("Error occurred:", event);
  },
});
```

### 4.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using async for iteration
```typescript
// WRONG - TypeScript SDK uses subscribe pattern, not async iteration
for await (const event of session) {
  // Process events
}

// WRONG - async for is Python pattern
async for (const event of conn) {
  // Process events
}
```

---

## 5. Audio Streaming Patterns

### 5.1 ✅ CORRECT: Send Audio Data
```typescript
function sendAudioChunk(audioBuffer: ArrayBuffer) {
  session.sendAudio(audioBuffer);
}
```

### 5.2 ✅ CORRECT: Receive and Play Audio
```typescript
const subscription = session.subscribe({
  onResponseAudioDelta: async (event, context) => {
    // Audio comes as base64 encoded
    const audioData = event.delta;
    // Use Web Audio API or other audio system to play
    await playAudioChunk(audioData);
  },
});
```

### 5.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong method names
```typescript
// WRONG - method is sendAudio
await session.input_audio_buffer.append(audio);

// WRONG - append does not exist
await session.appendAudio(audioData);
```

---

## 6. VAD (Voice Activity Detection) Patterns

### 6.1 ✅ CORRECT: Server VAD Configuration
```typescript
await session.updateSession({
  turnDetection: {
    type: "server_vad",
    threshold: 0.5,
    prefixPaddingMs: 300,
    silenceDurationMs: 500,
  },
});
```

### 6.2 ✅ CORRECT: Azure Semantic VAD
```typescript
await session.updateSession({
  turnDetection: {
    type: "azure_semantic_vad_en",
  },
});
```

### 6.3 ✅ CORRECT: Disable VAD (Manual Mode)
```typescript
await session.updateSession({
  turnDetection: null,
});
```

### 6.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong field names
```typescript
// WRONG - field is turnDetection, not turn_detection
await session.updateSession({
  turn_detection: {
    type: "server_vad",
  },
});

// WRONG - requires object, not string
await session.updateSession({
  turnDetection: "server_vad",
});
```

---

## 7. Function Calling Patterns

### 7.1 ✅ CORRECT: Define Function Tools
```typescript
const tools = [
  {
    type: "function" as const,
    name: "get_weather",
    description: "Get current weather for a location",
    parameters: {
      type: "object",
      properties: {
        location: {
          type: "string",
          description: "The city and state or country",
        },
      },
      required: ["location"],
    },
  },
];

await session.updateSession({
  modalities: ["audio", "text"],
  instructions: "You can help users with weather information.",
  tools: tools,
  toolChoice: "auto",
});
```

### 7.2 ✅ CORRECT: Handle Function Calls
```typescript
const subscription = session.subscribe({
  onResponseFunctionCallArgumentsDone: async (event, context) => {
    if (event.name === "get_weather") {
      const args = JSON.parse(event.arguments);
      const weatherData = await getWeatherData(args.location);

      // Send function result back
      await session.addConversationItem({
        type: "function_call_output",
        callId: event.callId,
        output: JSON.stringify(weatherData),
      });

      // Request response generation
      await session.sendEvent({
        type: "response.create",
      });
    }
  },
});
```

---

## 8. Conversation Item Patterns

### 8.1 ✅ CORRECT: Add Text Message
```typescript
await session.addConversationItem({
  type: "message",
  role: "user",
  content: [{ type: "input_text", text: "Hello, how can you help me?" }],
});

await session.sendEvent({
  type: "response.create",
});
```

### 8.2 ✅ CORRECT: Add Function Call Output
```typescript
await session.addConversationItem({
  type: "function_call_output",
  callId: functionCallEvent.callId,
  output: JSON.stringify({ result: "Success" }),
});
```

---

## 9. Model Selection

### 9.1 ✅ CORRECT: Available Models
```typescript
// GPT-4o with real-time audio
const session = await client.startSession("gpt-4o-realtime-preview");

// Lightweight GPT-4o variant
const session = await client.startSession("gpt-4o-mini-realtime-preview");

// Phi model with multimodal support
const session = await client.startSession("phi4-mm-realtime");
```

---

## 10. Session Lifecycle

### 10.1 ✅ CORRECT: Complete Session Lifecycle
```typescript
import { VoiceLiveClient } from "@azure/ai-voicelive";
import { DefaultAzureCredential } from "@azure/identity";

async function runVoiceAssistant() {
  const credential = new DefaultAzureCredential();
  const endpoint = process.env.AZURE_COGNITIVE_SERVICES_ENDPOINT!;

  const client = new VoiceLiveClient(endpoint, credential);
  const session = await client.startSession("gpt-4o-mini-realtime-preview");

  // Configure session
  await session.updateSession({
    modalities: ["text", "audio"],
    instructions: "You are a helpful assistant.",
    voice: {
      type: "azure-standard",
      name: "en-US-AvaNeural",
    },
    turnDetection: {
      type: "server_vad",
      threshold: 0.5,
      silenceDurationMs: 500,
    },
  });

  // Set up event handlers
  const subscription = session.subscribe({
    onResponseTextDelta: async (event) => {
      process.stdout.write(event.delta);
    },
    onResponseAudioDelta: async (event) => {
      // Handle audio playback
    },
    onError: async (event) => {
      console.error("Error:", event);
    },
  });

  // Send audio from microphone
  // session.sendAudio(microphoneBuffer);

  // Cleanup when done
  // subscription.unsubscribe();
  // await session.close();
}
```

---

## 11. Error Handling

### 11.1 ✅ CORRECT: Error Event Handler
```typescript
const subscription = session.subscribe({
  onError: async (event, context) => {
    console.error("VoiceLive error:", event);
  },
});
```

### 11.2 ✅ CORRECT: Try-Catch Pattern
```typescript
try {
  const session = await client.startSession("gpt-4o-realtime-preview");
  await session.updateSession({
    instructions: "You are helpful",
  });
} catch (error) {
  if (error instanceof Error) {
    console.error(`Session error: ${error.message}`);
  }
  throw error;
}
```

---

## 12. Logging

### 12.1 ✅ CORRECT: Enable Azure Logging
```typescript
import { setLogLevel } from "@azure/logger";

setLogLevel("info");
```

---

## 13. Environment Variables

### 13.1 ✅ CORRECT: Required Environment Variables
```typescript
const endpoint = process.env.AZURE_COGNITIVE_SERVICES_ENDPOINT!;
const apiKey = process.env.AZURE_COGNITIVE_SERVICES_KEY; // Optional if using AAD
```

### 13.2 ❌ INCORRECT: Hardcoded Values
```typescript
// WRONG - endpoints should be from environment
const client = new VoiceLiveClient(
  "https://my-resource.cognitiveservices.azure.com",
  new DefaultAzureCredential(),
);
```

---

## 14. Browser vs Node.js

### 14.1 ✅ CORRECT: TypeScript Configuration for Node.js
```typescript
// In tsconfig.json, ensure you have:
// "compilerOptions": {
//   "allowSyntheticDefaultImports": true,
//   "esModuleInterop": true
// }
```

### 14.2 ✅ CORRECT: Browser Bundle
```typescript
// For browser usage, use a bundler like webpack or vite
// The SDK supports both browser and Node.js environments
```
