# Azure Compute Batch Acceptance Criteria

**SDK**: `com.azure:azure-compute-batch`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/batch/azure-compute-batch
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Full qualified client imports
```java
import com.azure.compute.batch.BatchClient;
import com.azure.compute.batch.BatchClientBuilder;
import com.azure.compute.batch.BatchAsyncClient;
```

#### ❌ INCORRECT: Old package imports
```java
import com.microsoft.azure.batch.BatchClient;
```

### 1.2 Model Imports
#### ✅ CORRECT: Models from compute.batch.models package
```java
import com.azure.compute.batch.models.*;
```

### 1.3 Credential Imports
#### ✅ CORRECT: Authentication credentials
```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.core.credential.AzureNamedKeyCredential;
```

---

## 2. Client Creation Patterns

### 2.1 With Microsoft Entra ID (Recommended)
#### ✅ CORRECT: DefaultAzureCredential
```java
BatchClient batchClient = new BatchClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(System.getenv("AZURE_BATCH_ENDPOINT"))
    .buildClient();
```

### 2.2 With Shared Key Credentials
#### ✅ CORRECT: AzureNamedKeyCredential
```java
String accountName = System.getenv("AZURE_BATCH_ACCOUNT");
String accountKey = System.getenv("AZURE_BATCH_ACCESS_KEY");
AzureNamedKeyCredential sharedKeyCreds = new AzureNamedKeyCredential(accountName, accountKey);

BatchClient batchClient = new BatchClientBuilder()
    .credential(sharedKeyCreds)
    .endpoint(System.getenv("AZURE_BATCH_ENDPOINT"))
    .buildClient();
```

### 2.3 Async Client
#### ✅ CORRECT: Async client creation
```java
BatchAsyncClient batchAsyncClient = new BatchClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(System.getenv("AZURE_BATCH_ENDPOINT"))
    .buildAsyncClient();
```

#### ❌ INCORRECT: Missing endpoint
```java
BatchClient batchClient = new BatchClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

---

## 3. Pool Operations

### 3.1 Create Pool
#### ✅ CORRECT: Full pool creation
```java
batchClient.createPool(new BatchPoolCreateParameters("myPoolId", "STANDARD_DC2s_V2")
    .setVirtualMachineConfiguration(
        new VirtualMachineConfiguration(
            new BatchVmImageReference()
                .setPublisher("Canonical")
                .setOffer("UbuntuServer")
                .setSku("22_04-lts")
                .setVersion("latest"),
            "batch.node.ubuntu 22.04"))
    .setTargetDedicatedNodes(2)
    .setTargetLowPriorityNodes(0), null);
```

#### ❌ INCORRECT: Missing VM configuration
```java
batchClient.createPool(new BatchPoolCreateParameters("myPoolId", "STANDARD_DC2s_V2"), null);
```

### 3.2 Get Pool
#### ✅ CORRECT: Retrieve pool
```java
BatchPool pool = batchClient.getPool("myPoolId");
System.out.println("Pool state: " + pool.getState());
System.out.println("Current dedicated nodes: " + pool.getCurrentDedicatedNodes());
```

### 3.3 List Pools
#### ✅ CORRECT: With PagedIterable
```java
PagedIterable<BatchPool> pools = batchClient.listPools();
for (BatchPool pool : pools) {
    System.out.println("Pool: " + pool.getId() + ", State: " + pool.getState());
}
```

### 3.4 Resize Pool
#### ✅ CORRECT: Using SyncPoller for LRO
```java
BatchPoolResizeParameters resizeParams = new BatchPoolResizeParameters()
    .setTargetDedicatedNodes(4)
    .setTargetLowPriorityNodes(2);

SyncPoller<BatchPool, BatchPool> poller = batchClient.beginResizePool("myPoolId", resizeParams);
poller.waitForCompletion();
BatchPool resizedPool = poller.getFinalResult();
```

### 3.5 Enable AutoScale
#### ✅ CORRECT: AutoScale with formula
```java
BatchPoolEnableAutoScaleParameters autoScaleParams = new BatchPoolEnableAutoScaleParameters()
    .setAutoScaleEvaluationInterval(Duration.ofMinutes(5))
    .setAutoScaleFormula("$TargetDedicatedNodes = min(10, $PendingTasks.GetSample(TimeInterval_Minute * 5));");

batchClient.enablePoolAutoScale("myPoolId", autoScaleParams);
```

### 3.6 Delete Pool
#### ✅ CORRECT: Using SyncPoller for LRO
```java
SyncPoller<BatchPool, Void> deletePoller = batchClient.beginDeletePool("myPoolId");
deletePoller.waitForCompletion();
```

---

## 4. Job Operations

### 4.1 Create Job
#### ✅ CORRECT: With pool info and constraints
```java
batchClient.createJob(
    new BatchJobCreateParameters("myJobId", new BatchPoolInfo().setPoolId("myPoolId"))
        .setPriority(100)
        .setConstraints(new BatchJobConstraints()
            .setMaxWallClockTime(Duration.ofHours(24))
            .setMaxTaskRetryCount(3)),
    null);
```

#### ❌ INCORRECT: Missing pool info
```java
batchClient.createJob(new BatchJobCreateParameters("myJobId", null), null);
```

### 4.2 Get Job
#### ✅ CORRECT: Retrieve job
```java
BatchJob job = batchClient.getJob("myJobId", null, null);
System.out.println("Job state: " + job.getState());
```

### 4.3 List Jobs
#### ✅ CORRECT: With options
```java
PagedIterable<BatchJob> jobs = batchClient.listJobs(new BatchJobsListOptions());
for (BatchJob job : jobs) {
    System.out.println("Job: " + job.getId() + ", State: " + job.getState());
}
```

### 4.4 Get Task Counts
#### ✅ CORRECT: Monitor progress
```java
BatchTaskCountsResult counts = batchClient.getJobTaskCounts("myJobId");
System.out.println("Active: " + counts.getTaskCounts().getActive());
System.out.println("Running: " + counts.getTaskCounts().getRunning());
System.out.println("Completed: " + counts.getTaskCounts().getCompleted());
```

### 4.5 Terminate Job
#### ✅ CORRECT: Using SyncPoller
```java
BatchJobTerminateParameters terminateParams = new BatchJobTerminateParameters()
    .setTerminationReason("Manual termination");
BatchJobTerminateOptions options = new BatchJobTerminateOptions().setParameters(terminateParams);

SyncPoller<BatchJob, BatchJob> poller = batchClient.beginTerminateJob("myJobId", options, null);
poller.waitForCompletion();
```

---

## 5. Task Operations

### 5.1 Create Single Task
#### ✅ CORRECT: Simple task
```java
BatchTaskCreateParameters task = new BatchTaskCreateParameters("task1", "echo 'Hello World'");
batchClient.createTask("myJobId", task);
```

### 5.2 Create Task with Exit Conditions
#### ✅ CORRECT: With exit conditions and user identity
```java
batchClient.createTask("myJobId", new BatchTaskCreateParameters("task2", "cmd /c exit 3")
    .setExitConditions(new ExitConditions()
        .setExitCodeRanges(Arrays.asList(
            new ExitCodeRangeMapping(2, 4, 
                new ExitOptions().setJobAction(BatchJobActionKind.TERMINATE)))))
    .setUserIdentity(new UserIdentity()
        .setAutoUser(new AutoUserSpecification()
            .setScope(AutoUserScope.TASK)
            .setElevationLevel(ElevationLevel.NON_ADMIN))),
    null);
```

### 5.3 Create Task Collection (up to 100)
#### ✅ CORRECT: Batch create
```java
List<BatchTaskCreateParameters> taskList = Arrays.asList(
    new BatchTaskCreateParameters("task1", "echo Task 1"),
    new BatchTaskCreateParameters("task2", "echo Task 2"),
    new BatchTaskCreateParameters("task3", "echo Task 3")
);
BatchTaskGroup taskGroup = new BatchTaskGroup(taskList);
BatchCreateTaskCollectionResult result = batchClient.createTaskCollection("myJobId", taskGroup);
```

### 5.4 Create Many Tasks (no limit)
#### ✅ CORRECT: For more than 100 tasks
```java
List<BatchTaskCreateParameters> tasks = new ArrayList<>();
for (int i = 0; i < 1000; i++) {
    tasks.add(new BatchTaskCreateParameters("task" + i, "echo Task " + i));
}
batchClient.createTasks("myJobId", tasks);
```

### 5.5 Get Task
#### ✅ CORRECT: Retrieve task
```java
BatchTask task = batchClient.getTask("myJobId", "task1");
System.out.println("Task state: " + task.getState());
System.out.println("Exit code: " + task.getExecutionInfo().getExitCode());
```

### 5.6 Get Task Output
#### ✅ CORRECT: Read stdout
```java
BinaryData stdout = batchClient.getTaskFile("myJobId", "task1", "stdout.txt");
System.out.println(new String(stdout.toBytes(), StandardCharsets.UTF_8));
```

---

## 6. Node Operations

### 6.1 List Nodes
#### ✅ CORRECT: With options
```java
PagedIterable<BatchNode> nodes = batchClient.listNodes("myPoolId", new BatchNodesListOptions());
for (BatchNode node : nodes) {
    System.out.println("Node: " + node.getId() + ", State: " + node.getState());
}
```

### 6.2 Reboot Node
#### ✅ CORRECT: Using SyncPoller
```java
SyncPoller<BatchNode, BatchNode> rebootPoller = batchClient.beginRebootNode("myPoolId", "nodeId");
rebootPoller.waitForCompletion();
```

### 6.3 Get Remote Login Settings
#### ✅ CORRECT: For SSH access
```java
BatchNodeRemoteLoginSettings settings = batchClient.getNodeRemoteLoginSettings("myPoolId", "nodeId");
System.out.println("IP: " + settings.getRemoteLoginIpAddress());
System.out.println("Port: " + settings.getRemoteLoginPort());
```

---

## 7. Job Schedule Operations

### 7.1 Create Job Schedule
#### ✅ CORRECT: Recurring job
```java
batchClient.createJobSchedule(new BatchJobScheduleCreateParameters("myScheduleId",
    new BatchJobScheduleConfiguration()
        .setRecurrenceInterval(Duration.ofHours(6))
        .setDoNotRunUntil(OffsetDateTime.now().plusDays(1)),
    new BatchJobSpecification(new BatchPoolInfo().setPoolId("myPoolId"))
        .setPriority(50)),
    null);
```

---

## 8. Error Handling

### 8.1 BatchErrorException
#### ✅ CORRECT: Specific error handling
```java
try {
    batchClient.getPool("nonexistent-pool");
} catch (BatchErrorException e) {
    BatchError error = e.getValue();
    System.err.println("Error code: " + error.getCode());
    System.err.println("Message: " + error.getMessage().getValue());
    
    if ("PoolNotFound".equals(error.getCode())) {
        System.err.println("The specified pool does not exist.");
    }
}
```

#### ❌ INCORRECT: Catching generic exception
```java
try {
    batchClient.getPool("nonexistent-pool");
} catch (Exception e) {
    // Too broad
}
```

---

## 9. Required Dependencies

### 9.1 Maven Configuration
#### ✅ CORRECT: Current version
```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-compute-batch</artifactId>
    <version>1.0.0-beta.5</version>
</dependency>
```

---

## 10. Environment Variables

### 10.1 Required Variables
```bash
AZURE_BATCH_ENDPOINT=https://<account>.<region>.batch.azure.com
AZURE_BATCH_ACCOUNT=<account-name>
AZURE_BATCH_ACCESS_KEY=<account-key>
```

---

## 11. Best Practices

### 11.1 Authentication
- Use Entra ID (DefaultAzureCredential) over shared key for production
- Use management SDK (`azure-resourcemanager-batch`) for pool operations with managed identities

### 11.2 Task Management
- Use `createTaskCollection` for batches up to 100 tasks
- Use `createTasks` for larger batches (no limit)
- Set `maxWallClockTime` and `maxTaskRetryCount` constraints

### 11.3 Long-Running Operations
- Pool resize and delete are LRO - use SyncPoller
- Monitor with `waitForCompletion()` or poll status

### 11.4 Cost Optimization
- Use low-priority nodes for fault-tolerant workloads
- Enable autoscale to dynamically adjust pool size
