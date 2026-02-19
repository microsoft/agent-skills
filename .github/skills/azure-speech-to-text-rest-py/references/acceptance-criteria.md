# Azure Speech to Text REST API Acceptance Criteria

**API**: Azure Speech to Text REST API for Short Audio
**Documentation**: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-speech-to-text-short
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. HTTP Request Construction

### 1.1 ✅ CORRECT: REST API URL Format
```python
import os

region = os.environ["AZURE_SPEECH_REGION"]
url = f"https://{region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
```

### 1.2 ✅ CORRECT: Alternative Recognition Mode
```python
# For dictation (longer pauses allowed)
url = f"https://{region}.stt.speech.microsoft.com/speech/recognition/dictation/cognitiveservices/v1"
```

### 1.3 ❌ INCORRECT: Wrong URL format
```python
# WRONG - Missing stt subdomain
url = f"https://{region}.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"

# WRONG - Using API instead of stt
url = f"https://{region}.api.cognitive.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"

# WRONG - Using SDK-style endpoint
url = f"https://{region}.cognitiveservices.azure.com/speech"
```

---

## 2. Authentication

### 2.1 ✅ CORRECT: Subscription Key Header
```python
headers = {
    "Ocp-Apim-Subscription-Key": os.environ["AZURE_SPEECH_KEY"]
}
```

### 2.2 ✅ CORRECT: Bearer Token Authentication
```python
def get_access_token() -> str:
    region = os.environ["AZURE_SPEECH_REGION"]
    api_key = os.environ["AZURE_SPEECH_KEY"]
    
    token_url = f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
    
    response = requests.post(
        token_url,
        headers={
            "Ocp-Apim-Subscription-Key": api_key,
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": "0"
        }
    )
    response.raise_for_status()
    return response.text

token = get_access_token()
headers = {"Authorization": f"Bearer {token}"}
```

### 2.3 ❌ INCORRECT: Wrong authentication
```python
# WRONG - Hardcoded credentials
headers = {"Ocp-Apim-Subscription-Key": "abc123"}

# WRONG - Wrong header name
headers = {"X-Api-Key": os.environ["AZURE_SPEECH_KEY"]}

# WRONG - Using AzureKeyCredential (this is REST API, not SDK)
from azure.core.credentials import AzureKeyCredential
credential = AzureKeyCredential(os.environ["AZURE_SPEECH_KEY"])
```

---

## 3. Content-Type Headers

### 3.1 ✅ CORRECT: WAV PCM 16kHz
```python
headers = {
    "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000"
}
```

### 3.2 ✅ CORRECT: OGG OPUS
```python
headers = {
    "Content-Type": "audio/ogg; codecs=opus"
}
```

### 3.3 ❌ INCORRECT: Wrong content type
```python
# WRONG - Missing codec and sample rate
headers = {"Content-Type": "audio/wav"}

# WRONG - Wrong MIME type
headers = {"Content-Type": "audio/mpeg"}

# WRONG - Missing codecs parameter
headers = {"Content-Type": "audio/ogg"}
```

---

## 4. Request Parameters

### 4.1 ✅ CORRECT: Required Language Parameter
```python
params = {
    "language": "en-US"
}
```

### 4.2 ✅ CORRECT: Full Parameters
```python
params = {
    "language": "en-US",
    "format": "detailed",  # or "simple"
    "profanity": "masked"  # or "removed", "raw"
}
```

### 4.3 ❌ INCORRECT: Missing language
```python
# WRONG - Language is required
params = {"format": "detailed"}

# WRONG - Using locale instead of language
params = {"locale": "en-US"}
```

---

## 5. Making the Request

### 5.1 ✅ CORRECT: Basic Request
```python
import requests

def transcribe_audio(audio_file_path: str, language: str = "en-US") -> dict:
    region = os.environ["AZURE_SPEECH_REGION"]
    api_key = os.environ["AZURE_SPEECH_KEY"]
    
    url = f"https://{region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
    
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
        "Accept": "application/json"
    }
    
    params = {"language": language, "format": "detailed"}
    
    with open(audio_file_path, "rb") as audio_file:
        response = requests.post(url, headers=headers, params=params, data=audio_file)
    
    response.raise_for_status()
    return response.json()
```

### 5.2 ✅ CORRECT: Chunked Transfer for Lower Latency
```python
def transcribe_chunked(audio_file_path: str) -> dict:
    headers = {
        "Ocp-Apim-Subscription-Key": os.environ["AZURE_SPEECH_KEY"],
        "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
        "Transfer-Encoding": "chunked",
        "Expect": "100-continue"
    }
    
    def generate_chunks(file_path: str, chunk_size: int = 1024):
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                yield chunk
    
    response = requests.post(url, headers=headers, params=params, data=generate_chunks(audio_file_path))
    return response.json()
```

### 5.3 ❌ INCORRECT: Wrong request method or format
```python
# WRONG - GET instead of POST
response = requests.get(url, headers=headers, params=params)

# WRONG - Using JSON body instead of binary audio
response = requests.post(url, headers=headers, json={"audio": audio_data})

# WRONG - Using Speech SDK client
from azure.cognitiveservices.speech import SpeechRecognizer
```

---

## 6. Response Handling

### 6.1 ✅ CORRECT: Simple Response
```python
result = response.json()
if result.get("RecognitionStatus") == "Success":
    print(result["DisplayText"])
```

### 6.2 ✅ CORRECT: Detailed Response with NBest
```python
result = response.json()
if result.get("RecognitionStatus") == "Success":
    for item in result.get("NBest", []):
        print(f"Text: {item['Display']}")
        print(f"Confidence: {item['Confidence']}")
```

### 6.3 ✅ CORRECT: Status Handling
```python
status = result.get("RecognitionStatus")
if status == "Success":
    print(result["DisplayText"])
elif status == "NoMatch":
    print("No speech detected")
elif status == "InitialSilenceTimeout":
    print("Only silence detected")
elif status == "BabbleTimeout":
    print("Only noise detected")
else:
    print(f"Error: {status}")
```

### 6.4 ❌ INCORRECT: Wrong response access
```python
# WRONG - Using lowercase keys
print(result["displayText"])

# WRONG - Assuming always has text
print(result["DisplayText"])  # May be None if NoMatch

# WRONG - SDK-style response
print(result.text)
```

---

## 7. Async Version

### 7.1 ✅ CORRECT: Using aiohttp
```python
import aiohttp
import asyncio

async def transcribe_async(audio_file_path: str, language: str = "en-US") -> dict:
    region = os.environ["AZURE_SPEECH_REGION"]
    api_key = os.environ["AZURE_SPEECH_KEY"]
    
    url = f"https://{region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
    
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
        "Accept": "application/json"
    }
    
    params = {"language": language, "format": "detailed"}
    
    async with aiohttp.ClientSession() as session:
        with open(audio_file_path, "rb") as f:
            audio_data = f.read()
        
        async with session.post(url, headers=headers, params=params, data=audio_data) as response:
            response.raise_for_status()
            return await response.json()
```

### 7.2 ❌ INCORRECT: Blocking in async
```python
# WRONG - Using blocking requests in async
async def transcribe_wrong():
    response = requests.post(url, data=audio)  # Blocks event loop
```

---

## 8. Error Handling

### 8.1 ✅ CORRECT: HTTP and Recognition Errors
```python
try:
    response = requests.post(url, headers=headers, params=params, data=audio_file)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("RecognitionStatus") == "Success":
            return result
        else:
            print(f"Recognition failed: {result.get('RecognitionStatus')}")
    elif response.status_code == 400:
        print("Bad request: Check language code or audio format")
    elif response.status_code == 401:
        print("Unauthorized: Check API key")
    elif response.status_code == 403:
        print("Forbidden: Missing authorization header")
        
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

### 8.2 ❌ INCORRECT: No error handling
```python
# WRONG - No error handling
response = requests.post(url, data=audio)
return response.json()["DisplayText"]
```

---

## 9. Do NOT Use

### 9.1 ❌ INCORRECT: Using Speech SDK
```python
# WRONG - This skill is for REST API, not SDK
from azure.cognitiveservices.speech import SpeechRecognizer
from azure.cognitiveservices.speech import SpeechConfig

# WRONG - SDK-style configuration
speech_config = SpeechConfig(subscription=key, region=region)
```

### 9.2 ❌ INCORRECT: Using Azure SDK Credentials
```python
# WRONG - REST API doesn't use Azure SDK credentials
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
```

---

## 10. Audio Limitations

### 10.1 ✅ CORRECT: Documented Limits
- Maximum audio duration: 60 seconds
- For pronunciation assessment: 30 seconds maximum
- Supported formats: WAV PCM 16kHz mono, OGG OPUS

### 10.2 ❌ INCORRECT: Exceeding Limits
```python
# WRONG - No validation of audio length
# Audio > 60 seconds will fail
```

---

## Summary: Key Patterns

| Pattern | Correct | Incorrect |
|---------|---------|-----------|
| URL format | `{region}.stt.speech.microsoft.com` | `{region}.speech.microsoft.com` |
| Auth header | `Ocp-Apim-Subscription-Key` | `X-Api-Key`, hardcoded |
| Content-Type | `audio/wav; codecs=audio/pcm; samplerate=16000` | `audio/wav` (missing params) |
| Required param | `language=en-US` | Missing or `locale=en-US` |
| Response key | `RecognitionStatus`, `DisplayText` | `recognitionStatus`, `displayText` |
| Library | `requests`, `aiohttp` | `azure.cognitiveservices.speech` |
