# Azure Storage Queue SDK Acceptance Criteria

**SDK**: `azure-storage-queue`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Sync Clients
```python
from azure.storage.queue import QueueServiceClient, QueueClient
from azure.identity import DefaultAzureCredential
```

#### ✅ CORRECT: Async Clients
```python
from azure.storage.queue.aio import QueueServiceClient, QueueClient
from azure.identity.aio import DefaultAzureCredential
```

### 1.2 Optional Policy Imports

#### ✅ CORRECT: Base64 Encode/Decode Policies
```python
from azure.storage.queue import BinaryBase64EncodePolicy, BinaryBase64DecodePolicy
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong import paths
```python
# WRONG - QueueClient is not in azure.storage.queue.queueclient
from azure.storage.queue.queueclient import QueueClient

# WRONG - async client class does not exist
from azure.storage.queue import QueueServiceClientAsync
```

---

## 2. Authentication Patterns

### 2.1 ✅ CORRECT: DefaultAzureCredential (Sync)
```python
import os
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueServiceClient

service_client = QueueServiceClient(
    account_url=os.environ["AZURE_STORAGE_ACCOUNT_URL"],
    credential=DefaultAzureCredential(),
)
```

### 2.2 ✅ CORRECT: DefaultAzureCredential (Async)
```python
import os
from azure.identity.aio import DefaultAzureCredential
from azure.storage.queue.aio import QueueServiceClient

service_client = QueueServiceClient(
    account_url=os.environ["AZURE_STORAGE_ACCOUNT_URL"],
    credential=DefaultAzureCredential(),
)
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded keys or connection strings
```python
# WRONG - hardcoded key
service_client = QueueServiceClient(
    account_url="https://example.queue.core.windows.net",
    credential="ACCOUNT_KEY",
)

# WRONG - connection string instead of DefaultAzureCredential
service_client = QueueServiceClient.from_connection_string(
    "DefaultEndpointsProtocol=https;AccountName=...;AccountKey=..."
)
```

---

## 3. QueueServiceClient Patterns

### 3.1 ✅ CORRECT: Create, List, and Delete Queues
```python
import os
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueServiceClient

service_client = QueueServiceClient(
    account_url=os.environ["AZURE_STORAGE_ACCOUNT_URL"],
    credential=DefaultAzureCredential(),
)

service_client.create_queue("tasks")

for queue in service_client.list_queues():
    print(queue.name)

service_client.delete_queue("tasks")
```

### 3.2 ✅ CORRECT: Get QueueClient from Service
```python
queue_client = service_client.get_queue_client("tasks")
```

### 3.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing account_url or credential
```python
# WRONG - missing required account_url
service_client = QueueServiceClient(credential=DefaultAzureCredential())
```

---

## 4. QueueClient Patterns

### 4.1 ✅ CORRECT: Create QueueClient Directly
```python
import os
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueClient

queue_client = QueueClient(
    account_url=os.environ["AZURE_STORAGE_ACCOUNT_URL"],
    queue_name="tasks",
    credential=DefaultAzureCredential(),
)
```

### 4.2 ✅ CORRECT: Create QueueClient from QueueServiceClient
```python
queue_client = service_client.get_queue_client("tasks")
```

### 4.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: QueueClient without queue_name parameter
```python
# WRONG - QueueClient instantiated with only account_url and credential, missing queue_name
QueueClient(account_url=url, credential=cred)
```

---

## 5. Send / Receive / Peek Message Patterns

### 5.1 ✅ CORRECT: Send, Receive, Peek, and Delete
```python
queue_client.send_message("task-1")

messages = queue_client.receive_messages(max_messages=5)
for message in messages:
    print(message.content)
    queue_client.delete_message(message)

peeked = queue_client.peek_messages(max_messages=5)
for message in peeked:
    print(message.content)
```

### 5.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Deleting without pop_receipt or full message
```python
# WRONG - delete_message requires a QueueMessage or (id, pop_receipt)
queue_client.delete_message(message.id)
```

---

## 6. Visibility Timeout Patterns

### 6.1 ✅ CORRECT: Send with Visibility Timeout and TTL
```python
queue_client.send_message(
    content="delayed-task",
    visibility_timeout=60,
    time_to_live=3600,
)
```

### 6.2 ✅ CORRECT: Receive with Visibility Timeout
```python
messages = queue_client.receive_messages(
    visibility_timeout=30,
    messages_per_page=5,
)
for message in messages:
    queue_client.delete_message(message)
```

### 6.3 ✅ CORRECT: Update Message to Extend Visibility
```python
messages = queue_client.receive_messages()
message = next(messages)
queue_client.update_message(
    message,
    pop_receipt=message.pop_receipt,
    visibility_timeout=120,
    content="updated-task",
)
```

### 6.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using milliseconds instead of seconds
```python
# WRONG - visibility_timeout expects seconds, not milliseconds
queue_client.send_message("task", visibility_timeout=30000)
```

---

## 7. Async Variants

### 7.1 ✅ CORRECT: Async QueueClient Usage
```python
import os
import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.storage.queue.aio import QueueClient

async def main():
    credential = DefaultAzureCredential()
    async with QueueClient(
        account_url=os.environ["AZURE_STORAGE_ACCOUNT_URL"],
        queue_name="tasks",
        credential=credential,
    ) as client:
        await client.send_message("async-task")
        async for message in client.receive_messages():
            print(message.content)
            await client.delete_message(message)

asyncio.run(main())
```

### 7.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Mixing sync credential with async client
```python
from azure.identity import DefaultAzureCredential  # WRONG
from azure.storage.queue.aio import QueueClient

async with QueueClient(
    account_url=os.environ["AZURE_STORAGE_ACCOUNT_URL"],
    queue_name="tasks",
    credential=DefaultAzureCredential(),
):
    ...
```

#### ❌ INCORRECT: Not using async iteration
```python
# WRONG - receive_messages returns async iterator in async mode
messages = client.receive_messages()
for message in messages:
    print(message.content)
```
