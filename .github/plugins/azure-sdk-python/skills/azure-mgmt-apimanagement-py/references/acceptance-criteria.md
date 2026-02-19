# Azure API Management SDK Acceptance Criteria

**SDK**: `azure-mgmt-apimanagement`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Commit**: Latest stable v10.x
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: ApiManagementClient with DefaultAzureCredential
```python
from azure.mgmt.apimanagement import ApiManagementClient
from azure.identity import DefaultAzureCredential
import os

client = ApiManagementClient(
    credential=DefaultAzureCredential(),
    subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"]
)
```

#### ❌ INCORRECT: Missing subscription_id
```python
from azure.mgmt.apimanagement import ApiManagementClient
client = ApiManagementClient(credential=DefaultAzureCredential())
# subscription_id is required parameter
```

#### ❌ INCORRECT: Hardcoded subscription ID
```python
client = ApiManagementClient(
    credential=DefaultAzureCredential(),
    subscription_id="12345-67890-abcde"  # Don't hardcode
)
```

### 1.2 Model Imports

#### ✅ CORRECT: Models from azure.mgmt.apimanagement.models
```python
from azure.mgmt.apimanagement.models import (
    ApiManagementServiceResource,
    ApiManagementServiceSkuProperties,
    ApiCreateOrUpdateParameter,
    ProductContract,
    SubscriptionCreateParameters,
    PolicyContract,
    NamedValueCreateContract,
    BackendContract,
)
```

#### ❌ INCORRECT: Models from wrong location
```python
from azure.mgmt.apimanagement import ApiManagementServiceResource  # Wrong
from azure.mgmt.apimanagement.operations import ProductContract    # Wrong
```

#### ✅ CORRECT: Enum imports
```python
from azure.mgmt.apimanagement.models import (
    SkuType,
    ContentFormat,
    Protocol,
)
```

---

## 2. Client Creation Patterns

### 2.1 Authentication

#### ✅ CORRECT: DefaultAzureCredential (recommended)
```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient
import os

client = ApiManagementClient(
    credential=DefaultAzureCredential(),
    subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"]
)
```

#### ✅ CORRECT: Using environment variables
```python
client = ApiManagementClient(
    credential=DefaultAzureCredential(),
    subscription_id=os.environ.get("AZURE_SUBSCRIPTION_ID")
)
```

#### ❌ INCORRECT: Hardcoded credentials
```python
from azure.mgmt.apimanagement import ApiManagementClient
client = ApiManagementClient(
    credential="my-secret-key",
    subscription_id="12345-67890"
)
```

#### ❌ INCORRECT: Missing environment variable check
```python
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]  # Can raise KeyError
# Should be os.environ.get() or handled gracefully
```

---

## 3. APIM Service Operations

### 3.1 Service Creation

#### ✅ CORRECT: Create APIM service with LRO
```python
from azure.mgmt.apimanagement.models import (
    ApiManagementServiceResource,
    ApiManagementServiceSkuProperties,
    SkuType,
)

service = client.api_management_service.begin_create_or_update(
    resource_group_name="my-rg",
    service_name="my-apim",
    parameters=ApiManagementServiceResource(
        location="eastus",
        publisher_email="admin@example.com",
        publisher_name="My Organization",
        sku=ApiManagementServiceSkuProperties(
            name=SkuType.DEVELOPER,
            capacity=1
        )
    )
).result()
```

#### ✅ CORRECT: Alternative with async LRO (if async)
```python
service = await client.api_management_service.begin_create_or_update(
    resource_group_name="my-rg",
    service_name="my-apim",
    parameters=ApiManagementServiceResource(...)
).result()
```

#### ❌ INCORRECT: Missing .result() on LRO
```python
service = client.api_management_service.begin_create_or_update(
    resource_group_name="my-rg",
    service_name="my-apim",
    parameters=ApiManagementServiceResource(...)
)
# This returns PollerLRO, not the service resource
```

#### ❌ INCORRECT: Not passing required parameters
```python
client.api_management_service.begin_create_or_update(
    service_name="my-apim",
    # Missing resource_group_name and parameters
)
```

### 3.2 Service Operations

#### ✅ CORRECT: List APIM services
```python
services = client.api_management_service.list_by_resource_group(
    resource_group_name="my-rg"
)

for service in services:
    print(f"{service.name}: {service.id}")
```

#### ✅ CORRECT: Get specific service
```python
service = client.api_management_service.get(
    resource_group_name="my-rg",
    service_name="my-apim"
)
```

#### ✅ CORRECT: Delete service
```python
poller = client.api_management_service.begin_delete(
    resource_group_name="my-rg",
    service_name="my-apim"
)
poller.result()  # Wait for completion
```

---

## 4. API Management

### 4.1 API Creation from OpenAPI

#### ✅ CORRECT: Import API from OpenAPI JSON
```python
from azure.mgmt.apimanagement.models import (
    ApiCreateOrUpdateParameter,
    ContentFormat,
    Protocol,
)

api = client.api.begin_create_or_update(
    resource_group_name="my-rg",
    service_name="my-apim",
    api_id="my-api",
    parameters=ApiCreateOrUpdateParameter(
        display_name="My API",
        path="myapi",
        protocols=[Protocol.HTTPS],
        format=ContentFormat.OPENAPI_JSON,
        value='{"openapi": "3.0.0", ...}'
    )
).result()
```

#### ✅ CORRECT: Import API from URL
```python
api = client.api.begin_create_or_update(
    resource_group_name="my-rg",
    service_name="my-apim",
    api_id="petstore",
    parameters=ApiCreateOrUpdateParameter(
        display_name="Petstore API",
        path="petstore",
        protocols=[Protocol.HTTPS],
        format=ContentFormat.OPENAPI_LINK,
        value="https://petstore.swagger.io/v2/swagger.json"
    )
).result()
```

#### ❌ INCORRECT: Missing format parameter
```python
api = client.api.begin_create_or_update(
    resource_group_name="my-rg",
    service_name="my-apim",
    api_id="my-api",
    parameters=ApiCreateOrUpdateParameter(
        display_name="My API",
        path="myapi",
        value='{"openapi": "3.0.0", ...}'
        # Missing format and protocols
    )
).result()
```

### 4.2 API Operations

#### ✅ CORRECT: List APIs
```python
apis = client.api.list_by_service(
    resource_group_name="my-rg",
    service_name="my-apim"
)

for api in apis:
    print(f"{api.name}: {api.display_name}")
```

#### ✅ CORRECT: List API operations
```python
operations = client.api_operation.list_by_api(
    resource_group_name="my-rg",
    service_name="my-apim",
    api_id="my-api"
)

for op in operations:
    print(f"{op.name}: {op.display_name}")
```

#### ✅ CORRECT: Delete API
```python
client.api.delete(
    resource_group_name="my-rg",
    service_name="my-apim",
    api_id="my-api"
)
```

---

## 5. Product Management

### 5.1 Product Creation

#### ✅ CORRECT: Create product
```python
from azure.mgmt.apimanagement.models import ProductContract

product = client.product.create_or_update(
    resource_group_name="my-rg",
    service_name="my-apim",
    product_id="premium",
    parameters=ProductContract(
        display_name="Premium",
        description="Premium tier with unlimited access",
        subscription_required=True,
        approval_required=False,
        state="published"
    )
)
```

#### ✅ CORRECT: Add API to product
```python
client.product_api.create_or_update(
    resource_group_name="my-rg",
    service_name="my-apim",
    product_id="premium",
    api_id="my-api"
)
```

#### ❌ INCORRECT: Missing required product fields
```python
product = client.product.create_or_update(
    resource_group_name="my-rg",
    service_name="my-apim",
    product_id="premium",
    parameters=ProductContract(
        # Missing display_name
        description="Premium tier"
    )
)
```

### 5.2 Product Operations

#### ✅ CORRECT: List products
```python
products = client.product.list_by_service(
    resource_group_name="my-rg",
    service_name="my-apim"
)

for product in products:
    print(f"{product.name}: {product.display_name}")
```

#### ✅ CORRECT: Delete product
```python
client.product.delete(
    resource_group_name="my-rg",
    service_name="my-apim",
    product_id="premium"
)
```

---

## 6. Subscription Management

### 6.1 Subscription Creation

#### ✅ CORRECT: Create subscription
```python
from azure.mgmt.apimanagement.models import SubscriptionCreateParameters

subscription = client.subscription.create_or_update(
    resource_group_name="my-rg",
    service_name="my-apim",
    sid="my-subscription",
    parameters=SubscriptionCreateParameters(
        display_name="My Subscription",
        scope="/products/premium",
        state="active"
    )
)
```

#### ✅ CORRECT: Get subscription with keys
```python
subscription = client.subscription.get(
    resource_group_name="my-rg",
    service_name="my-apim",
    sid="my-subscription"
)

print(f"Primary key: {subscription.primary_key}")
print(f"Secondary key: {subscription.secondary_key}")
```

#### ❌ INCORRECT: Missing scope parameter
```python
subscription = client.subscription.create_or_update(
    resource_group_name="my-rg",
    service_name="my-apim",
    sid="my-subscription",
    parameters=SubscriptionCreateParameters(
        display_name="My Subscription",
        # Missing scope - indicates product or API scope
    )
)
```

### 6.2 Subscription Operations

#### ✅ CORRECT: List subscriptions
```python
subscriptions = client.subscription.list(
    resource_group_name="my-rg",
    service_name="my-apim"
)

for sub in subscriptions:
    print(f"{sub.name}: {sub.display_name}")
```

#### ✅ CORRECT: Regenerate subscription keys
```python
client.subscription.regenerate_primary_key(
    resource_group_name="my-rg",
    service_name="my-apim",
    sid="my-subscription"
)

client.subscription.regenerate_secondary_key(
    resource_group_name="my-rg",
    service_name="my-apim",
    sid="my-subscription"
)
```

---

## 7. Policy Management

### 7.1 API Policy Creation

#### ✅ CORRECT: Set API-level policy with rate limiting
```python
from azure.mgmt.apimanagement.models import PolicyContract

policy_xml = """<policies>
    <inbound>
        <rate-limit calls="100" renewal-period="60" />
        <set-header name="X-Custom-Header" exists-action="override">
            <value>CustomValue</value>
        </set-header>
    </inbound>
    <backend>
        <forward-request />
    </backend>
    <outbound />
    <on-error />
</policies>"""

client.api_policy.create_or_update(
    resource_group_name="my-rg",
    service_name="my-apim",
    api_id="my-api",
    policy_id="policy",
    parameters=PolicyContract(
        value=policy_xml,
        format="xml"
    )
)
```

#### ✅ CORRECT: Set operation-level policy
```python
operation_policy = client.api_operation_policy.create_or_update(
    resource_group_name="my-rg",
    service_name="my-apim",
    api_id="my-api",
    operation_id="get-user",
    policy_id="policy",
    parameters=PolicyContract(
        value=policy_xml,
        format="xml"
    )
)
```

#### ❌ INCORRECT: Policy XML missing required sections
```python
invalid_policy = """<policies>
    <inbound>
        <rate-limit calls="100" renewal-period="60" />
    </inbound>
</policies>"""
# Missing <backend>, <outbound>, <on-error> sections
```

#### ❌ INCORRECT: Using string instead of PolicyContract
```python
client.api_policy.create_or_update(
    resource_group_name="my-rg",
    service_name="my-apim",
    api_id="my-api",
    policy_id="policy",
    parameters=policy_xml  # Should be PolicyContract object
)
```

### 7.2 Policy Operations

#### ✅ CORRECT: Get policy
```python
policy = client.api_policy.get(
    resource_group_name="my-rg",
    service_name="my-apim",
    api_id="my-api",
    policy_id="policy"
)

print(policy.value)  # Returns XML
```

#### ✅ CORRECT: Delete policy
```python
client.api_policy.delete(
    resource_group_name="my-rg",
    service_name="my-apim",
    api_id="my-api",
    policy_id="policy"
)
```

---

## 8. Named Values & Backends

### 8.1 Named Value (Secret) Management

#### ✅ CORRECT: Create named value for secrets
```python
from azure.mgmt.apimanagement.models import NamedValueCreateContract

named_value = client.named_value.begin_create_or_update(
    resource_group_name="my-rg",
    service_name="my-apim",
    named_value_id="backend-api-key",
    parameters=NamedValueCreateContract(
        display_name="Backend API Key",
        value="secret-key-value",
        secret=True
    )
).result()
```

#### ✅ CORRECT: Use named value in policy
```python
policy_xml = """<policies>
    <inbound>
        <set-header name="Authorization" exists-action="override">
            <value>Bearer {{backend-api-key}}</value>
        </set-header>
    </inbound>
</policies>"""
```

#### ❌ INCORRECT: Storing plain secrets without secret flag
```python
named_value = client.named_value.begin_create_or_update(
    resource_group_name="my-rg",
    service_name="my-apim",
    named_value_id="backend-api-key",
    parameters=NamedValueCreateContract(
        display_name="Backend API Key",
        value="secret-key-value",
        secret=False  # Don't mark as secret - bad practice
    )
).result()
```

### 8.2 Backend Management

#### ✅ CORRECT: Create backend service
```python
from azure.mgmt.apimanagement.models import BackendContract

backend = client.backend.create_or_update(
    resource_group_name="my-rg",
    service_name="my-apim",
    backend_id="my-backend",
    parameters=BackendContract(
        url="https://api.backend.example.com",
        protocol="http",
        description="My backend service"
    )
)
```

#### ✅ CORRECT: List backends
```python
backends = client.backend.list_by_service(
    resource_group_name="my-rg",
    service_name="my-apim"
)

for backend in backends:
    print(f"{backend.name}: {backend.url}")
```

#### ❌ INCORRECT: Missing URL parameter
```python
backend = client.backend.create_or_update(
    resource_group_name="my-rg",
    service_name="my-apim",
    backend_id="my-backend",
    parameters=BackendContract(
        protocol="http",
        # Missing url
    )
)
```

---

## 9. Anti-Patterns (ERRORS)

### 9.1 Common Mistakes

#### ❌ INCORRECT: Not handling LRO properly
```python
# Don't forget .result()
service = client.api_management_service.begin_create_or_update(...)
# service is a Poller, not the actual service

# Correct:
service = client.api_management_service.begin_create_or_update(...).result()
```

#### ❌ INCORRECT: Mixing authentication patterns
```python
# Don't use both managed identity and other credentials
from azure.identity import ManagedIdentityCredential, DefaultAzureCredential

# This is wrong - pick one
credential = DefaultAzureCredential()  # This includes managed identity
credential = ManagedIdentityCredential()  # Don't mix
```

#### ❌ INCORRECT: Assuming all operations are LRO
```python
# Some operations don't return pollers
product = client.product.create_or_update(...)  # No .result()
named_value = client.named_value.begin_create_or_update(...).result()  # Has .begin_
```

#### ❌ INCORRECT: Resource group not specified
```python
# Many operations require resource_group_name
client.api.list_by_service(
    service_name="my-apim"
    # Missing resource_group_name
)
```

#### ❌ INCORRECT: Hardcoding string enums
```python
# Use enums from models
client.product.create_or_update(
    parameters=ProductContract(
        state="published"  # String enum - okay but fragile
    )
)

# Better:
from azure.mgmt.apimanagement.models import ProductStateEnum
parameters=ProductContract(
    state=ProductStateEnum.PUBLISHED  # Type-safe
)
```

---

## 10. Operation Groups Reference

| Operation Group | Method Examples | Purpose |
|-----------------|-----------------|---------|
| `api_management_service` | `get()`, `create_or_update()`, `delete()`, `list_by_resource_group()` | APIM instance management |
| `api` | `get()`, `create_or_update()`, `delete()`, `list_by_service()` | API CRUD operations |
| `api_operation` | `get()`, `create_or_update()`, `list_by_api()` | API operation details |
| `api_policy` | `get()`, `create_or_update()`, `delete()` | API-level policies |
| `api_operation_policy` | `get()`, `create_or_update()`, `delete()` | Operation-level policies |
| `product` | `get()`, `create_or_update()`, `delete()`, `list_by_service()` | Product management |
| `product_api` | `create_or_update()`, `get()`, `delete()`, `list_by_product()` | Product-API associations |
| `subscription` | `get()`, `create_or_update()`, `delete()`, `list()` | Subscription CRUD |
| `subscription.regenerate_primary_key()` | `regenerate_primary_key()` | Regenerate subscription keys |
| `user` | `get()`, `create_or_update()`, `delete()`, `list()` | User management |
| `named_value` | `get()`, `create_or_update()`, `delete()`, `list_by_service()` | Named values/secrets |
| `backend` | `get()`, `create_or_update()`, `delete()`, `list_by_service()` | Backend services |

