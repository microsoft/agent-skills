# Azure Cosmos DB (FastAPI Patterns) Acceptance Criteria

**SDK**: `azure-cosmos`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Commit**: `n/a`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. FastAPI Service Layer Patterns

### ✅ CORRECT: Service Class with _use_cosmos and Conversion Methods
```python
from typing import Optional
from app.db.cosmos import get_container, get_document, upsert_document, delete_document, query_documents
from app.models.project import Project, ProjectCreate, ProjectUpdate, ProjectInDB

class ProjectService:
    def _use_cosmos(self) -> bool:
        return get_container() is not None

    def _doc_to_model_in_db(self, doc: dict) -> ProjectInDB:
        return ProjectInDB(
            id=doc["id"],
            name=doc["name"],
            workspace_id=doc["workspaceId"],
            doc_type=doc.get("docType", "project"),
        )

    def _model_in_db_to_doc(self, model: ProjectInDB) -> dict:
        return {
            "id": model.id,
            "name": model.name,
            "workspaceId": model.workspace_id,
            "docType": model.doc_type,
        }

    def _model_in_db_to_model(self, model: ProjectInDB) -> Project:
        return Project(id=model.id, name=model.name, workspace_id=model.workspace_id)
```

### ❌ INCORRECT: Database Access in Router (No Service Layer)
```python
from fastapi import APIRouter
from app.db.cosmos import get_container

router = APIRouter()

@router.get("/projects/{project_id}")
async def get_project(project_id: str, workspace_id: str):
    container = get_container()
    # WRONG - direct Cosmos usage in router
    return container.read_item(item=project_id, partition_key=workspace_id)
```

---

## 2. Dual Auth (DefaultAzureCredential + Emulator)

### ✅ CORRECT: Dual Authentication Strategy
```python
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential

def _is_emulator_endpoint(endpoint: str) -> bool:
    return "localhost" in endpoint.lower() or "127.0.0.1" in endpoint

def _create_client(settings) -> CosmosClient:
    if _is_emulator_endpoint(settings.cosmos_endpoint):
        return CosmosClient(
            url=settings.cosmos_endpoint,
            credential=settings.cosmos_key,
            connection_verify=False,
        )
    return CosmosClient(
        url=settings.cosmos_endpoint,
        credential=DefaultAzureCredential(),
    )
```

### ❌ INCORRECT: Using Keys in Production
```python
from azure.cosmos import CosmosClient

# WRONG - always using keys, even for Azure RBAC environments
client = CosmosClient(
    url=settings.cosmos_endpoint,
    credential=settings.cosmos_key,
)
```

---

## 3. CRUD Service Classes

### ✅ CORRECT: CRUD Methods with Graceful Defaults
```python
class ProjectService:
    def _use_cosmos(self) -> bool:
        return get_container() is not None

    async def get_by_id(self, project_id: str, workspace_id: str) -> Optional[Project]:
        if not self._use_cosmos():
            return None
        doc = await get_document(project_id, partition_key=workspace_id)
        if doc is None:
            return None
        return self._model_in_db_to_model(self._doc_to_model_in_db(doc))

    async def delete(self, project_id: str, workspace_id: str) -> bool:
        if not self._use_cosmos():
            return False
        return await delete_document(project_id, partition_key=workspace_id)

    async def list_by_workspace(self, workspace_id: str) -> list[Project]:
        if not self._use_cosmos():
            return []
        docs = await query_documents(doc_type="project", partition_key=workspace_id)
        return [self._model_in_db_to_model(self._doc_to_model_in_db(doc)) for doc in docs]
```

### ❌ INCORRECT: Missing Partition Key in CRUD
```python
async def get_by_id(self, project_id: str) -> dict:
    # WRONG - partition key missing
    container = get_container()
    return container.read_item(item=project_id)
```

---

## 4. Partition Key Strategies

### ✅ CORRECT: Parent-Scoped Partitioning
```python
class ProjectInDB(BaseModel):
    id: str
    workspace_id: str  # Partition key
    doc_type: str = "project"

doc = await get_document(project_id, partition_key=workspace_id)
```

### ✅ CORRECT: Global Partition for Cross-Cutting Entities
```python
GLOBAL_PARTITION = "global"

users = await query_documents(
    doc_type="user",
    partition_key=GLOBAL_PARTITION,
    extra_filter="AND c.email = @email",
    parameters=[{"name": "@email", "value": email}],
)
```

### ❌ INCORRECT: Cross-Partition Query Without Enable Flag
```python
# WRONG - no partition key and missing enable_cross_partition_query
items = container.query_items(
    query="SELECT * FROM c WHERE c.docType = @docType",
    parameters=[{"name": "@docType", "value": "user"}],
)
```

---

## 5. Parameterized Queries

### ✅ CORRECT: Parameterized Filters
```python
docs = await query_documents(
    doc_type="project",
    partition_key=workspace_id,
    extra_filter="AND c.slug = @slug",
    parameters=[{"name": "@slug", "value": slug}],
)
```

### ❌ INCORRECT: String Interpolation in Query
```python
query = f"SELECT * FROM c WHERE c.docType = 'project' AND c.slug = '{slug}'"
items = container.query_items(query=query)
```

---

## 6. TDD Patterns

### ✅ CORRECT: pytest + Mocked Cosmos Container
```python
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_cosmos_container(mocker):
    container = MagicMock()
    mocker.patch("app.db.cosmos.get_container", return_value=container)
    return container

@pytest.mark.asyncio
async def test_get_by_id_returns_project(mock_cosmos_container):
    mock_cosmos_container.read_item.return_value = {"id": "123", "name": "Test"}
    result = await project_service.get_by_id("123", workspace_id="ws-1")
    assert result is not None
```

### ❌ INCORRECT: Tests Without Async Mark or Mocks
```python
def test_get_by_id_hits_real_db():
    # WRONG - no pytest.mark.asyncio and no mocking
    result = await project_service.get_by_id("123", workspace_id="ws-1")
    assert result is not None
```

---

## 7. FastAPI Router Integration (Service Layer)

### ✅ CORRECT: Router Delegates to Service
```python
from fastapi import APIRouter, Depends
from app.services.project_service import project_service

router = APIRouter()

@router.get("/workspaces/{workspace_id}/projects/{project_id}")
async def get_project(project_id: str, workspace_id: str):
    return await project_service.get_by_id(project_id, workspace_id)
```

### ❌ INCORRECT: Router Constructs Cosmos Client Directly
```python
from fastapi import APIRouter
from azure.cosmos import CosmosClient

router = APIRouter()

@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    # WRONG - direct client creation inside endpoint
    client = CosmosClient(url="https://...", credential="KEY")
    container = client.get_database_client("db").get_container_client("container")
    return container.read_item(item=project_id, partition_key=project_id)
```
