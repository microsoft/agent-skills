# Azure Service Bus SDK Acceptance Criteria

**SDK**: `azure-servicebus`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Sync Client
```python
from azure.servicebus import ServiceBusClient
from azure.identity import DefaultAzureCredential
```

#### ✅ CORRECT: Async Client
```python
from azure.servicebus.aio import ServiceBusClient
from azure.identity.aio import DefaultAzureCredential
```

### 1.2 Message and Enum Imports

#### ✅ CORRECT: Messages and Enums
```python
from azure.servicebus import (
    ServiceBusMessage,
    ServiceBusReceiveMode,
    ServiceBusSubQueue,
    NEXT_AVAILABLE_SESSION,
)
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong import paths
```python
# WRONG - async client is in azure.servicebus.aio
from azure.servicebus import ServiceBusClient  # Async usage with sync import

# WRONG - ServiceBusMessage is not in azure.servicebus.aio
from azure.servicebus.aio import ServiceBusMessage
```

---

## 2. Authentication Patterns

### 2.1 ✅ CORRECT: DefaultAzureCredential (Sync)
```python
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
```

### 2.2 ✅ CORRECT: DefaultAzureCredential (Async)
```python
from azure.identity.aio import DefaultAzureCredential

credential = DefaultAzureCredential()
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Connection string auth
```python
# WRONG - use DefaultAzureCredential in this skill
client = ServiceBusClient.from_connection_string(conn_str)
```

#### ❌ INCORRECT: Hardcoded credentials
```python
# WRONG - do not hardcode secrets
client = ServiceBusClient.from_connection_string("Endpoint=sb://...")
```

---

## 3. ServiceBusClient Creation

### 3.1 ✅ CORRECT: Sync Client with Context Manager
```python
client = ServiceBusClient(
    fully_qualified_namespace=os.environ["SERVICEBUS_FULLY_QUALIFIED_NAMESPACE"],
    credential=DefaultAzureCredential(),
)

with client:
    sender = client.get_queue_sender(queue_name="myqueue")
```

### 3.2 ✅ CORRECT: Async Client with Context Manager
```python
client = ServiceBusClient(
    fully_qualified_namespace=os.environ["SERVICEBUS_FULLY_QUALIFIED_NAMESPACE"],
    credential=DefaultAzureCredential(),
)

async with client:
    sender = client.get_queue_sender(queue_name="myqueue")
```

### 3.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong parameter name
```python
# WRONG - must use fully_qualified_namespace
client = ServiceBusClient(namespace=namespace, credential=credential)
```

#### ❌ INCORRECT: Missing context manager
```python
# WRONG - client should be used with context manager or explicitly closed
client = ServiceBusClient(
    fully_qualified_namespace=namespace,
    credential=credential,
)
sender = client.get_queue_sender(queue_name="myqueue")
```

---

## 4. Sender/Receiver Patterns

### 4.1 ✅ CORRECT: Queue Sender and Receiver
```python
with client.get_queue_sender(queue_name="myqueue") as sender:
    sender.send_messages(ServiceBusMessage("hello"))

with client.get_queue_receiver(queue_name="myqueue") as receiver:
    for message in receiver:
        receiver.complete_message(message)
```

### 4.2 ✅ CORRECT: Async Sender and Receiver
```python
async with client.get_queue_sender(queue_name="myqueue") as sender:
    await sender.send_messages(ServiceBusMessage("hello"))

async with client.get_queue_receiver(queue_name="myqueue") as receiver:
    messages = await receiver.receive_messages(max_message_count=10, max_wait_time=5)
    for message in messages:
        await receiver.complete_message(message)
```

### 4.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong method names
```python
# WRONG - send() does not exist
sender.send(ServiceBusMessage("hello"))
```


---

## 5. Queues, Topics, and Subscriptions

### 5.1 ✅ CORRECT: Topic Sender and Subscription Receiver
```python
with client.get_topic_sender(topic_name="mytopic") as sender:
    sender.send_messages(ServiceBusMessage("topic message"))

with client.get_subscription_receiver(
    topic_name="mytopic",
    subscription_name="mysubscription",
) as receiver:
    messages = receiver.receive_messages(max_message_count=5, max_wait_time=5)
```

### 5.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing subscription_name
```python
# WRONG - subscription receiver requires subscription_name
receiver = client.get_subscription_receiver(topic_name="mytopic")
```

---

## 6. Sessions

### 6.1 ✅ CORRECT: Session-Enabled Messages
```python
message = ServiceBusMessage("session message")
message.session_id = "order-123"
sender.send_messages(message)

receiver = client.get_queue_receiver(
    queue_name="session-queue",
    session_id="order-123",
)
```

### 6.2 ✅ CORRECT: Next Available Session
```python
receiver = client.get_queue_receiver(
    queue_name="session-queue",
    session_id=NEXT_AVAILABLE_SESSION,
)
```

### 6.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong parameter name
```python
# WRONG - parameter is session_id
receiver = client.get_queue_receiver(queue_name="session-queue", session="order-123")
```

---

## 7. Async Variants

### 7.1 ✅ CORRECT: Async Flow
```python
from azure.servicebus.aio import ServiceBusClient
from azure.identity.aio import DefaultAzureCredential

async with ServiceBusClient(
    fully_qualified_namespace=os.environ["SERVICEBUS_FULLY_QUALIFIED_NAMESPACE"],
    credential=DefaultAzureCredential(),
) as client:
    async with client.get_queue_sender(queue_name="myqueue") as sender:
        await sender.send_messages(ServiceBusMessage("hello"))
```

### 7.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Sync credential with async client
```python
from azure.identity import DefaultAzureCredential
from azure.servicebus.aio import ServiceBusClient

# WRONG - should use azure.identity.aio.DefaultAzureCredential
async with ServiceBusClient(
    fully_qualified_namespace=namespace,
    credential=DefaultAzureCredential(),
):
    ...
```

#### ❌ INCORRECT: Missing await
```python
# WRONG - missing await
async with client.get_queue_sender(queue_name="myqueue") as sender:
    sender.send_messages(ServiceBusMessage("hello"))
```
