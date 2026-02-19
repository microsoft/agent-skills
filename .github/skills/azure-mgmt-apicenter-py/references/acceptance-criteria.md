# Azure API Center Management SDK Acceptance Criteria

**SDK**: `azure-mgmt-apicenter`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Package**: `azure.mgmt.apicenter`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: ApiCenterMgmtClient
```python
from azure.mgmt.apicenter import ApiCenterMgmtClient
from azure.identity import DefaultAzureCredential
```

#### ✅ CORRECT: Async Credential
```python
from azure.mgmt.apicenter import ApiCenterMgmtClient
from azure.identity.aio import DefaultAzureCredential  # Async credential
```

### 1.2 Model Imports

#### ✅ CORRECT: Service Model
```python
from azure.mgmt.apicenter.models import Service
```

#### ✅ CORRECT: API Models
```python
from azure.mgmt.apicenter.models import (
    Api,
    ApiKind,
    LifecycleStage,
    ApiVersion,
    ApiDefinition,
    ApiSpecImportRequest,
    ApiSpecImportSourceFormat,
)
```

#### ✅ CORRECT: Environment and Deployment Models
```python
from azure.mgmt.apicenter.models import (
    Environment,
    EnvironmentKind,
    Deployment,
    DeploymentState,
)
```

#### ✅ CORRECT: Metadata Models
```python
from azure.mgmt.apicenter.models import MetadataSchema
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Importing from wrong module
```python
# WRONG - Service is not in azure.mgmt.apicenter directly
from azure.mgmt.apicenter import Service
```

**Correct approach:** Import from the `models` submodule instead: `from azure.mgmt.apicenter.models import Service`

#### ❌ INCORRECT: Using deprecated paths
```python
# WRONG - Wrong import path
from azure.mgmt.apicenter.services import Service
```

**Correct approach:** Use `models` module: `from azure.mgmt.apicenter.models import Service`

#### ❌ INCORRECT: Mixing subscription and resource group operations
```python
# WRONG - list_by_subscription doesn't exist
apis = client.apis.list_by_subscription()
```

**Correct approach:** All API operations are scoped to resource group, service, and workspace. Use the `list()` method with all three parameters: `client.apis.list(resource_group_name="my-rg", service_name="my-api-center", workspace_name="default")`

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Basic Client Creation
```python
from azure.mgmt.apicenter import ApiCenterMgmtClient
from azure.identity import DefaultAzureCredential
import os

client = ApiCenterMgmtClient(
    credential=DefaultAzureCredential(),
    subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"]
)
```

### 2.2 ✅ CORRECT: With Context Manager
```python
from azure.mgmt.apicenter import ApiCenterMgmtClient
from azure.identity import DefaultAzureCredential
import os

with ApiCenterMgmtClient(
    credential=DefaultAzureCredential(),
    subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"]
) as client:
    # Use client here
    pass
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing subscription_id
```python
# WRONG - subscription_id is required
client = ApiCenterMgmtClient(credential=credential)
```

**Correct approach:** Always pass `subscription_id` as a parameter when creating the client: `client = ApiCenterMgmtClient(credential=credential, subscription_id=subscription_id)`

#### ❌ INCORRECT: Not using environment variable
```python
# WRONG - hardcoded credentials
client = ApiCenterMgmtClient(
    credential=credential,
    subscription_id="12345678-1234-1234-1234-123456789012"
)
```

**Correct approach:** Always read sensitive values from environment variables instead of hardcoding them. Use `os.environ["AZURE_SUBSCRIPTION_ID"]` to retrieve the subscription ID at runtime.

---

## 3. API Center Service Management

### 3.1 ✅ CORRECT: Create API Center Service
```python
from azure.mgmt.apicenter.models import Service

api_center = client.services.create_or_update(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    resource=Service(
        location="eastus",
        tags={"environment": "production"}
    )
)
```

### 3.2 ✅ CORRECT: List API Centers
```python
api_centers = client.services.list_by_subscription()

for api_center in api_centers:
    print(f"{api_center.name} - {api_center.location}")
```

### 3.3 ✅ CORRECT: List API Centers in Resource Group
```python
api_centers = client.services.list_by_resource_group(
    resource_group_name="my-resource-group"
)

for api_center in api_centers:
    print(f"{api_center.name}")
```

### 3.4 ✅ CORRECT: Get Single API Center
```python
api_center = client.services.get(
    resource_group_name="my-resource-group",
    service_name="my-api-center"
)

print(f"API Center: {api_center.name}")
```

### 3.5 ✅ CORRECT: Update API Center
```python
api_center = client.services.create_or_update(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    resource=Service(
        location="eastus",
        tags={"environment": "staging", "version": "v2"}
    )
)
```

### 3.6 ✅ CORRECT: Delete API Center
```python
client.services.delete(
    resource_group_name="my-resource-group",
    service_name="my-api-center"
)
```

### 3.7 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing location in Service creation
```python
# WRONG - location is required
api_center = client.services.create_or_update(
    resource_group_name="my-rg",
    service_name="my-api-center",
    resource=Service()  # Missing location
)
```

**Correct approach:** Always specify a location (e.g., "eastus") when creating a Service resource. Location is a required field.

---

## 4. API Registration and Management

### 4.1 ✅ CORRECT: Register an API
```python
from azure.mgmt.apicenter.models import Api, ApiKind, LifecycleStage

api = client.apis.create_or_update(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    api_name="my-api",
    resource=Api(
        title="My API",
        description="A sample API",
        kind=ApiKind.REST,
        lifecycle_stage=LifecycleStage.PRODUCTION,
        terms_of_service={"url": "https://example.com/terms"},
        contacts=[{"name": "API Team", "email": "api-team@example.com"}]
    )
)
```

### 4.2 ✅ CORRECT: List APIs
```python
apis = client.apis.list(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default"
)

for api in apis:
    print(f"{api.name}: {api.title} ({api.kind})")
```

### 4.3 ✅ CORRECT: Get Single API
```python
api = client.apis.get(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    api_name="my-api"
)

print(f"API: {api.title}")
print(f"Kind: {api.kind}")
print(f"Lifecycle: {api.lifecycle_stage}")
```

### 4.4 ✅ CORRECT: Update API
```python
api = client.apis.create_or_update(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    api_name="my-api",
    resource=Api(
        title="My API Updated",
        description="Updated description",
        kind=ApiKind.REST,
        lifecycle_stage=LifecycleStage.DEPRECATED
    )
)
```

### 4.5 ✅ CORRECT: Delete API
```python
client.apis.delete(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    api_name="my-api"
)
```

### 4.6 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing workspace_name
```python
# WRONG - workspace_name is required
api = client.apis.create_or_update(
    resource_group_name="my-rg",
    service_name="my-api-center",
    api_name="my-api",
    resource=Api(title="My API", kind=ApiKind.REST)
)
```

**Correct approach:** All API operations require `workspace_name` parameter. The default workspace is typically named "default".

#### ❌ INCORRECT: Using wrong ApiKind enum
```python
# WRONG - ApiKind.SOAP might not exist, use REST, GraphQL, GRPC, WEBHOOK
api = client.apis.create_or_update(
    ...,
    resource=Api(kind="SOAP")  # Wrong
)
```

**Correct approach:** Use only valid `ApiKind` enum values: `REST`, `GraphQL`, `GRPC`, or `WEBHOOK`. Avoid string literals; use the enum type.

---

## 5. API Version Management

### 5.1 ✅ CORRECT: Create API Version
```python
from azure.mgmt.apicenter.models import ApiVersion, LifecycleStage

version = client.api_versions.create_or_update(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    api_name="my-api",
    version_name="v1",
    resource=ApiVersion(
        title="Version 1.0",
        lifecycle_stage=LifecycleStage.PRODUCTION
    )
)
```

### 5.2 ✅ CORRECT: List API Versions
```python
versions = client.api_versions.list(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    api_name="my-api"
)

for version in versions:
    print(f"{version.title} - {version.lifecycle_stage}")
```

### 5.3 ✅ CORRECT: Get API Version
```python
version = client.api_versions.get(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    api_name="my-api",
    version_name="v1"
)
```

### 5.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing version_name
```python
# WRONG
version = client.api_versions.create_or_update(
    resource_group_name="my-rg",
    service_name="my-api-center",
    workspace_name="default",
    api_name="my-api",
    resource=ApiVersion(title="v1")
)
```

**Correct approach:** `version_name` is a required parameter passed separately, not inside the resource body. Pass it as: `version_name="v1"` alongside the resource.

---

## 6. API Definition Management

### 6.1 ✅ CORRECT: Create API Definition
```python
from azure.mgmt.apicenter.models import ApiDefinition

definition = client.api_definitions.create_or_update(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    api_name="my-api",
    version_name="v1",
    definition_name="openapi",
    resource=ApiDefinition(
        title="OpenAPI Definition",
        description="OpenAPI 3.0 specification"
    )
)
```

### 6.2 ✅ CORRECT: List API Definitions
```python
definitions = client.api_definitions.list(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    api_name="my-api",
    version_name="v1"
)

for definition in definitions:
    print(f"{definition.title}")
```

### 6.3 ✅ CORRECT: Import API Specification (Inline)
```python
from azure.mgmt.apicenter.models import ApiSpecImportRequest, ApiSpecImportSourceFormat

client.api_definitions.import_specification(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    api_name="my-api",
    version_name="v1",
    definition_name="openapi",
    body=ApiSpecImportRequest(
        format=ApiSpecImportSourceFormat.INLINE,
        value='{"openapi": "3.0.0", "info": {"title": "My API", "version": "1.0"}, "paths": {}}'
    )
)
```

### 6.4 ✅ CORRECT: Import API Specification (URL)
```python
client.api_definitions.import_specification(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    api_name="my-api",
    version_name="v1",
    definition_name="openapi",
    body=ApiSpecImportRequest(
        format=ApiSpecImportSourceFormat.OPENAPI_3_0,
        value="https://example.com/openapi.json"
    )
)
```

### 6.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing definition_name
```python
# WRONG
definition = client.api_definitions.create_or_update(
    resource_group_name="my-rg",
    service_name="my-api-center",
    workspace_name="default",
    api_name="my-api",
    version_name="v1",
    resource=ApiDefinition(title="OpenAPI")
)
```

**Correct approach:** `definition_name` is a required parameter passed separately to the method call, not inside the resource body. Use: `definition_name="openapi"` alongside the resource.

---

## 7. Environment Management

### 7.1 ✅ CORRECT: Create Environment
```python
from azure.mgmt.apicenter.models import Environment, EnvironmentKind

environment = client.environments.create_or_update(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    environment_name="production",
    resource=Environment(
        title="Production",
        description="Production environment",
        kind=EnvironmentKind.PRODUCTION,
        server={
            "type": "Azure API Management",
            "management_portal_uri": ["https://portal.azure.com"]
        }
    )
)
```

### 7.2 ✅ CORRECT: List Environments
```python
environments = client.environments.list(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default"
)

for env in environments:
    print(f"{env.title} - {env.kind}")
```

### 7.3 ✅ CORRECT: Get Environment
```python
environment = client.environments.get(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    environment_name="production"
)
```

### 7.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing kind
```python
# WRONG - kind is required
environment = client.environments.create_or_update(
    ...,
    resource=Environment(
        title="Production",
        description="Prod env"
    )
)
```

**Correct approach:** Always specify the `kind` field (e.g., `EnvironmentKind.PRODUCTION`, `EnvironmentKind.STAGING`, etc.) when creating an Environment resource.

---

## 8. Deployment Tracking

### 8.1 ✅ CORRECT: Create Deployment
```python
from azure.mgmt.apicenter.models import Deployment, DeploymentState

deployment = client.deployments.create_or_update(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    api_name="my-api",
    deployment_name="prod-deployment",
    resource=Deployment(
        title="Production Deployment",
        description="Deployed to production APIM",
        environment_id="/workspaces/default/environments/production",
        definition_id="/workspaces/default/apis/my-api/versions/v1/definitions/openapi",
        state=DeploymentState.ACTIVE,
        server={"runtime_uri": ["https://api.example.com"]}
    )
)
```

### 8.2 ✅ CORRECT: List Deployments
```python
deployments = client.deployments.list(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    api_name="my-api"
)

for deployment in deployments:
    print(f"{deployment.title} - {deployment.state}")
```

### 8.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing state
```python
# WRONG - state is required for tracking
deployment = client.deployments.create_or_update(
    ...,
    resource=Deployment(
        title="Prod",
        environment_id="...",
        definition_id="..."
    )
)
```

**Correct approach:** Always specify the `state` field (e.g., `DeploymentState.ACTIVE`, `DeploymentState.INACTIVE`) when creating a Deployment resource for proper lifecycle tracking.

---

## 9. Custom Metadata Management

### 9.1 ✅ CORRECT: Define Custom Metadata Schema
```python
from azure.mgmt.apicenter.models import MetadataSchema

metadata = client.metadata_schemas.create_or_update(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    metadata_schema_name="data-classification",
    resource=MetadataSchema(
        schema='{"type": "string", "title": "Data Classification", "enum": ["public", "internal", "confidential"]}'
    )
)
```

### 9.2 ✅ CORRECT: List Metadata Schemas
```python
schemas = client.metadata_schemas.list(
    resource_group_name="my-resource-group",
    service_name="my-api-center"
)

for schema in schemas:
    print(f"{schema.name}")
```

### 9.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Invalid JSON schema
```python
# WRONG - schema must be valid JSON
metadata = client.metadata_schemas.create_or_update(
    ...,
    resource=MetadataSchema(
        schema='invalid json'
    )
)
```

**Correct approach:** Always pass valid JSON for the schema field. The schema should be a properly formatted JSON string that defines the structure and constraints for the metadata.

---

## 10. Best Practices

### ✅ Pattern: Complete API Center Workflow
```python
import os
from azure.mgmt.apicenter import ApiCenterMgmtClient
from azure.mgmt.apicenter.models import (
    Service,
    Api,
    ApiKind,
    LifecycleStage,
    ApiVersion,
    ApiDefinition,
    Environment,
    EnvironmentKind,
    Deployment,
    DeploymentState,
    ApiSpecImportRequest,
    ApiSpecImportSourceFormat,
)
from azure.identity import DefaultAzureCredential

def main():
    # Create client
    client = ApiCenterMgmtClient(
        credential=DefaultAzureCredential(),
        subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"]
    )
    
    # Create API Center
    api_center = client.services.create_or_update(
        resource_group_name="my-rg",
        service_name="my-api-center",
        resource=Service(location="eastus")
    )
    
    # Register API
    api = client.apis.create_or_update(
        resource_group_name="my-rg",
        service_name="my-api-center",
        workspace_name="default",
        api_name="my-api",
        resource=Api(
            title="My API",
            kind=ApiKind.REST,
            lifecycle_stage=LifecycleStage.PRODUCTION
        )
    )
    
    # Create API Version
    version = client.api_versions.create_or_update(
        resource_group_name="my-rg",
        service_name="my-api-center",
        workspace_name="default",
        api_name="my-api",
        version_name="v1",
        resource=ApiVersion(
            title="Version 1.0",
            lifecycle_stage=LifecycleStage.PRODUCTION
        )
    )
    
    # Add API Definition
    definition = client.api_definitions.create_or_update(
        resource_group_name="my-rg",
        service_name="my-api-center",
        workspace_name="default",
        api_name="my-api",
        version_name="v1",
        definition_name="openapi",
        resource=ApiDefinition(title="OpenAPI Definition")
    )
    
    # Create Environment
    environment = client.environments.create_or_update(
        resource_group_name="my-rg",
        service_name="my-api-center",
        workspace_name="default",
        environment_name="production",
        resource=Environment(
            title="Production",
            kind=EnvironmentKind.PRODUCTION
        )
    )
    
    # Create Deployment
    deployment = client.deployments.create_or_update(
        resource_group_name="my-rg",
        service_name="my-api-center",
        workspace_name="default",
        api_name="my-api",
        deployment_name="prod-deployment",
        resource=Deployment(
            title="Production Deployment",
            state=DeploymentState.ACTIVE,
            environment_id=environment.id,
            definition_id=definition.id
        )
    )
    
    print(f"Created API Center: {api_center.name}")
    print(f"Registered API: {api.title}")
    print(f"Deployment state: {deployment.state}")

if __name__ == "__main__":
    main()
```

---

## 11. Environment Variables

### Required Variables
```bash
AZURE_SUBSCRIPTION_ID=your-subscription-id
```

---

## 12. Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `TypeError: __init__() missing required argument 'subscription_id'` | Missing subscription_id | Add `subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"]` |
| `AttributeError: 'ApiCenterMgmtClient' has no attribute 'apis'` | Client not properly initialized | Ensure using context manager or explicit close |
| `ValueError: resource_group_name cannot be None` | Missing parameter | All operations require resource_group_name |
| `AttributeError: 'ApiKind' has no attribute 'SOAP'` | Wrong ApiKind value | Use REST, GraphQL, GRPC, or WEBHOOK |
| `TypeError: Api() missing required argument 'title'` | Missing required model field | All models require title field |
| `ValueError: workspace_name cannot be None` | Missing workspace_name | APIs require workspace_name parameter |

---

## 13. Test Scenarios Checklist

### API Center Service Management
- [ ] Create API Center with location
- [ ] List API Centers by subscription
- [ ] List API Centers by resource group
- [ ] Get single API Center
- [ ] Update API Center tags
- [ ] Delete API Center

### API Registration
- [ ] Register REST API
- [ ] Register GraphQL API
- [ ] Register GRPC API
- [ ] List APIs in workspace
- [ ] Get single API
- [ ] Update API lifecycle stage
- [ ] Delete API

### API Versions
- [ ] Create API version
- [ ] List API versions
- [ ] Get single version
- [ ] Update version lifecycle
- [ ] Delete version

### API Definitions
- [ ] Create API definition
- [ ] List definitions
- [ ] Import OpenAPI spec (inline)
- [ ] Import OpenAPI spec (URL)
- [ ] Delete definition

### Environments
- [ ] Create production environment
- [ ] Create staging environment
- [ ] List environments
- [ ] Get environment
- [ ] Delete environment

### Deployments
- [ ] Create deployment in active state
- [ ] List deployments
- [ ] Get deployment
- [ ] Update deployment state
- [ ] Delete deployment

### Metadata
- [ ] Create string metadata schema
- [ ] Create enum metadata schema
- [ ] List metadata schemas
- [ ] Delete schema

### Governance
- [ ] Use workspaces to organize APIs
- [ ] Track API lifecycle stages
- [ ] Manage API contacts
- [ ] Define terms of service
- [ ] Track deployment locations
