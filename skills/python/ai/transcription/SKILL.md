---
name: azure-cognitiveservices-speech-python
description: |
  Azure Speech SDK for speech-to-text, text-to-speech, translation, and speaker recognition. Use for audio transcription, voice synthesis, and real-time speech processing.
  Triggers: "speech to text", "text to speech", "transcription", "voice synthesis", "SpeechConfig", "SpeechRecognizer".
---

# Azure Cognitive Services Speech SDK for Python

Client library for Azure Speech services including recognition, synthesis, translation, and speaker identification.

## Installation

```bash
pip install azure-cognitiveservices-speech
```

## Environment Variables

```bash
SPEECH_KEY=<your-speech-key>
SPEECH_REGION=<your-region>  # e.g., eastus, westus2
# Or use endpoint directly
SPEECH_ENDPOINT=https://<region>.api.cognitive.microsoft.com/
```

## Authentication

Speech SDK uses subscription key authentication (not DefaultAzureCredential):

```python
import os
import azure.cognitiveservices.speech as speechsdk

speech_config = speechsdk.SpeechConfig(
    subscription=os.environ["SPEECH_KEY"],
    region=os.environ["SPEECH_REGION"]
)
```

Or with endpoint:

```python
speech_config = speechsdk.SpeechConfig(
    subscription=os.environ["SPEECH_KEY"],
    endpoint=os.environ["SPEECH_ENDPOINT"]
)
```

## Speech-to-Text (Recognition)

### From Microphone

```python
import azure.cognitiveservices.speech as speechsdk

speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
speech_config.speech_recognition_language = "en-US"

# Default microphone
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

print("Speak into your microphone...")
result = speech_recognizer.recognize_once_async().get()

if result.reason == speechsdk.ResultReason.RecognizedSpeech:
    print(f"Recognized: {result.text}")
elif result.reason == speechsdk.ResultReason.NoMatch:
    print("No speech could be recognized")
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation = result.cancellation_details
    print(f"Canceled: {cancellation.reason}")
```

### From Audio File

```python
audio_config = speechsdk.audio.AudioConfig(filename="audio.wav")
speech_recognizer = speechsdk.SpeechRecognizer(
    speech_config=speech_config,
    audio_config=audio_config
)

result = speech_recognizer.recognize_once_async().get()
print(f"Recognized: {result.text}")
```

### Continuous Recognition

```python
speech_recognizer = speechsdk.SpeechRecognizer(
    speech_config=speech_config,
    audio_config=audio_config
)

done = False

def recognized_cb(evt):
    print(f"RECOGNIZED: {evt.result.text}")

def stop_cb(evt):
    nonlocal done
    done = True

speech_recognizer.recognized.connect(recognized_cb)
speech_recognizer.session_stopped.connect(stop_cb)
speech_recognizer.canceled.connect(stop_cb)

speech_recognizer.start_continuous_recognition()

while not done:
    pass

speech_recognizer.stop_continuous_recognition()
```

## Text-to-Speech (Synthesis)

### Basic Synthesis

```python
speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

result = synthesizer.speak_text_async("Hello, world!").get()

if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesized successfully")
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation = result.cancellation_details
    print(f"Synthesis canceled: {cancellation.reason}")
```

### Save to Audio File

```python
audio_config = speechsdk.audio.AudioOutputConfig(filename="output.wav")
synthesizer = speechsdk.SpeechSynthesizer(
    speech_config=speech_config,
    audio_config=audio_config
)

result = synthesizer.speak_text_async("Hello, world!").get()
```

### SSML for Advanced Control

```python
ssml = """
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
    <voice name="en-US-JennyNeural">
        <prosody rate="-10%" pitch="+5%">
            Hello! <break time="500ms"/> How are you today?
        </prosody>
    </voice>
</speak>
"""

result = synthesizer.speak_ssml_async(ssml).get()
```

## Speech Translation

```python
translation_config = speechsdk.translation.SpeechTranslationConfig(
    subscription=key,
    region=region
)
translation_config.speech_recognition_language = "en-US"
translation_config.add_target_language("es")
translation_config.add_target_language("fr")

recognizer = speechsdk.translation.TranslationRecognizer(
    translation_config=translation_config
)

result = recognizer.recognize_once_async().get()

if result.reason == speechsdk.ResultReason.TranslatedSpeech:
    print(f"Recognized: {result.text}")
    print(f"Spanish: {result.translations['es']}")
    print(f"French: {result.translations['fr']}")
```

## Speaker Recognition

```python
# Create voice profile
profile_client = speechsdk.SpeakerRecognizer(speech_config, audio_config)

# Verify speaker
model = speechsdk.SpeakerVerificationModel(profile)
result = profile_client.recognize_once_async(model).get()

if result.reason == speechsdk.ResultReason.RecognizedSpeaker:
    print(f"Verified with score: {result.score}")
```

## Configuration Options

| Property | Description |
|----------|-------------|
| `speech_recognition_language` | Recognition language (e.g., "en-US") |
| `speech_synthesis_voice_name` | TTS voice (e.g., "en-US-JennyNeural") |
| `set_profanity` | Profanity handling (Masked, Removed, Raw) |
| `enable_dictation` | Enable dictation mode |
| `request_word_level_timestamps` | Get word timing |

## Client Types

| Class | Purpose |
|-------|---------|
| `SpeechRecognizer` | Speech-to-text |
| `SpeechSynthesizer` | Text-to-speech |
| `TranslationRecognizer` | Speech translation |
| `SpeakerRecognizer` | Speaker identification/verification |
| `ConversationTranscriber` | Multi-speaker transcription |

## Audio Formats

```python
# Configure audio format
audio_format = speechsdk.audio.AudioStreamFormat(
    samples_per_second=16000,
    bits_per_sample=16,
    channels=1
)

# Push stream for custom audio input
push_stream = speechsdk.audio.PushAudioInputStream(audio_format)
audio_config = speechsdk.audio.AudioConfig(stream=push_stream)

# Write audio data
push_stream.write(audio_data)
push_stream.close()
```

## Best Practices

1. **Use continuous recognition** for long audio streams
2. **Handle all result reasons** (success, no match, canceled)
3. **Specify language** to improve recognition accuracy
4. **Use Neural voices** for natural-sounding TTS
5. **Implement event handlers** for real-time feedback
6. **Close resources** when done (recognizer.close())
7. **Use SSML** for fine-grained speech control
