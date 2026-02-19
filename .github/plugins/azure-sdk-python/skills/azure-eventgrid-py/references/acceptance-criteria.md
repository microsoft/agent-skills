# Azure Event Grid SDK Acceptance Criteria

**SDK**: `azure-eventgrid`
**Repository**: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/eventgrid/azure-eventgrid
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Imports

### 1.1 ✅ CORRECT: Core Imports
```python
from azure.eventgrid import EventGridPublisherClient, CloudEvent, EventGridEvent
from azure.identity import DefaultAzureCredential
```

### 1.2 ✅ CORRECT: Async Client Imports
```python
from azure.eventgrid.aio import EventGridPublisherClient
from azure.identity.aio import DefaultAzureCredential
```

### 1.3 ✅ CORRECT: Supporting Imports
```python
import os
from datetime import datetime, timezone
```

### 1.4 ❌ INCORRECT: Wrong import locations
```python
# WRONG - models are not in aio module
from azure.eventgrid.aio import CloudEvent

# WRONG - non-existent async client class
from azure.eventgrid import EventGridPublisherClientAsync
```

---

## 2. Authentication

### 2.1 ✅ CORRECT: DefaultAzureCredential
```python
import os
from azure.identity import DefaultAzureCredential
from azure.eventgrid import EventGridPublisherClient

endpoint = os.environ["EVENTGRID_TOPIC_ENDPOINT"]
credential = DefaultAzureCredential()
client = EventGridPublisherClient(endpoint, credential)
```

### 2.2 ❌ INCORRECT: Hardcoded credentials or endpoints
```python
# WRONG - hardcoded endpoint
client = EventGridPublisherClient(
    "https://example.eventgrid.azure.net/api/events",
    DefaultAzureCredential()
)

# WRONG - hardcoded key usage in examples
from azure.core.credentials import AzureKeyCredential
client = EventGridPublisherClient(endpoint, AzureKeyCredential("<key>"))
```

---

## 3. EventGridPublisherClient

### 3.1 ✅ CORRECT: Sync Client with Context Manager
```python
import os
from azure.eventgrid import EventGridPublisherClient, CloudEvent
from azure.identity import DefaultAzureCredential

endpoint = os.environ["EVENTGRID_TOPIC_ENDPOINT"]
credential = DefaultAzureCredential()

with EventGridPublisherClient(endpoint, credential) as client:
    event = CloudEvent(
        type="MyApp.Events.Created",
        source="/myapp/items",
        data={"id": "123"},
    )
    client.send(event)
```

### 3.2 ✅ CORRECT: Async Client with Context Manager
```python
import os
from azure.eventgrid.aio import EventGridPublisherClient
from azure.eventgrid import CloudEvent
from azure.identity.aio import DefaultAzureCredential

endpoint = os.environ["EVENTGRID_TOPIC_ENDPOINT"]

async with EventGridPublisherClient(endpoint, DefaultAzureCredential()) as client:
    event = CloudEvent(
        type="MyApp.Events.Created",
        source="/myapp/items",
        data={"id": "123"},
    )
    await client.send(event)
```

### 3.3 ❌ INCORRECT: Missing client cleanup
```python
client = EventGridPublisherClient(endpoint, DefaultAzureCredential())
client.send(event)
print("done without cleanup")
```

---

## 4. CloudEvent

### 4.1 ✅ CORRECT: Required Fields
```python
from azure.eventgrid import CloudEvent

event = CloudEvent(
    type="MyApp.Events.ItemCreated",
    source="/myapp/items",
    data={"item_id": "abc"},
)
```

### 4.2 ✅ CORRECT: Optional Properties
```python
from azure.eventgrid import CloudEvent
from datetime import datetime, timezone

event = CloudEvent(
    type="MyApp.Events.ItemCreated",
    source="/myapp/items",
    data={"item_id": "abc"},
    subject="items/abc",
    datacontenttype="application/json",
    dataschema="https://schema.example/items.json",
    time=datetime.now(timezone.utc),
    extensions={"traceId": "123"},
)
```

### 4.3 ❌ INCORRECT: Missing required fields
```python
# WRONG - missing type and source
event = CloudEvent(data={"item_id": "abc"})
```

---

## 5. EventGridEvent

### 5.1 ✅ CORRECT: Required Fields
```python
from azure.eventgrid import EventGridEvent

event = EventGridEvent(
    subject="/myapp/items/abc",
    event_type="MyApp.Events.ItemCreated",
    data={"item_id": "abc"},
    data_version="1.0",
)
```

### 5.2 ✅ CORRECT: Optional Properties
```python
from azure.eventgrid import EventGridEvent
from datetime import datetime, timezone

event = EventGridEvent(
    subject="/myapp/items/abc",
    event_type="MyApp.Events.ItemCreated",
    data={"item_id": "abc"},
    data_version="1.0",
    topic="/subscriptions/0000/resourceGroups/rg/providers/Microsoft.EventGrid/topics/topic",
    event_time=datetime.now(timezone.utc),
)
```

### 5.3 ❌ INCORRECT: Wrong parameter names or missing data_version
```python
# WRONG - eventType is not a valid parameter name
event = EventGridEvent(
    subject="/myapp/items/abc",
    eventType="MyApp.Events.ItemCreated",
    data={"item_id": "abc"},
    data_version="1.0",
)

# WRONG - data_version is required
event = EventGridEvent(
    subject="/myapp/items/abc",
    event_type="MyApp.Events.ItemCreated",
    data={"item_id": "abc"},
)
```

---

## 6. Publishing events

### 6.1 ✅ CORRECT: Send a single CloudEvent
```python
from azure.eventgrid import EventGridPublisherClient, CloudEvent
from azure.identity import DefaultAzureCredential

client = EventGridPublisherClient(endpoint, DefaultAzureCredential())
event = CloudEvent(
    type="MyApp.Events.Created",
    source="/myapp/items",
    data={"id": "123"},
)
client.send(event)
```

### 6.2 ✅ CORRECT: Send a batch of CloudEvents
```python
events = [
    CloudEvent(
        type="MyApp.Events.Created",
        source="/myapp/items",
        data={"id": f"item-{i}"},
    )
    for i in range(3)
]
client.send(events)
```

### 6.3 ✅ CORRECT: Send EventGridEvent
```python
event = EventGridEvent(
    subject="/myapp/items/abc",
    event_type="MyApp.Events.ItemCreated",
    data={"item_id": "abc"},
    data_version="1.0",
)
client.send(event)
```

### 6.4 ✅ CORRECT: Namespace Topic (Async)
```python
from azure.eventgrid.aio import EventGridPublisherClient
from azure.eventgrid import CloudEvent
from azure.identity.aio import DefaultAzureCredential

namespace_endpoint = os.environ["EVENTGRID_NAMESPACE_ENDPOINT"]
topic_name = "my-topic"

async with EventGridPublisherClient(namespace_endpoint, DefaultAzureCredential()) as client:
    event = CloudEvent(
        type="MyApp.Events.Created",
        source="/myapp/items",
        data={"id": "123"},
    )
    await client.send(event, namespace_topic=topic_name)
```

### 6.5 ❌ INCORRECT: Wrong send usage
```python
# WRONG - using await with sync client
client = EventGridPublisherClient(endpoint, DefaultAzureCredential())
await client.send(event)

# WRONG - namespace_topic with topic endpoint
client.send(event, namespace_topic="my-topic")
```
