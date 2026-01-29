# Azure Batch Java SDK - Examples

Comprehensive code examples for the Azure Batch SDK for Java.

## Table of Contents

- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Pool Operations](#pool-operations)
- [Job Operations](#job-operations)
- [Task Operations](#task-operations)
- [Node Operations](#node-operations)
- [Job Schedule Operations](#job-schedule-operations)
- [Error Handling](#error-handling)
- [Complete Application Example](#complete-application-example)

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-compute-batch</artifactId>
    <version>1.0.0-beta.5</version>
</dependency>

<!-- For DefaultAzureCredential -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
    <version>1.14.2</version>
</dependency>
```

## Client Creation

### With Microsoft Entra ID (Recommended)

```java
import com.azure.compute.batch.BatchClient;
import com.azure.compute.batch.BatchClientBuilder;
import com.azure.identity.DefaultAzureCredentialBuilder;

String endpoint = System.getenv("AZURE_BATCH_ENDPOINT");

BatchClient batchClient = new BatchClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint)
    .buildClient();
```

### Async Client

```java
import com.azure.compute.batch.BatchAsyncClient;

BatchAsyncClient batchAsyncClient = new BatchClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint)
    .buildAsyncClient();
```

### With Shared Key Credentials

```java
import com.azure.core.credential.AzureNamedKeyCredential;

String accountName = System.getenv("AZURE_BATCH_ACCOUNT");
String accountKey = System.getenv("AZURE_BATCH_ACCESS_KEY");

AzureNamedKeyCredential sharedKeyCreds = new AzureNamedKeyCredential(accountName, accountKey);

BatchClient batchClient = new BatchClientBuilder()
    .credential(sharedKeyCreds)
    .endpoint(endpoint)
    .buildClient();
```

## Pool Operations

### Create Pool

```java
import com.azure.compute.batch.models.*;

batchClient.createPool(new BatchPoolCreateParameters("myPoolId", "STANDARD_DC2s_v2")
    .setVirtualMachineConfiguration(
        new VirtualMachineConfiguration(
            new BatchVmImageReference()
                .setPublisher("Canonical")
                .setOffer("UbuntuServer")
                .setSku("22_04-lts")
                .setVersion("latest"),
            "batch.node.ubuntu 22.04"))
    .setTargetDedicatedNodes(2)
    .setTargetLowPriorityNodes(0)
    .setTaskSlotsPerNode(4)
    .setTaskSchedulingPolicy(new TaskSchedulingPolicy(ComputeNodeFillType.SPREAD)), null);

System.out.println("Pool created: myPoolId");
```

### Create Pool with Start Task

```java
batchClient.createPool(new BatchPoolCreateParameters("myPoolWithStartTask", "STANDARD_D2s_v3")
    .setVirtualMachineConfiguration(
        new VirtualMachineConfiguration(
            new BatchVmImageReference()
                .setPublisher("Canonical")
                .setOffer("0001-com-ubuntu-server-jammy")
                .setSku("22_04-lts")
                .setVersion("latest"),
            "batch.node.ubuntu 22.04"))
    .setTargetDedicatedNodes(2)
    .setStartTask(new StartTask("apt-get update && apt-get install -y python3")
        .setUserIdentity(new UserIdentity()
            .setAutoUser(new AutoUserSpecification()
                .setScope(AutoUserScope.POOL)
                .setElevationLevel(ElevationLevel.ADMIN)))
        .setMaxTaskRetryCount(2)
        .setWaitForSuccess(true)), null);
```

### Create Pool with Application Packages

```java
import java.util.Arrays;

batchClient.createPool(new BatchPoolCreateParameters("appPackagePool", "STANDARD_D2s_v3")
    .setVirtualMachineConfiguration(
        new VirtualMachineConfiguration(
            new BatchVmImageReference()
                .setPublisher("MicrosoftWindowsServer")
                .setOffer("WindowsServer")
                .setSku("2022-datacenter")
                .setVersion("latest"),
            "batch.node.windows amd64"))
    .setTargetDedicatedNodes(2)
    .setApplicationPackageReferences(Arrays.asList(
        new ApplicationPackageReference("myApp").setVersion("1.0"),
        new ApplicationPackageReference("myDependency").setVersion("2.0"))), null);
```

### Get Pool

```java
BatchPool pool = batchClient.getPool("myPoolId");

System.out.println("=== Pool Details ===");
System.out.println("Pool ID: " + pool.getId());
System.out.println("State: " + pool.getState());
System.out.println("Allocation State: " + pool.getAllocationState());
System.out.println("VM Size: " + pool.getVmSize());
System.out.println("Current Dedicated Nodes: " + pool.getCurrentDedicatedNodes());
System.out.println("Current Low Priority Nodes: " + pool.getCurrentLowPriorityNodes());
System.out.println("Target Dedicated Nodes: " + pool.getTargetDedicatedNodes());
```

### List Pools

```java
import com.azure.core.http.rest.PagedIterable;

PagedIterable<BatchPool> pools = batchClient.listPools();

System.out.println("=== Available Pools ===");
for (BatchPool p : pools) {
    System.out.printf("Pool: %s, State: %s, Nodes: %d/%d%n",
        p.getId(),
        p.getState(),
        p.getCurrentDedicatedNodes(),
        p.getTargetDedicatedNodes());
}
```

### Resize Pool

```java
import com.azure.core.util.polling.SyncPoller;
import java.time.Duration;

BatchPoolResizeParameters resizeParams = new BatchPoolResizeParameters()
    .setTargetDedicatedNodes(4)
    .setTargetLowPriorityNodes(2)
    .setResizeTimeout(Duration.ofMinutes(15))
    .setNodeDeallocationOption(BatchNodeDeallocationOption.TASK_COMPLETION);

SyncPoller<BatchPool, BatchPool> poller = batchClient.beginResizePool("myPoolId", resizeParams);
poller.waitForCompletion();

BatchPool resizedPool = poller.getFinalResult();
System.out.println("Pool resized. New target: " + resizedPool.getTargetDedicatedNodes());
```

### Enable AutoScale

```java
String autoScaleFormula = """
    // Target 1 dedicated node per 5 pending tasks
    pendingTasks = $PendingTasks.GetSample(TimeInterval_Minute * 5);
    $TargetDedicatedNodes = min(10, max(1, pendingTasks / 5));
    $TargetLowPriorityNodes = 0;
    """;

BatchPoolEnableAutoScaleParameters autoScaleParams = new BatchPoolEnableAutoScaleParameters()
    .setAutoScaleEvaluationInterval(Duration.ofMinutes(5))
    .setAutoScaleFormula(autoScaleFormula);

batchClient.enablePoolAutoScale("myPoolId", autoScaleParams);
System.out.println("AutoScale enabled");
```

### Disable AutoScale

```java
batchClient.disablePoolAutoScale("myPoolId");
System.out.println("AutoScale disabled");
```

### Delete Pool

```java
SyncPoller<BatchPool, Void> deletePoller = batchClient.beginDeletePool("myPoolId");
deletePoller.waitForCompletion();
System.out.println("Pool deleted");
```

## Job Operations

### Create Job

```java
batchClient.createJob(
    new BatchJobCreateParameters("myJobId", new BatchPoolInfo().setPoolId("myPoolId"))
        .setDisplayName("My Batch Job")
        .setPriority(100)
        .setConstraints(new BatchJobConstraints()
            .setMaxWallClockTime(Duration.ofHours(24))
            .setMaxTaskRetryCount(3))
        .setOnAllTasksComplete(OnAllBatchTasksComplete.TERMINATE_JOB)
        .setOnTaskFailure(OnBatchTaskFailure.NO_ACTION),
    null);

System.out.println("Job created: myJobId");
```

### Create Job with Job Manager Task

```java
batchClient.createJob(
    new BatchJobCreateParameters("managedJobId", new BatchPoolInfo().setPoolId("myPoolId"))
        .setJobManagerTask(new BatchJobManagerTask("manager", "python3 manage_tasks.py")
            .setDisplayName("Job Manager")
            .setKillJobOnCompletion(true)
            .setRunExclusive(true)),
    null);
```

### Get Job

```java
BatchJob job = batchClient.getJob("myJobId", null, null);

System.out.println("=== Job Details ===");
System.out.println("Job ID: " + job.getId());
System.out.println("State: " + job.getState());
System.out.println("Priority: " + job.getPriority());
System.out.println("Pool: " + job.getPoolInfo().getPoolId());
System.out.println("Created: " + job.getCreationTime());
```

### List Jobs

```java
PagedIterable<BatchJob> jobs = batchClient.listJobs(new BatchJobsListOptions());

System.out.println("=== Active Jobs ===");
for (BatchJob j : jobs) {
    System.out.printf("Job: %s, State: %s, Pool: %s%n",
        j.getId(),
        j.getState(),
        j.getPoolInfo().getPoolId());
}
```

### Get Task Counts

```java
BatchTaskCountsResult counts = batchClient.getJobTaskCounts("myJobId");

System.out.println("=== Task Counts ===");
System.out.println("Active: " + counts.getTaskCounts().getActive());
System.out.println("Running: " + counts.getTaskCounts().getRunning());
System.out.println("Completed: " + counts.getTaskCounts().getCompleted());
System.out.println("Succeeded: " + counts.getTaskCounts().getSucceeded());
System.out.println("Failed: " + counts.getTaskCounts().getFailed());
```

### Update Job

```java
BatchJobUpdateParameters updateParams = new BatchJobUpdateParameters()
    .setPriority(200)
    .setConstraints(new BatchJobConstraints()
        .setMaxWallClockTime(Duration.ofHours(48)));

batchClient.updateJob("myJobId", updateParams);
System.out.println("Job updated");
```

### Terminate Job

```java
BatchJobTerminateParameters terminateParams = new BatchJobTerminateParameters()
    .setTerminationReason("Manual termination - job complete");
BatchJobTerminateOptions options = new BatchJobTerminateOptions().setParameters(terminateParams);

SyncPoller<BatchJob, BatchJob> poller = batchClient.beginTerminateJob("myJobId", options, null);
poller.waitForCompletion();
System.out.println("Job terminated");
```

### Delete Job

```java
SyncPoller<BatchJob, Void> deletePoller = batchClient.beginDeleteJob("myJobId");
deletePoller.waitForCompletion();
System.out.println("Job deleted");
```

## Task Operations

### Create Single Task

```java
BatchTaskCreateParameters task = new BatchTaskCreateParameters("task1", "echo 'Hello World'");
batchClient.createTask("myJobId", task);
System.out.println("Task created: task1");
```

### Create Task with Resource Files

```java
import java.util.Arrays;

BatchTaskCreateParameters task = new BatchTaskCreateParameters("processDataTask", 
    "python3 process.py input.csv output.csv")
    .setResourceFiles(Arrays.asList(
        new ResourceFile()
            .setHttpUrl("https://storage.blob.core.windows.net/container/process.py?sasToken")
            .setFilePath("process.py"),
        new ResourceFile()
            .setHttpUrl("https://storage.blob.core.windows.net/container/input.csv?sasToken")
            .setFilePath("input.csv")))
    .setOutputFiles(Arrays.asList(
        new OutputFile("output.csv")
            .setDestination(new OutputFileDestination()
                .setContainer(new OutputFileBlobContainerDestination(
                    "https://storage.blob.core.windows.net/results?sasToken")
                    .setPath("results/output.csv")))
            .setUploadOptions(new OutputFileUploadOptions()
                .setUploadCondition(OutputFileUploadCondition.TASK_SUCCESS))));

batchClient.createTask("myJobId", task);
```

### Create Task with Exit Conditions

```java
BatchTaskCreateParameters task = new BatchTaskCreateParameters("conditionalTask", "cmd /c exit 3")
    .setExitConditions(new ExitConditions()
        .setExitCodeRanges(Arrays.asList(
            new ExitCodeRangeMapping(0, 0,
                new ExitOptions().setJobAction(BatchJobActionKind.NONE)),
            new ExitCodeRangeMapping(1, 5,
                new ExitOptions().setJobAction(BatchJobActionKind.TERMINATE)),
            new ExitCodeRangeMapping(6, 10,
                new ExitOptions().setDependencyAction(DependencyActionKind.BLOCK))))
        .setDefault(new ExitOptions()
            .setJobAction(BatchJobActionKind.NONE)));

batchClient.createTask("myJobId", task);
```

### Create Task with User Identity

```java
BatchTaskCreateParameters task = new BatchTaskCreateParameters("adminTask", "sudo apt-get update")
    .setUserIdentity(new UserIdentity()
        .setAutoUser(new AutoUserSpecification()
            .setScope(AutoUserScope.TASK)
            .setElevationLevel(ElevationLevel.ADMIN)));

batchClient.createTask("myJobId", task);
```

### Create Task Collection (up to 100)

```java
List<BatchTaskCreateParameters> taskList = Arrays.asList(
    new BatchTaskCreateParameters("task1", "echo Task 1"),
    new BatchTaskCreateParameters("task2", "echo Task 2"),
    new BatchTaskCreateParameters("task3", "echo Task 3"),
    new BatchTaskCreateParameters("task4", "echo Task 4"),
    new BatchTaskCreateParameters("task5", "echo Task 5")
);

BatchTaskGroup taskGroup = new BatchTaskGroup(taskList);
BatchCreateTaskCollectionResult result = batchClient.createTaskCollection("myJobId", taskGroup);

System.out.printf("Created %d tasks%n", result.getValue().size());
```

### Create Many Tasks (no limit)

```java
import java.util.ArrayList;

List<BatchTaskCreateParameters> tasks = new ArrayList<>();
for (int i = 0; i < 1000; i++) {
    tasks.add(new BatchTaskCreateParameters("task" + i, 
        String.format("python3 process.py --partition %d", i)));
}

batchClient.createTasks("myJobId", tasks);
System.out.printf("Created %d tasks%n", tasks.size());
```

### Create Task with Dependencies

```java
// First, create prerequisite tasks
batchClient.createTask("myJobId", new BatchTaskCreateParameters("setup", "setup.sh"));
batchClient.createTask("myJobId", new BatchTaskCreateParameters("download", "download.sh"));

// Create dependent task
BatchTaskCreateParameters dependentTask = new BatchTaskCreateParameters("process", "process.sh")
    .setDependsOn(new BatchTaskDependencies()
        .setTaskIds(Arrays.asList("setup", "download")));

batchClient.createTask("myJobId", dependentTask);
```

### Get Task

```java
BatchTask task = batchClient.getTask("myJobId", "task1");

System.out.println("=== Task Details ===");
System.out.println("Task ID: " + task.getId());
System.out.println("State: " + task.getState());
System.out.println("Command: " + task.getCommandLine());

if (task.getExecutionInfo() != null) {
    System.out.println("Exit Code: " + task.getExecutionInfo().getExitCode());
    System.out.println("Start Time: " + task.getExecutionInfo().getStartTime());
    System.out.println("End Time: " + task.getExecutionInfo().getEndTime());
    
    if (task.getExecutionInfo().getFailureInfo() != null) {
        System.out.println("Failure: " + task.getExecutionInfo().getFailureInfo().getMessage());
    }
}
```

### List Tasks

```java
PagedIterable<BatchTask> tasks = batchClient.listTasks("myJobId");

System.out.println("=== Tasks ===");
for (BatchTask t : tasks) {
    System.out.printf("Task: %s, State: %s%n", t.getId(), t.getState());
}
```

### Get Task Output

```java
import com.azure.core.util.BinaryData;
import java.nio.charset.StandardCharsets;

// Get stdout
BinaryData stdout = batchClient.getTaskFile("myJobId", "task1", "stdout.txt");
System.out.println("=== stdout ===");
System.out.println(new String(stdout.toBytes(), StandardCharsets.UTF_8));

// Get stderr
BinaryData stderr = batchClient.getTaskFile("myJobId", "task1", "stderr.txt");
System.out.println("=== stderr ===");
System.out.println(new String(stderr.toBytes(), StandardCharsets.UTF_8));
```

### List Task Files

```java
PagedIterable<BatchNodeFile> files = batchClient.listTaskFiles("myJobId", "task1");

System.out.println("=== Task Files ===");
for (BatchNodeFile file : files) {
    System.out.printf("File: %s, Size: %d bytes%n",
        file.getName(),
        file.getProperties().getContentLength());
}
```

### Terminate Task

```java
batchClient.terminateTask("myJobId", "task1", null, null);
System.out.println("Task terminated");
```

### Delete Task

```java
batchClient.deleteTask("myJobId", "task1");
System.out.println("Task deleted");
```

## Node Operations

### List Nodes

```java
PagedIterable<BatchNode> nodes = batchClient.listNodes("myPoolId", new BatchNodesListOptions());

System.out.println("=== Compute Nodes ===");
for (BatchNode node : nodes) {
    System.out.printf("Node: %s, State: %s, IP: %s%n",
        node.getId(),
        node.getState(),
        node.getIpAddress());
}
```

### Get Node

```java
BatchNode node = batchClient.getNode("myPoolId", "nodeId");

System.out.println("=== Node Details ===");
System.out.println("Node ID: " + node.getId());
System.out.println("State: " + node.getState());
System.out.println("IP Address: " + node.getIpAddress());
System.out.println("VM Size: " + node.getVmSize());
System.out.println("Total Tasks Run: " + node.getTotalTasksRun());
System.out.println("Running Tasks: " + node.getRunningTasksCount());
```

### Reboot Node

```java
BatchNodeRebootParameters rebootParams = new BatchNodeRebootParameters()
    .setNodeRebootOption(BatchNodeRebootOption.TASK_COMPLETION);

SyncPoller<BatchNode, BatchNode> rebootPoller = 
    batchClient.beginRebootNode("myPoolId", "nodeId", rebootParams);
rebootPoller.waitForCompletion();
System.out.println("Node rebooted");
```

### Get Remote Login Settings

```java
BatchNodeRemoteLoginSettings settings = batchClient.getNodeRemoteLoginSettings("myPoolId", "nodeId");

System.out.println("=== Remote Login Settings ===");
System.out.println("IP Address: " + settings.getRemoteLoginIpAddress());
System.out.println("Port: " + settings.getRemoteLoginPort());

// SSH command
System.out.printf("SSH: ssh -p %d user@%s%n",
    settings.getRemoteLoginPort(),
    settings.getRemoteLoginIpAddress());
```

### Remove Node from Pool

```java
BatchNodeRemoveParameters removeParams = new BatchNodeRemoveParameters(
    Arrays.asList("nodeId1", "nodeId2"))
    .setNodeDeallocationOption(BatchNodeDeallocationOption.TASK_COMPLETION)
    .setResizeTimeout(Duration.ofMinutes(15));

batchClient.removeNodes("myPoolId", removeParams);
System.out.println("Nodes removal initiated");
```

## Job Schedule Operations

### Create Job Schedule

```java
import java.time.OffsetDateTime;

batchClient.createJobSchedule(new BatchJobScheduleCreateParameters("dailySchedule",
    new BatchJobScheduleConfiguration()
        .setRecurrenceInterval(Duration.ofHours(24))
        .setDoNotRunUntil(OffsetDateTime.now().plusHours(1))
        .setDoNotRunAfter(OffsetDateTime.now().plusDays(30)),
    new BatchJobSpecification(new BatchPoolInfo().setPoolId("myPoolId"))
        .setDisplayName("Daily Processing Job")
        .setPriority(100)
        .setConstraints(new BatchJobConstraints()
            .setMaxTaskRetryCount(3))),
    null);

System.out.println("Job schedule created: dailySchedule");
```

### Get Job Schedule

```java
BatchJobSchedule schedule = batchClient.getJobSchedule("dailySchedule");

System.out.println("=== Job Schedule Details ===");
System.out.println("Schedule ID: " + schedule.getId());
System.out.println("State: " + schedule.getState());
System.out.println("Next Run: " + schedule.getExecutionInfo().getNextRunTime());
System.out.println("Recent Jobs: " + schedule.getExecutionInfo().getRecentJob());
```

### List Job Schedules

```java
PagedIterable<BatchJobSchedule> schedules = batchClient.listJobSchedules();

System.out.println("=== Job Schedules ===");
for (BatchJobSchedule s : schedules) {
    System.out.printf("Schedule: %s, State: %s%n", s.getId(), s.getState());
}
```

### Disable Job Schedule

```java
batchClient.disableJobSchedule("dailySchedule");
System.out.println("Job schedule disabled");
```

### Enable Job Schedule

```java
batchClient.enableJobSchedule("dailySchedule");
System.out.println("Job schedule enabled");
```

### Terminate Job Schedule

```java
batchClient.terminateJobSchedule("dailySchedule");
System.out.println("Job schedule terminated");
```

### Delete Job Schedule

```java
batchClient.deleteJobSchedule("dailySchedule");
System.out.println("Job schedule deleted");
```

## Error Handling

```java
import com.azure.compute.batch.models.BatchErrorException;
import com.azure.compute.batch.models.BatchError;

try {
    BatchPool pool = batchClient.getPool("nonexistent-pool");
} catch (BatchErrorException e) {
    BatchError error = e.getValue();
    
    System.err.println("=== Batch Error ===");
    System.err.println("Error code: " + error.getCode());
    System.err.println("Message: " + error.getMessage().getValue());
    
    // Handle specific errors
    switch (error.getCode()) {
        case "PoolNotFound":
            System.err.println("The specified pool does not exist.");
            break;
        case "JobNotFound":
            System.err.println("The specified job does not exist.");
            break;
        case "TaskNotFound":
            System.err.println("The specified task does not exist.");
            break;
        case "PoolQuotaReached":
            System.err.println("Pool quota exceeded. Delete unused pools or request quota increase.");
            break;
        case "ActiveJobAndScheduleQuotaReached":
            System.err.println("Job quota exceeded.");
            break;
        default:
            System.err.println("Unexpected error: " + error.getCode());
    }
    
    // Show additional details if available
    if (error.getValues() != null) {
        for (var detail : error.getValues()) {
            System.err.printf("  %s: %s%n", detail.getKey(), detail.getValue());
        }
    }
}
```

## Complete Application Example

```java
import com.azure.compute.batch.BatchClient;
import com.azure.compute.batch.BatchClientBuilder;
import com.azure.compute.batch.models.*;
import com.azure.core.http.rest.PagedIterable;
import com.azure.core.util.BinaryData;
import com.azure.identity.DefaultAzureCredentialBuilder;

import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.*;

public class BatchJobRunner {
    
    private final BatchClient client;
    private final String poolId;
    
    public BatchJobRunner(String poolId) {
        this.client = new BatchClientBuilder()
            .endpoint(System.getenv("AZURE_BATCH_ENDPOINT"))
            .credential(new DefaultAzureCredentialBuilder().build())
            .buildClient();
        this.poolId = poolId;
    }
    
    public void ensurePoolExists() {
        try {
            BatchPool pool = client.getPool(poolId);
            System.out.println("Pool exists: " + pool.getId());
        } catch (BatchErrorException e) {
            if ("PoolNotFound".equals(e.getValue().getCode())) {
                createPool();
            } else {
                throw e;
            }
        }
    }
    
    private void createPool() {
        System.out.println("Creating pool: " + poolId);
        
        client.createPool(new BatchPoolCreateParameters(poolId, "STANDARD_D2s_v3")
            .setVirtualMachineConfiguration(
                new VirtualMachineConfiguration(
                    new BatchVmImageReference()
                        .setPublisher("Canonical")
                        .setOffer("0001-com-ubuntu-server-jammy")
                        .setSku("22_04-lts")
                        .setVersion("latest"),
                    "batch.node.ubuntu 22.04"))
            .setTargetDedicatedNodes(2)
            .setTaskSlotsPerNode(4), null);
        
        // Wait for pool to be ready
        waitForPoolReady();
    }
    
    private void waitForPoolReady() {
        System.out.println("Waiting for pool to be ready...");
        while (true) {
            BatchPool pool = client.getPool(poolId);
            if (pool.getAllocationState() == AllocationState.STEADY 
                && pool.getCurrentDedicatedNodes() > 0) {
                System.out.println("Pool is ready with " + pool.getCurrentDedicatedNodes() + " nodes");
                break;
            }
            try {
                Thread.sleep(10000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new RuntimeException(e);
            }
        }
    }
    
    public String runJob(String jobId, List<String> commands) {
        // Create job
        client.createJob(
            new BatchJobCreateParameters(jobId, new BatchPoolInfo().setPoolId(poolId))
                .setOnAllTasksComplete(OnAllBatchTasksComplete.TERMINATE_JOB),
            null);
        
        System.out.println("Job created: " + jobId);
        
        // Create tasks
        List<BatchTaskCreateParameters> tasks = new ArrayList<>();
        for (int i = 0; i < commands.size(); i++) {
            tasks.add(new BatchTaskCreateParameters("task" + i, commands.get(i)));
        }
        
        client.createTasks(jobId, tasks);
        System.out.println("Created " + tasks.size() + " tasks");
        
        // Wait for completion
        waitForJobComplete(jobId);
        
        return jobId;
    }
    
    private void waitForJobComplete(String jobId) {
        System.out.println("Waiting for job to complete...");
        while (true) {
            BatchJob job = client.getJob(jobId, null, null);
            
            if (job.getState() == BatchJobState.COMPLETED) {
                System.out.println("Job completed");
                break;
            } else if (job.getState() == BatchJobState.DISABLED 
                    || job.getState() == BatchJobState.TERMINATING) {
                throw new RuntimeException("Job failed or was terminated");
            }
            
            // Show progress
            BatchTaskCountsResult counts = client.getJobTaskCounts(jobId);
            System.out.printf("Progress: %d/%d tasks completed%n",
                counts.getTaskCounts().getCompleted(),
                counts.getTaskCounts().getActive() + counts.getTaskCounts().getRunning() 
                    + counts.getTaskCounts().getCompleted());
            
            try {
                Thread.sleep(5000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new RuntimeException(e);
            }
        }
    }
    
    public Map<String, String> getTaskOutputs(String jobId) {
        Map<String, String> outputs = new HashMap<>();
        
        PagedIterable<BatchTask> tasks = client.listTasks(jobId);
        for (BatchTask task : tasks) {
            try {
                BinaryData stdout = client.getTaskFile(jobId, task.getId(), "stdout.txt");
                outputs.put(task.getId(), new String(stdout.toBytes(), StandardCharsets.UTF_8));
            } catch (Exception e) {
                outputs.put(task.getId(), "Error: " + e.getMessage());
            }
        }
        
        return outputs;
    }
    
    public void cleanup(String jobId) {
        try {
            client.beginDeleteJob(jobId).waitForCompletion();
            System.out.println("Job deleted: " + jobId);
        } catch (Exception e) {
            System.err.println("Failed to delete job: " + e.getMessage());
        }
    }
    
    public static void main(String[] args) {
        BatchJobRunner runner = new BatchJobRunner("my-batch-pool");
        
        try {
            // Ensure pool exists
            runner.ensurePoolExists();
            
            // Run job with tasks
            List<String> commands = Arrays.asList(
                "echo 'Processing partition 1' && sleep 5",
                "echo 'Processing partition 2' && sleep 5",
                "echo 'Processing partition 3' && sleep 5",
                "echo 'Processing partition 4' && sleep 5"
            );
            
            String jobId = "job-" + System.currentTimeMillis();
            runner.runJob(jobId, commands);
            
            // Get outputs
            Map<String, String> outputs = runner.getTaskOutputs(jobId);
            
            System.out.println("\n=== Task Outputs ===");
            outputs.forEach((taskId, output) -> {
                System.out.printf("%s: %s%n", taskId, output.trim());
            });
            
            // Cleanup
            runner.cleanup(jobId);
            
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
```

## Environment Variables

```bash
AZURE_BATCH_ENDPOINT=https://<account>.<region>.batch.azure.com
AZURE_BATCH_ACCOUNT=<account-name>
AZURE_BATCH_ACCESS_KEY=<account-key>

# For DefaultAzureCredential
AZURE_CLIENT_ID=<service-principal-client-id>
AZURE_CLIENT_SECRET=<service-principal-secret>
AZURE_TENANT_ID=<tenant-id>
```

## Best Practices

1. **Use Entra ID** — Preferred over shared key for authentication
2. **Use management SDK for pools** — `azure-resourcemanager-batch` supports managed identities
3. **Batch task creation** — Use `createTaskCollection` or `createTasks` for multiple tasks
4. **Handle LRO properly** — Pool resize, delete operations are long-running
5. **Monitor task counts** — Use `getJobTaskCounts` to track progress
6. **Set constraints** — Configure `maxWallClockTime` and `maxTaskRetryCount`
7. **Use low-priority nodes** — Cost savings for fault-tolerant workloads
8. **Enable autoscale** — Dynamically adjust pool size based on workload
