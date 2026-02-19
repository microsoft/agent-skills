# Azure Service Bus SDK Acceptance Criteria (.NET)

**SDK**: `Azure.Messaging.ServiceBus`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/servicebus/Azure.Messaging.ServiceBus
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Using Statements

### 1.1 ✅ CORRECT: Core Service Bus Imports
```csharp
using Azure.Messaging.ServiceBus;
using Azure.Messaging.ServiceBus.Administration;
```

### 1.2 ✅ CORRECT: With Identity
```csharp
using Azure.Identity;
using Azure.Messaging.ServiceBus;
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong namespace
```csharp
// WRONG - Azure.Messaging.ServiceBus not Microsoft.Azure.ServiceBus
using Microsoft.Azure.ServiceBus;
```

---

## 2. Authentication

### 2.1 ✅ CORRECT: DefaultAzureCredential (Preferred)
```csharp
using Azure.Identity;
using Azure.Messaging.ServiceBus;

string fullyQualifiedNamespace = "<namespace>.servicebus.windows.net";
await using ServiceBusClient client = new(fullyQualifiedNamespace, new DefaultAzureCredential());
```

### 2.2 ✅ CORRECT: Connection String
```csharp
using Azure.Messaging.ServiceBus;

string connectionString = Environment.GetEnvironmentVariable("AZURE_SERVICEBUS_CONNECTION_STRING");
await using ServiceBusClient client = new(connectionString);
```

### 2.3 ✅ CORRECT: ASP.NET Core Dependency Injection
```csharp
using Azure.Identity;
using Microsoft.Extensions.Azure;

services.AddAzureClients(builder =>
{
    builder.AddServiceBusClientWithNamespace("<namespace>.servicebus.windows.net");
    builder.UseCredential(new DefaultAzureCredential());
});
```

### 2.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded connection string
```csharp
// WRONG - never hardcode connection strings
await using ServiceBusClient client = new("Endpoint=sb://myns.servicebus.windows.net/;SharedAccessKeyName=...");
```

---

## 3. Client Hierarchy

### 3.1 ✅ CORRECT: Understanding Client Types
```csharp
// ServiceBusClient is the main entry point
await using ServiceBusClient client = new(fullyQualifiedNamespace, credential);

// Create senders and receivers from the client
ServiceBusSender sender = client.CreateSender("my-queue");
ServiceBusReceiver receiver = client.CreateReceiver("my-queue");
ServiceBusProcessor processor = client.CreateProcessor("my-queue");
ServiceBusSessionReceiver sessionReceiver = await client.AcceptNextSessionAsync("my-queue");
```

---

## 4. Sending Messages

### 4.1 ✅ CORRECT: Send Single Message
```csharp
await using ServiceBusClient client = new(fullyQualifiedNamespace, new DefaultAzureCredential());
ServiceBusSender sender = client.CreateSender("my-queue");

ServiceBusMessage message = new("Hello world!");
await sender.SendMessageAsync(message);
```

### 4.2 ✅ CORRECT: Safe Batching (Recommended)
```csharp
using ServiceBusMessageBatch batch = await sender.CreateMessageBatchAsync();

if (batch.TryAddMessage(new ServiceBusMessage("Message 1")))
{
    // Message added successfully
}
if (batch.TryAddMessage(new ServiceBusMessage("Message 2")))
{
    // Message added successfully
}
await sender.SendMessagesAsync(batch);
```

### 4.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not using safe batching
```csharp
// WRONG - may fail if batch exceeds size limit
var messages = new List<ServiceBusMessage>
{
    new ServiceBusMessage("Message 1"),
    new ServiceBusMessage("Message 2")
};
await sender.SendMessagesAsync(messages);
```

---

## 5. Receiving Messages

### 5.1 ✅ CORRECT: Receive Single Message
```csharp
ServiceBusReceiver receiver = client.CreateReceiver("my-queue");

ServiceBusReceivedMessage message = await receiver.ReceiveMessageAsync();
string body = message.Body.ToString();
Console.WriteLine(body);

// Complete the message (removes from queue)
await receiver.CompleteMessageAsync(message);
```

### 5.2 ✅ CORRECT: Batch Receive
```csharp
IReadOnlyList<ServiceBusReceivedMessage> messages = await receiver.ReceiveMessagesAsync(maxMessages: 10);
foreach (var msg in messages)
{
    Console.WriteLine(msg.Body.ToString());
    await receiver.CompleteMessageAsync(msg);
}
```

### 5.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Forgetting to complete messages
```csharp
// WRONG - message will be redelivered after lock expires
var message = await receiver.ReceiveMessageAsync();
Console.WriteLine(message.Body.ToString());
// Missing: await receiver.CompleteMessageAsync(message);
```

---

## 6. Message Settlement

### 6.1 ✅ CORRECT: All Settlement Options
```csharp
// Complete - removes message from queue
await receiver.CompleteMessageAsync(message);

// Abandon - releases lock, message can be received again
await receiver.AbandonMessageAsync(message);

// Defer - prevents normal receive, use ReceiveDeferredMessageAsync
await receiver.DeferMessageAsync(message);

// Dead Letter - moves to dead letter subqueue
await receiver.DeadLetterMessageAsync(message, "InvalidFormat", "Message body was not valid JSON");
```

---

## 7. Background Processing with Processor

### 7.1 ✅ CORRECT: Using ServiceBusProcessor
```csharp
ServiceBusProcessor processor = client.CreateProcessor("my-queue", new ServiceBusProcessorOptions
{
    AutoCompleteMessages = false,
    MaxConcurrentCalls = 2
});

processor.ProcessMessageAsync += async (args) =>
{
    try
    {
        string body = args.Message.Body.ToString();
        Console.WriteLine($"Received: {body}");
        await args.CompleteMessageAsync(args.Message);
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error processing: {ex.Message}");
        await args.AbandonMessageAsync(args.Message);
    }
};

processor.ProcessErrorAsync += (args) =>
{
    Console.WriteLine($"Error source: {args.ErrorSource}");
    Console.WriteLine($"Entity: {args.EntityPath}");
    Console.WriteLine($"Exception: {args.Exception}");
    return Task.CompletedTask;
};

await processor.StartProcessingAsync();
// ... application runs
await processor.StopProcessingAsync();
```

### 7.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not handling ProcessErrorAsync
```csharp
// WRONG - always register error handler
processor.ProcessMessageAsync += async (args) =>
{
    await args.CompleteMessageAsync(args.Message);
};
// Missing: processor.ProcessErrorAsync += ...
await processor.StartProcessingAsync();
```

---

## 8. Sessions (Ordered Processing)

### 8.1 ✅ CORRECT: Send Session Message
```csharp
ServiceBusMessage message = new("Hello")
{
    SessionId = "order-123"
};
await sender.SendMessageAsync(message);
```

### 8.2 ✅ CORRECT: Receive from Session
```csharp
// Receive from next available session
ServiceBusSessionReceiver receiver = await client.AcceptNextSessionAsync("my-queue");

// Or receive from specific session
ServiceBusSessionReceiver receiver = await client.AcceptSessionAsync("my-queue", "order-123");

// Session state management
await receiver.SetSessionStateAsync(new BinaryData("processing"));
BinaryData state = await receiver.GetSessionStateAsync();

// Renew session lock
await receiver.RenewSessionLockAsync();
```

---

## 9. Dead Letter Queue

### 9.1 ✅ CORRECT: Receive from Dead Letter Queue
```csharp
ServiceBusReceiver dlqReceiver = client.CreateReceiver("my-queue", new ServiceBusReceiverOptions
{
    SubQueue = SubQueue.DeadLetter
});

ServiceBusReceivedMessage dlqMessage = await dlqReceiver.ReceiveMessageAsync();

// Access dead letter metadata
string reason = dlqMessage.DeadLetterReason;
string description = dlqMessage.DeadLetterErrorDescription;
Console.WriteLine($"Dead letter reason: {reason} - {description}");
```

---

## 10. Topics and Subscriptions

### 10.1 ✅ CORRECT: Send to Topic and Receive from Subscription
```csharp
// Send to topic
ServiceBusSender topicSender = client.CreateSender("my-topic");
await topicSender.SendMessageAsync(new ServiceBusMessage("Broadcast message"));

// Receive from subscription
ServiceBusReceiver subReceiver = client.CreateReceiver("my-topic", "my-subscription");
var message = await subReceiver.ReceiveMessageAsync();
```

---

## 11. Administration (CRUD)

### 11.1 ✅ CORRECT: Create Queue
```csharp
var adminClient = new ServiceBusAdministrationClient(
    fullyQualifiedNamespace, 
    new DefaultAzureCredential());

var options = new CreateQueueOptions("my-queue")
{
    MaxDeliveryCount = 10,
    LockDuration = TimeSpan.FromSeconds(30),
    RequiresSession = true,
    DeadLetteringOnMessageExpiration = true
};
QueueProperties queue = await adminClient.CreateQueueAsync(options);
```

### 11.2 ✅ CORRECT: Create Topic and Subscription
```csharp
await adminClient.CreateTopicAsync(new CreateTopicOptions("my-topic"));
await adminClient.CreateSubscriptionAsync(
    new CreateSubscriptionOptions("my-topic", "my-subscription"));
```

---

## 12. Cross-Entity Transactions

### 12.1 ✅ CORRECT: Transaction Scope
```csharp
var options = new ServiceBusClientOptions { EnableCrossEntityTransactions = true };
await using var client = new ServiceBusClient(connectionString, options);

ServiceBusReceiver receiverA = client.CreateReceiver("queueA");
ServiceBusSender senderB = client.CreateSender("queueB");

ServiceBusReceivedMessage receivedMessage = await receiverA.ReceiveMessageAsync();

using (var ts = new TransactionScope(TransactionScopeAsyncFlowOption.Enabled))
{
    await receiverA.CompleteMessageAsync(receivedMessage);
    await senderB.SendMessageAsync(new ServiceBusMessage("Forwarded"));
    ts.Complete();
}
```

---

## 13. Error Handling

### 13.1 ✅ CORRECT: Handling Service Bus Exceptions
```csharp
using Azure.Messaging.ServiceBus;

try
{
    await sender.SendMessageAsync(message);
}
catch (ServiceBusException ex) when (ex.Reason == ServiceBusFailureReason.ServiceBusy)
{
    // Retry with backoff
    await Task.Delay(TimeSpan.FromSeconds(5));
}
catch (ServiceBusException ex)
{
    Console.WriteLine($"Service Bus Error: {ex.Reason} - {ex.Message}");
}
```

### 13.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Generic exception handling
```csharp
// WRONG - use specific ServiceBusException
try
{
    await sender.SendMessageAsync(message);
}
catch (Exception ex)
{
    Console.WriteLine(ex.Message);
}
```

---

## 14. Resource Management

### 14.1 ✅ CORRECT: Proper Disposal Pattern
```csharp
await using ServiceBusClient client = new(fullyQualifiedNamespace, credential);
ServiceBusSender sender = client.CreateSender("my-queue");

try
{
    await sender.SendMessageAsync(message);
}
finally
{
    await sender.DisposeAsync();
}
```

### 14.2 ✅ CORRECT: Singleton Pattern (Recommended)
```csharp
// Clients are thread-safe and should be reused
public class MessageService
{
    private readonly ServiceBusClient _client;
    private readonly ServiceBusSender _sender;
    
    public MessageService(string fullyQualifiedNamespace)
    {
        _client = new ServiceBusClient(fullyQualifiedNamespace, new DefaultAzureCredential());
        _sender = _client.CreateSender("my-queue");
    }
    
    public async Task SendAsync(string message)
    {
        await _sender.SendMessageAsync(new ServiceBusMessage(message));
    }
}
```

---

## Key Types Reference

| Type | Purpose |
|------|---------|
| `ServiceBusClient` | Main entry point, manages connection |
| `ServiceBusSender` | Sends messages to queues/topics |
| `ServiceBusReceiver` | Receives messages from queues/subscriptions |
| `ServiceBusSessionReceiver` | Receives session messages |
| `ServiceBusProcessor` | Background message processing |
| `ServiceBusSessionProcessor` | Background session processing |
| `ServiceBusAdministrationClient` | CRUD for queues/topics/subscriptions |
| `ServiceBusMessage` | Message to send |
| `ServiceBusReceivedMessage` | Received message with metadata |
| `ServiceBusMessageBatch` | Batch of messages |
