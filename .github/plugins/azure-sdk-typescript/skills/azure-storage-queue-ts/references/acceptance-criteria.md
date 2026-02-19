# Azure Storage Queue SDK Acceptance Criteria (TypeScript)

**SDK**: `@azure/storage-queue`
**Repository**: https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/storage/storage-queue
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Core Client Imports
```typescript
import { QueueServiceClient, QueueClient } from "@azure/storage-queue";
```

#### ✅ CORRECT: With Authentication
```typescript
import { QueueServiceClient, StorageSharedKeyCredential } from "@azure/storage-queue";
import { DefaultAzureCredential } from "@azure/identity";
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong package name
```typescript
// WRONG - package is @azure/storage-queue
import { QueueServiceClient } from "@azure/storage-queues";
import { QueueServiceClient } from "azure-storage";
```

---

## 2. Authentication Patterns

### 2.1 ✅ CORRECT: DefaultAzureCredential (Recommended)
```typescript
import { QueueServiceClient } from "@azure/storage-queue";
import { DefaultAzureCredential } from "@azure/identity";

const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const client = new QueueServiceClient(
  `https://${accountName}.queue.core.windows.net`,
  new DefaultAzureCredential()
);
```

### 2.2 ✅ CORRECT: Connection String
```typescript
import { QueueServiceClient } from "@azure/storage-queue";

const client = QueueServiceClient.fromConnectionString(
  process.env.AZURE_STORAGE_CONNECTION_STRING!
);
```

### 2.3 ✅ CORRECT: StorageSharedKeyCredential
```typescript
import { QueueServiceClient, StorageSharedKeyCredential } from "@azure/storage-queue";

const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const accountKey = process.env.AZURE_STORAGE_ACCOUNT_KEY!;

const sharedKeyCredential = new StorageSharedKeyCredential(accountName, accountKey);
const client = new QueueServiceClient(
  `https://${accountName}.queue.core.windows.net`,
  sharedKeyCredential
);
```

### 2.4 ✅ CORRECT: SAS Token
```typescript
import { QueueServiceClient } from "@azure/storage-queue";

const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const sasToken = process.env.AZURE_STORAGE_SAS_TOKEN!;

const client = new QueueServiceClient(
  `https://${accountName}.queue.core.windows.net${sasToken}`
);
```

### 2.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials
```typescript
// WRONG - hardcoded account key
const sharedKeyCredential = new StorageSharedKeyCredential(
  "myaccount",
  "myaccountkey12345"
);
```

---

## 3. Queue Operations Patterns

### 3.1 ✅ CORRECT: Create Queue
```typescript
const queueClient = client.getQueueClient("my-queue");
await queueClient.create();

// Or create if not exists
await queueClient.createIfNotExists();
```

### 3.2 ✅ CORRECT: List Queues
```typescript
for await (const queue of client.listQueues()) {
  console.log(queue.name);
}

// With prefix filter
for await (const queue of client.listQueues({ prefix: "task-" })) {
  console.log(queue.name);
}
```

### 3.3 ✅ CORRECT: Delete Queue
```typescript
await queueClient.delete();

// Or delete if exists
await queueClient.deleteIfExists();
```

### 3.4 ✅ CORRECT: Get Queue Properties
```typescript
const properties = await queueClient.getProperties();
console.log("Approximate message count:", properties.approximateMessagesCount);
console.log("Metadata:", properties.metadata);
```

### 3.5 ✅ CORRECT: Set Queue Metadata
```typescript
await queueClient.setMetadata({
  department: "engineering",
  priority: "high",
});
```

---

## 4. Message Operations Patterns

### 4.1 ✅ CORRECT: Send Message
```typescript
const queueClient = client.getQueueClient("my-queue");

// Simple message
await queueClient.sendMessage("Hello, World!");

// With options
await queueClient.sendMessage("Delayed message", {
  visibilityTimeout: 60,
  messageTimeToLive: 3600,
});

// JSON message
const task = { type: "process", data: { id: 123 } };
await queueClient.sendMessage(JSON.stringify(task));
```

### 4.2 ✅ CORRECT: Receive Messages
```typescript
const response = await queueClient.receiveMessages({
  numberOfMessages: 10,
  visibilityTimeout: 30,
});

for (const message of response.receivedMessageItems) {
  console.log("Message ID:", message.messageId);
  console.log("Content:", message.messageText);
  console.log("Dequeue Count:", message.dequeueCount);
  console.log("Pop Receipt:", message.popReceipt);
  
  // Delete after processing
  await queueClient.deleteMessage(message.messageId, message.popReceipt);
}
```

### 4.3 ✅ CORRECT: Peek Messages
```typescript
const response = await queueClient.peekMessages({
  numberOfMessages: 5,
});

for (const message of response.peekedMessageItems) {
  console.log("Message ID:", message.messageId);
  console.log("Content:", message.messageText);
}
```

### 4.4 ✅ CORRECT: Update Message
```typescript
const response = await queueClient.receiveMessages();
const message = response.receivedMessageItems[0];

if (message) {
  const updateResponse = await queueClient.updateMessage(
    message.messageId,
    message.popReceipt,
    "Updated content",
    60
  );
  
  console.log("New pop receipt:", updateResponse.popReceipt);
}
```

### 4.5 ✅ CORRECT: Delete Message
```typescript
const response = await queueClient.receiveMessages();
const message = response.receivedMessageItems[0];

if (message) {
  await queueClient.deleteMessage(message.messageId, message.popReceipt);
}
```

### 4.6 ✅ CORRECT: Clear All Messages
```typescript
await queueClient.clearMessages();
```

---

## 5. Message Processing Patterns

### 5.1 ✅ CORRECT: Basic Worker Pattern
```typescript
async function processQueue(queueClient: QueueClient): Promise<void> {
  while (true) {
    const response = await queueClient.receiveMessages({
      numberOfMessages: 10,
      visibilityTimeout: 30,
    });

    if (response.receivedMessageItems.length === 0) {
      await sleep(5000);
      continue;
    }

    for (const message of response.receivedMessageItems) {
      try {
        await processMessage(message.messageText);
        await queueClient.deleteMessage(message.messageId, message.popReceipt);
      } catch (error) {
        console.error(`Failed to process message ${message.messageId}:`, error);
      }
    }
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
```

### 5.2 ✅ CORRECT: Poison Message Handling
```typescript
const MAX_DEQUEUE_COUNT = 5;

async function processWithPoisonHandling(
  queueClient: QueueClient,
  poisonQueueClient: QueueClient
): Promise<void> {
  const response = await queueClient.receiveMessages({
    numberOfMessages: 10,
    visibilityTimeout: 30,
  });

  for (const message of response.receivedMessageItems) {
    if (message.dequeueCount > MAX_DEQUEUE_COUNT) {
      await poisonQueueClient.sendMessage(message.messageText);
      await queueClient.deleteMessage(message.messageId, message.popReceipt);
      console.log(`Moved message ${message.messageId} to poison queue`);
      continue;
    }

    try {
      await processMessage(message.messageText);
      await queueClient.deleteMessage(message.messageId, message.popReceipt);
    } catch (error) {
      console.error(`Processing failed (attempt ${message.dequeueCount}):`, error);
    }
  }
}
```

---

## 6. Message Encoding Patterns

### 6.1 ✅ CORRECT: Plain Text Encoding
```typescript
import { QueueClient } from "@azure/storage-queue";

const queueClient = new QueueClient(
  `https://${accountName}.queue.core.windows.net/my-queue`,
  credential,
  {
    messageEncoding: "text",
  }
);
```

---

## 7. SAS Token Generation Patterns

### 7.1 ✅ CORRECT: Generate Queue SAS
```typescript
import {
  QueueSASPermissions,
  generateQueueSASQueryParameters,
  StorageSharedKeyCredential,
} from "@azure/storage-queue";

const sharedKeyCredential = new StorageSharedKeyCredential(accountName, accountKey);

const sasToken = generateQueueSASQueryParameters(
  {
    queueName: "my-queue",
    permissions: QueueSASPermissions.parse("raup"),
    startsOn: new Date(),
    expiresOn: new Date(Date.now() + 3600 * 1000),
  },
  sharedKeyCredential
).toString();

const sasUrl = `https://${accountName}.queue.core.windows.net/my-queue?${sasToken}`;
```

---

## 8. Error Handling Patterns

### 8.1 ✅ CORRECT: Handle RestError
```typescript
import { RestError } from "@azure/storage-queue";

try {
  await queueClient.sendMessage("test");
} catch (error) {
  if (error instanceof RestError) {
    switch (error.statusCode) {
      case 404:
        console.log("Queue not found");
        break;
      case 400:
        console.log("Bad request - message too large or invalid");
        break;
      case 403:
        console.log("Access denied");
        break;
      case 409:
        console.log("Queue already exists or being deleted");
        break;
      default:
        console.error(`Storage error ${error.statusCode}: ${error.message}`);
    }
  }
  throw error;
}
```

---

## 9. Environment Variables

### 9.1 ✅ CORRECT: Required Variables
```typescript
const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const accountKey = process.env.AZURE_STORAGE_ACCOUNT_KEY!;
const connectionString = process.env.AZURE_STORAGE_CONNECTION_STRING!;
```

### 9.2 ❌ INCORRECT: Hardcoded values
```typescript
// WRONG - hardcoded account
const client = new QueueServiceClient(
  "https://myaccount.queue.core.windows.net",
  sharedKeyCredential
);
```
