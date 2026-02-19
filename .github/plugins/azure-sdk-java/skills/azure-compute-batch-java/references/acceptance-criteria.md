# Azure Batch SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-compute-batch`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/batch/azure-compute-batch
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Client and Builder
```java
import com.azure.compute.batch.BatchClient;
import com.azure.compute.batch.BatchClientBuilder;
import com.azure.compute.batch.BatchAsyncClient;
```

#### ✅ CORRECT: Authentication
```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.core.credential.AzureNamedKeyCredential;
```

### 1.2 Model Imports

#### ✅ CORRECT: Batch Models
```java
import com.azure.compute.batch.models.BatchPool;
import com.azure.compute.batch.models.BatchPoolCreateParameters;
import com.azure.compute.batch.models.BatchPoolResizeParameters;
import com.azure.compute.batch.models.BatchJob;
import com.azure.compute.batch.models.BatchJobCreateParameters;
import com.azure.compute.batch.models.BatchTask;
import com.azure.compute.batch.models.BatchTaskCreateParameters;
import com.azure.compute.batch.models.BatchTaskGroup;
import com.azure.compute.batch.models.VirtualMachineConfiguration;
import com.azure.compute.batch.models.BatchVmImageReference;
import com.azure.compute.batch.models.BatchPoolInfo;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Builder with DefaultAzureCredential
```java
String endpoint = System.getenv("AZURE_BATCH_ENDPOINT");

BatchClient batchClient = new BatchClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint)
    .buildClient();
```

### 2.2 ✅ CORRECT: Builder with Shared Key
```java
String accountName = System.getenv("AZURE_BATCH_ACCOUNT");
String accountKey = System.getenv("AZURE_BATCH_ACCESS_KEY");
AzureNamedKeyCredential sharedKeyCreds = new AzureNamedKeyCredential(accountName, accountKey);

BatchClient batchClient = new BatchClientBuilder()
    .credential(sharedKeyCreds)
    .endpoint(endpoint)
    .buildClient();
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials
```java
// WRONG - hardcoded values
BatchClient client = new BatchClientBuilder()
    .endpoint("https://mybatch.region.batch.azure.com")
    .credential(new AzureNamedKeyCredential("account", "key"))
    .buildClient();
```

---

## 3. Pool Operations

### 3.1 ✅ CORRECT: Create Pool
```java
batchClient.createPool(new BatchPoolCreateParameters("myPoolId", "STANDARD_DC2s_V2")
    .setVirtualMachineConfiguration(
        new VirtualMachineConfiguration(
            new BatchVmImageReference()
                .setPublisher("Canonical")
                .setOffer("UbuntuServer")
                .setSku("22_04-lts"),
            "batch.node.ubuntu 22.04"))
    .setTargetDedicatedNodes(2), null);
```

### 3.2 ✅ CORRECT: Get Pool
```java
BatchPool pool = batchClient.getPool("myPoolId");
System.out.println("Pool state: " + pool.getState());
```

### 3.3 ✅ CORRECT: List Pools
```java
PagedIterable<BatchPool> pools = batchClient.listPools();
for (BatchPool pool : pools) {
    System.out.println("Pool: " + pool.getId());
}
```

---

## 4. Job Operations

### 4.1 ✅ CORRECT: Create Job
```java
batchClient.createJob(
    new BatchJobCreateParameters("myJobId", new BatchPoolInfo().setPoolId("myPoolId"))
        .setPriority(100),
    null);
```

### 4.2 ✅ CORRECT: Get Task Counts
```java
BatchTaskCountsResult counts = batchClient.getJobTaskCounts("myJobId");
System.out.println("Running: " + counts.getTaskCounts().getRunning());
```

---

## 5. Task Operations

### 5.1 ✅ CORRECT: Create Single Task
```java
BatchTaskCreateParameters task = new BatchTaskCreateParameters("task1", "echo 'Hello World'");
batchClient.createTask("myJobId", task);
```

### 5.2 ✅ CORRECT: Create Task Collection
```java
List<BatchTaskCreateParameters> taskList = Arrays.asList(
    new BatchTaskCreateParameters("task1", "echo Task 1"),
    new BatchTaskCreateParameters("task2", "echo Task 2")
);
BatchTaskGroup taskGroup = new BatchTaskGroup(taskList);
batchClient.createTaskCollection("myJobId", taskGroup);
```

---

## 6. Error Handling

### 6.1 ✅ CORRECT: BatchErrorException Handling
```java
import com.azure.compute.batch.models.BatchErrorException;
import com.azure.compute.batch.models.BatchError;

try {
    batchClient.getPool("nonexistent-pool");
} catch (BatchErrorException e) {
    BatchError error = e.getValue();
    System.err.println("Error code: " + error.getCode());
    System.err.println("Message: " + error.getMessage().getValue());
}
```

---

## 7. Best Practices Checklist

- [ ] Use Entra ID (DefaultAzureCredential) over shared key
- [ ] Use environment variables for configuration
- [ ] Use `createTaskCollection` for batch task creation
- [ ] Handle long-running operations (resize, delete) with pollers
- [ ] Set appropriate job constraints (maxWallClockTime, maxTaskRetryCount)
- [ ] Use low-priority nodes for cost savings when appropriate
