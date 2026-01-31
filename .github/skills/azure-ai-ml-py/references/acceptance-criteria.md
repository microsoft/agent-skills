# Azure Machine Learning SDK v2 Acceptance Criteria

**SDK**: `azure-ai-ml`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: MLClient Creation
```python
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

ml_client = MLClient(
    credential=DefaultAzureCredential(),
    subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"],
    resource_group_name=os.environ["AZURE_RESOURCE_GROUP"],
    workspace_name=os.environ["AZURE_ML_WORKSPACE_NAME"]
)
```

#### ✅ CORRECT: MLClient from Config
```python
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

ml_client = MLClient.from_config(
    credential=DefaultAzureCredential()
)
```

#### ✅ CORRECT: Entity Imports
```python
from azure.ai.ml.entities import (
    Workspace,
    Data,
    Model,
    AmlCompute,
    Environment,
)
from azure.ai.ml.constants import AssetTypes
```

#### ✅ CORRECT: Job Imports
```python
from azure.ai.ml import command, Input, Output
from azure.ai.ml.entities import Pipeline
from azure.ai.ml import dsl
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using wrong module
```python
# WRONG - MLClient is in azure.ai.ml, not azure.ai.ml.client
from azure.ai.ml.client import MLClient

# WRONG - AssetTypes should be imported separately
from azure.ai.ml import AssetTypes
```

#### ❌ INCORRECT: Hardcoded credentials
```python
# WRONG - Never hardcode credentials
ml_client = MLClient(
    credential="hardcoded-key-or-token",
    subscription_id="sub-id",
    ...
)
```

#### ❌ INCORRECT: Missing context manager
```python
# WRONG - Should use context manager or close explicitly
ml_client = MLClient(credential=cred, ...)
workspace = ml_client.workspaces.get("my-ws")
# Missing: ml_client.close() or using 'with' statement
```

---

## 2. Workspace Management Patterns

### 2.1 ✅ CORRECT: Create Workspace
```python
from azure.ai.ml.entities import Workspace

ws = Workspace(
    name="my-workspace",
    location="eastus",
    display_name="My Workspace",
    description="ML workspace for experiments",
    tags={"purpose": "demo"}
)

created_ws = ml_client.workspaces.begin_create(ws).result()
```

### 2.2 ✅ CORRECT: List Workspaces
```python
workspaces = ml_client.workspaces.list()
for ws in workspaces:
    print(f"{ws.name}: {ws.location}")
```

### 2.3 ✅ CORRECT: Get Workspace
```python
workspace = ml_client.workspaces.get("my-workspace")
print(workspace.name)
```

### 2.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing begin_create().result()
```python
# WRONG - begin_create() returns LROPoller, need to call .result()
ml_client.workspaces.begin_create(ws)  # Missing .result()
```

#### ❌ INCORRECT: Wrong method names
```python
# WRONG - create_or_update is not the method for workspaces
ml_client.workspaces.create_or_update(ws)
```

**Correct approach:** Use `begin_create(ws).result()` instead of `create_or_update()`. Workspace creation is an async operation that requires the LROPoller chain.

---

## 3. Data Asset Registration Patterns

### 3.1 ✅ CORRECT: Register File Data
```python
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes

my_data = Data(
    name="my-dataset",
    version="1",
    path="azureml://datastores/workspaceblobstore/paths/data/train.csv",
    type=AssetTypes.URI_FILE,
    description="Training data"
)

ml_client.data.create_or_update(my_data)
```

### 3.2 ✅ CORRECT: Register Folder Data
```python
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes

my_data = Data(
    name="my-folder-dataset",
    version="1",
    path="azureml://datastores/workspaceblobstore/paths/data/",
    type=AssetTypes.URI_FOLDER
)

ml_client.data.create_or_update(my_data)
```

### 3.3 ✅ CORRECT: List Data Assets
```python
data_assets = ml_client.data.list(name="my-dataset")
for data in data_assets:
    print(f"{data.name} v{data.version}")
```

### 3.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing AssetTypes
```python
# WRONG - type should use AssetTypes enum
my_data = Data(
    name="dataset",
    type="uri_file",  # Should be AssetTypes.URI_FILE
    path="..."
)
```

#### ❌ INCORRECT: Using local paths instead of azureml:// URIs
```python
# WRONG - should use azureml:// URI format
my_data = Data(
    name="dataset",
    path="./local/data/train.csv",  # Wrong
    type=AssetTypes.URI_FILE
)
```

---

## 4. Model Registry Patterns

### 4.1 ✅ CORRECT: Register Model
```python
from azure.ai.ml.entities import Model
from azure.ai.ml.constants import AssetTypes

model = Model(
    name="my-model",
    version="1",
    path="./model/",
    type=AssetTypes.CUSTOM_MODEL,
    description="My trained model"
)

ml_client.models.create_or_update(model)
```

### 4.2 ✅ CORRECT: List Models
```python
models = ml_client.models.list(name="my-model")
for model in models:
    print(f"{model.name} v{model.version}")
```

### 4.3 ✅ CORRECT: Get Model
```python
model = ml_client.models.get(name="my-model", version="1")
print(model.path)
```

### 4.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing type
```python
# WRONG - type is required
model = Model(
    name="my-model",
    path="./model/",
    # Missing: type=AssetTypes.CUSTOM_MODEL
)
```

---

## 5. Compute Cluster Patterns

### 5.1 ✅ CORRECT: Create Compute Cluster
```python
from azure.ai.ml.entities import AmlCompute

cluster = AmlCompute(
    name="cpu-cluster",
    type="amlcompute",
    size="Standard_DS3_v2",
    min_instances=0,
    max_instances=4,
    idle_time_before_scale_down=120
)

ml_client.compute.begin_create_or_update(cluster).result()
```

### 5.2 ✅ CORRECT: List Compute
```python
compute_resources = ml_client.compute.list()
for compute in compute_resources:
    print(f"{compute.name}: {compute.type}")
```

### 5.3 ✅ CORRECT: Get Compute
```python
compute = ml_client.compute.get("cpu-cluster")
print(compute.provisioning_state)
```

### 5.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing begin/result chain
```python
# WRONG - compute creation is async, need .begin_create_or_update().result()
ml_client.compute.create_or_update(cluster)
```

**Correct approach:** Use `.begin_create_or_update(cluster).result()` instead. Long-running operations in Azure ML SDK return an LROPoller that must be awaited with `.result()`.

#### ❌ INCORRECT: Wrong cluster type
```python
# WRONG - type must be "amlcompute" string
cluster = AmlCompute(
    name="cpu-cluster",
    type=AmlCompute,  # Should be "amlcompute" string
    size="Standard_DS3_v2"
)
```

---

## 6. Job Execution Patterns

### 6.1 ✅ CORRECT: Command Job
```python
from azure.ai.ml import command, Input

job = command(
    code="./src",
    command="python train.py --data ${{inputs.data}} --lr ${{inputs.learning_rate}}",
    inputs={
        "data": Input(type="uri_folder", path="azureml:my-dataset:1"),
        "learning_rate": 0.01
    },
    environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
    compute="cpu-cluster",
    display_name="training-job"
)

returned_job = ml_client.jobs.create_or_update(job)
```

### 6.2 ✅ CORRECT: Monitor Job
```python
ml_client.jobs.stream(returned_job.name)
```

### 6.3 ✅ CORRECT: Get Job Details
```python
job = ml_client.jobs.get(returned_job.name)
print(f"Status: {job.status}")
print(f"Studio URL: {job.studio_url}")
```

### 6.4 ✅ CORRECT: List Jobs
```python
jobs = ml_client.jobs.list()
for job in jobs:
    print(f"{job.name}: {job.status}")
```

### 6.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong Input syntax
```python
# WRONG - Input type should be string
inputs={
    "data": Input(type=uri_folder, path="azureml:dataset:1"),  # Unquoted
}
```

**Correct approach:** Use string literals for the `type` parameter: `Input(type="uri_folder", path="azureml:my-dataset:1")`. The type must be a quoted string, not an unquoted variable name.

#### ❌ INCORRECT: Using wrong parameter placeholders
```python
# WRONG - should use ${{inputs.param}} format
command="python train.py --data {data} --lr {learning_rate}"
```

**Correct approach:** Use the Azure ML DSL placeholder syntax `${{inputs.param}}` instead of simple brace placeholders. This ensures the values are properly injected at job submission time.

---

## 7. Pipeline Patterns

### 7.1 ✅ CORRECT: Define Pipeline with DSL
```python
from azure.ai.ml import dsl, Input
from azure.ai.ml.entities import PipelineJob

@dsl.pipeline(
    compute="cpu-cluster",
    description="Training pipeline"
)
def training_pipeline(data_input):
    prep_step = prep_component(data=data_input)
    train_step = train_component(
        data=prep_step.outputs.output_data,
        learning_rate=0.01
    )
    return {"model": train_step.outputs.model}

pipeline = training_pipeline(
    data_input=Input(type="uri_folder", path="azureml:my-dataset:1")
)

pipeline_job = ml_client.jobs.create_or_update(pipeline)
```

### 7.2 ✅ CORRECT: Pipeline with Registered Components
```python
# Use get_component to reference registered components
prep_component = ml_client.components.get(name="prep", version="1")
train_component = ml_client.components.get(name="train", version="1")

@dsl.pipeline(compute="cpu-cluster")
def my_pipeline(data_input):
    step1 = prep_component(data=data_input)
    step2 = train_component(training_data=step1.outputs.output_data)
    return {"model": step2.outputs.model}
```

### 7.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not using @dsl.pipeline decorator
```python
# WRONG - must use @dsl.pipeline decorator
def training_pipeline(data_input):
    prep_step = prep_component(data=data_input)
    ...
```

#### ❌ INCORRECT: Returning outputs incorrectly
```python
# WRONG - must return dict with output mappings
@dsl.pipeline
def my_pipeline(data_input):
    step1 = component(data=data_input)
    return step1.outputs  # Should be {"name": step1.outputs.output_field}
```

---

## 8. Environment Patterns

### 8.1 ✅ CORRECT: Create Custom Environment
```python
from azure.ai.ml.entities import Environment

env = Environment(
    name="my-env",
    version="1",
    image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04",
    conda_file="./environment.yml"
)

ml_client.environments.create_or_update(env)
```

### 8.2 ✅ CORRECT: Use Curated Environment
```python
# Reference curated environment by name and version
job = command(
    ...
    environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
)
```

### 8.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing conda_file path
```python
# WRONG - conda_file should be path to environment.yml
env = Environment(
    name="my-env",
    image="mcr.microsoft.com/azureml/...",
    # Missing: conda_file="./environment.yml"
)
```

---

## 9. Datastore Patterns

### 9.1 ✅ CORRECT: List Datastores
```python
datastores = ml_client.datastores.list()
for ds in datastores:
    print(f"{ds.name}: {ds.type}")
```

### 9.2 ✅ CORRECT: Get Default Datastore
```python
default_datastore = ml_client.datastores.get_default()
print(f"Default: {default_datastore.name}")
```

### 9.3 ✅ CORRECT: Get Specific Datastore
```python
datastore = ml_client.datastores.get("workspaceblobstore")
```

---

## 10. Async Patterns

### 10.1 ✅ CORRECT: Long-Running Operations Pattern
```python
# Methods that return LROPoller should use .result() to wait
poller = ml_client.compute.begin_create_or_update(cluster)
cluster = poller.result()  # Wait for operation to complete

poller = ml_client.workspaces.begin_create(workspace)
workspace = poller.result()  # Wait for operation to complete
```

### 10.2 ✅ CORRECT: Stream Job Results
```python
# Stream output while job is running
ml_client.jobs.stream(job_name)
```

---

## 11. Error Handling Patterns

### 11.1 ✅ CORRECT: Handle Errors
```python
from azure.core.exceptions import AzureError

try:
    ml_client.workspaces.get("non-existent")
except AzureError as e:
    print(f"Error: {e}")
```

### 11.2 ✅ CORRECT: Check Job Status
```python
job = ml_client.jobs.get(job_name)
if job.status == "Failed":
    print(f"Job failed: {job.properties}")
elif job.status == "Completed":
    print("Job succeeded")
```

---

## 12. Environment Variables

### Required Variables
```bash
AZURE_SUBSCRIPTION_ID=<your-subscription-id>
AZURE_RESOURCE_GROUP=<your-resource-group>
AZURE_ML_WORKSPACE_NAME=<your-workspace-name>
```

### Optional Variables
```bash
AZURE_ML_COMPUTE_NAME=cpu-cluster
AZURE_ML_ENVIRONMENT_NAME=my-env
```

---

## 13. Common Error Patterns

| Error | Cause | Fix |
|-------|-------|-----|
| `AttributeError: 'AmlCompute' has no attribute 'name'` | Wrong property access | Use `cluster.name`, not `cluster.compute_name` |
| `Type must be string "amlcompute"` | Wrong type format | Use `type="amlcompute"` string, not enum |
| `Missing .result() on LROPoller` | Not waiting for async operation | Add `.result()` to `begin_*` methods |
| `azureml:// URI not found` | Wrong data asset reference | Use correct format: `azureml://datastores/name/paths/...` or `azureml:asset-name:version` |
| `Input type error` | Incorrect Input type syntax | Use `Input(type="uri_folder", path="...")` with string types |
| `Placeholder syntax error` | Wrong command placeholder format | Use `${{inputs.param}}` format, not `{param}` |

---

## 14. Test Scenarios Checklist

### Basic Operations
- [ ] MLClient creation with environment variables
- [ ] MLClient creation from config file
- [ ] Workspace creation and retrieval
- [ ] Data asset registration (file and folder)
- [ ] Model registration and retrieval

### Compute & Jobs
- [ ] Compute cluster creation
- [ ] Job creation and monitoring
- [ ] Job status checking
- [ ] List jobs

### Pipelines & Components
- [ ] Pipeline definition with @dsl.pipeline
- [ ] Pipeline with multiple steps
- [ ] Component reference and usage
- [ ] Pipeline job submission

### Assets & Environments
- [ ] Environment creation
- [ ] Datastore listing
- [ ] Asset versioning

### Error Handling
- [ ] Handle AzureError exceptions
- [ ] Check job failure status
- [ ] Verify workspace existence

---

## 15. Quick Reference: MLClient Operations

| Property | Operations | Async |
|----------|------------|-------|
| `workspaces` | get, list, begin_create, begin_delete | `.result()` required |
| `jobs` | create_or_update, get, list, stream, cancel | stream is sync |
| `models` | create_or_update, get, list, download, archive | No |
| `data` | create_or_update, get, list | No |
| `compute` | begin_create_or_update, get, list, begin_delete | `.result()` required |
| `environments` | create_or_update, get, list | No |
| `datastores` | get, list, get_default | No |
| `components` | create_or_update, get, list | No |
