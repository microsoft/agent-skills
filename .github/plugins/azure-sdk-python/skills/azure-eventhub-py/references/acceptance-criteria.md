# Azure Event Hubs SDK Acceptance Criteria

**SDK**: `azure-eventhub`
**Repository**: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/eventhub/azure-eventhub
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Sync Producer/Consumer
```python
from azure.eventhub import EventHubProducerClient, EventHubConsumerClient, EventData
from azure.identity import DefaultAzureCredential
```

#### ✅ CORRECT: Blob Checkpoint Store (Sync)
```python
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore
```

#### ✅ CORRECT: Async Clients
```python
from azure.eventhub.aio import EventHubProducerClient, EventHubConsumerClient
from azure.identity.aio import DefaultAzureCredential
```

#### ✅ CORRECT: Async Blob Checkpoint Store
```python
from azure.eventhub.extensions.checkpointstoreblob.aio import BlobCheckpointStore
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong modules
```python
# WRONG - package name is azure.eventhub
from azure.eventhubs import EventHubProducerClient

# WRONG - DefaultAzureCredential is from azure.identity(.aio)
from azure.eventhub.aio import DefaultAzureCredential
```

---

## 2. Authentication Patterns

### 2.1 ✅ CORRECT: DefaultAzureCredential with Fully Qualified Namespace
```python
import os
from azure.eventhub import EventHubProducerClient, EventHubConsumerClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
namespace = os.environ["EVENT_HUB_FULLY_QUALIFIED_NAMESPACE"]
eventhub_name = os.environ["EVENT_HUB_NAME"]

producer = EventHubProducerClient(
    fully_qualified_namespace=namespace,
    eventhub_name=eventhub_name,
    credential=credential,
)

consumer = EventHubConsumerClient(
    fully_qualified_namespace=namespace,
    eventhub_name=eventhub_name,
    consumer_group="$Default",
    credential=credential,
)
```

### 2.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded connection strings
```python
# WRONG - avoid hardcoded connection strings
producer = EventHubProducerClient.from_connection_string(
    "Endpoint=sb://...;SharedAccessKeyName=...;SharedAccessKey=...",
    eventhub_name="my-eventhub",
)
```

---

## 3. EventHubProducerClient Patterns

### 3.1 ✅ CORRECT: Batch Send with Size Handling
```python
from azure.eventhub import EventHubProducerClient, EventData
from azure.identity import DefaultAzureCredential

producer = EventHubProducerClient(
    fully_qualified_namespace="<namespace>.servicebus.windows.net",
    eventhub_name="my-eventhub",
    credential=DefaultAzureCredential(),
)

with producer:
    batch = producer.create_batch()
    for i in range(10):
        try:
            batch.add(EventData(f"event-{i}"))
        except ValueError:
            producer.send_batch(batch)
            batch = producer.create_batch()
            batch.add(EventData(f"event-{i}"))
    producer.send_batch(batch)
```

### 3.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing context manager or close
```python
# WRONG - producer should be used with context manager or explicitly closed
producer = EventHubProducerClient(
    fully_qualified_namespace=namespace,
    eventhub_name=eventhub_name,
    credential=credential,
)
producer.send_batch([EventData("event")])
```

---

## 4. EventHubConsumerClient Patterns

### 4.1 ✅ CORRECT: Receive with Checkpoint Update
```python
from azure.eventhub import EventHubConsumerClient
from azure.identity import DefaultAzureCredential

def on_event(partition_context, event):
    print(event.body_as_str())
    partition_context.update_checkpoint(event)

consumer = EventHubConsumerClient(
    fully_qualified_namespace="<namespace>.servicebus.windows.net",
    eventhub_name="my-eventhub",
    consumer_group="$Default",
    credential=DefaultAzureCredential(),
)

with consumer:
    consumer.receive(on_event=on_event, starting_position="-1")
```

### 4.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing on_event handler
```python
# WRONG - receive requires an on_event callback
consumer.receive(starting_position="-1")
```

---

## 5. Partitions

### 5.1 ✅ CORRECT: Send to Specific Partition
```python
batch_by_id = producer.create_batch(partition_id="0")
batch_by_id.add(EventData("event-for-partition-0"))

batch_by_key = producer.create_batch(partition_key="user-123")
batch_by_key.add(EventData("event-for-user-123"))
```

### 5.2 ✅ CORRECT: Read Partition Properties
```python
with producer:
    info = producer.get_eventhub_properties()
    for partition_id in info["partition_ids"]:
        partition_info = producer.get_partition_properties(partition_id)
        print(partition_info["last_enqueued_sequence_number"])
```

### 5.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Passing both partition_id and partition_key
```python
# WRONG - only one of partition_id or partition_key is allowed
producer.create_batch(partition_id="0", partition_key="user-123")
```

---

## 6. Checkpointing

### 6.1 ✅ CORRECT: BlobCheckpointStore with Consumer
```python
from azure.eventhub import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore
from azure.identity import DefaultAzureCredential

checkpoint_store = BlobCheckpointStore(
    blob_account_url="https://<account>.blob.core.windows.net",
    container_name="checkpoints",
    credential=DefaultAzureCredential(),
)

consumer = EventHubConsumerClient(
    fully_qualified_namespace="<namespace>.servicebus.windows.net",
    eventhub_name="my-eventhub",
    consumer_group="$Default",
    credential=DefaultAzureCredential(),
    checkpoint_store=checkpoint_store,
)

def on_event(partition_context, event):
    partition_context.update_checkpoint(event)
```

### 6.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Checkpoint store without updating checkpoints
```python
# WRONG - checkpoint store requires update_checkpoint to persist progress
def on_event(partition_context, event):
    print(event.body_as_str())
    return  # No checkpoint update!
```

---

## 7. Async Variants

### 7.1 ✅ CORRECT: Async Producer Send
```python
import asyncio
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient
from azure.identity.aio import DefaultAzureCredential

async def main():
    async with EventHubProducerClient(
        fully_qualified_namespace="<namespace>.servicebus.windows.net",
        eventhub_name="my-eventhub",
        credential=DefaultAzureCredential(),
    ) as producer:
        batch = await producer.create_batch()
        batch.add(EventData("async-event"))
        await producer.send_batch(batch)

asyncio.run(main())
```

### 7.2 ✅ CORRECT: Async Consumer with Checkpointing
```python
import asyncio
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblob.aio import BlobCheckpointStore
from azure.identity.aio import DefaultAzureCredential

async def on_event(partition_context, event):
    print(event.body_as_str())
    await partition_context.update_checkpoint(event)

async def main():
    checkpoint_store = BlobCheckpointStore(
        blob_account_url="https://<account>.blob.core.windows.net",
        container_name="checkpoints",
        credential=DefaultAzureCredential(),
    )

    async with EventHubConsumerClient(
        fully_qualified_namespace="<namespace>.servicebus.windows.net",
        eventhub_name="my-eventhub",
        consumer_group="$Default",
        credential=DefaultAzureCredential(),
        checkpoint_store=checkpoint_store,
    ) as consumer:
        await consumer.receive(on_event=on_event, starting_position="-1")

asyncio.run(main())
```

### 7.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Mixing sync credential with async client
```python
from azure.eventhub.aio import EventHubProducerClient
from azure.identity import DefaultAzureCredential  # WRONG - use azure.identity.aio

async with EventHubProducerClient(
    fully_qualified_namespace=namespace,
    eventhub_name=eventhub_name,
    credential=DefaultAzureCredential(),
):
    ...
```

---

## 8. Environment Variables

### Required Variables
```bash
EVENT_HUB_FULLY_QUALIFIED_NAMESPACE=<namespace>.servicebus.windows.net
EVENT_HUB_NAME=my-eventhub
```

### Optional Variables (Checkpointing)
```bash
STORAGE_ACCOUNT_URL=https://<account>.blob.core.windows.net
CHECKPOINT_CONTAINER=checkpoints
```
