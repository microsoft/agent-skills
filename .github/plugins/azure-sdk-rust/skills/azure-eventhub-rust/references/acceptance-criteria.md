# Azure Event Hubs SDK for Rust Acceptance Criteria

**Crate**: `azure_messaging_eventhubs`
**Repository**: https://github.com/Azure/azure-sdk-for-rust/tree/main/sdk/eventhubs/azure_messaging_eventhubs
**Purpose**: Skill testing acceptance criteria for validating generated Rust code correctness

---

## 1. Correct Import Patterns

### 1.1 ✅ CORRECT: Client Imports
```rust
use azure_messaging_eventhubs::ProducerClient;
use azure_messaging_eventhubs::ConsumerClient;
use azure_identity::DeveloperToolsCredential;
```

---

## 2. Producer Client

### 2.1 ✅ CORRECT: Create Producer with Builder Pattern
```rust
use azure_identity::DeveloperToolsCredential;
use azure_messaging_eventhubs::ProducerClient;

let credential = DeveloperToolsCredential::new(None)?;
let producer = ProducerClient::builder()
    .open("<namespace>.servicebus.windows.net", "eventhub-name", credential.clone())
    .await?;
```

### 2.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Direct instantiation
```rust
// WRONG - use builder pattern
let producer = ProducerClient::new(...);
```

---

## 3. Sending Events

### 3.1 ✅ CORRECT: Send Single Event
```rust
producer.send_event(vec![1, 2, 3, 4], None).await?;
```

### 3.2 ✅ CORRECT: Send Batch
```rust
let batch = producer.create_batch(None).await?;
batch.try_add_event_data(b"event 1".to_vec(), None)?;
batch.try_add_event_data(b"event 2".to_vec(), None)?;

producer.send_batch(batch, None).await?;
```

### 3.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Ignoring batch capacity
```rust
// WRONG - check return value of try_add_event_data
batch.try_add_event_data(data, None);  // Should check if returned true
```

---

## 4. Consumer Client

### 4.1 ✅ CORRECT: Create Consumer with Builder Pattern
```rust
use azure_messaging_eventhubs::ConsumerClient;

let credential = DeveloperToolsCredential::new(None)?;
let consumer = ConsumerClient::builder()
    .open("<namespace>.servicebus.windows.net", "eventhub-name", credential.clone())
    .await?;
```

### 4.2 ✅ CORRECT: Receive Events from Partition
```rust
let receiver = consumer.open_partition_receiver("0", None).await?;

let events = receiver.receive_events(100, None).await?;
for event in events {
    println!("Event data: {:?}", event.body());
}
```

---

## 5. Event Hub Properties

### 5.1 ✅ CORRECT: Get Event Hub Properties
```rust
let properties = consumer.get_eventhub_properties(None).await?;
println!("Partitions: {:?}", properties.partition_ids);
```

### 5.2 ✅ CORRECT: Get Partition Properties
```rust
let partition_props = consumer.get_partition_properties("0", None).await?;
```

---

## 6. Best Practices

### 6.1 ✅ CORRECT: Use builder pattern for clients
```rust
let producer = ProducerClient::builder()
    .open(host, eventhub, credential)
    .await?;
```

### 6.2 ✅ CORRECT: Check batch capacity
```rust
if !batch.try_add_event_data(data, None)? {
    // Batch is full, send it and create a new one
    producer.send_batch(batch, None).await?;
    batch = producer.create_batch(None).await?;
}
```
