# FastAPI Router Acceptance Criteria

**Skill**: `fastapi-router-py`  
**Purpose**: Create FastAPI routers with CRUD operations, authentication dependencies, and proper response models  
**Template**: [template.py](../assets/template.py)

---

## 1. Router Creation Patterns

### 1.1 ✅ CORRECT: Basic Router Setup

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["items"])

@router.get("/items")
async def list_items() -> list[ItemResponse]:
    """List all items."""
    return []
```

### 1.2 ✅ CORRECT: Router with Dependencies

```python
from fastapi import APIRouter, Depends
from app.services.item_service import ItemService

router = APIRouter(prefix="/api", tags=["items"])

def get_service() -> ItemService:
    """Dependency to get service instance."""
    return ItemService()

@router.get("/items")
async def list_items(service: ItemService = Depends(get_service)):
    """List items using injected service."""
    return await service.list_items()
```

### 1.3 ❌ INCORRECT: Missing prefix or tags

```python
# WRONG - no prefix definition
router = APIRouter()
# Missing tags make route organization unclear
```

---

## 2. HTTP Methods and Status Codes

### 2.1 ✅ CORRECT: Proper Status Codes

```python
from fastapi import status

# GET - implicit 200
@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str) -> ItemResponse:
    """Get a single item."""
    return await service.get_item(item_id)

# POST - 201 Created
@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(data: ItemCreate) -> ItemResponse:
    """Create a new item."""
    return await service.create_item(data)

# PATCH - 200 (partial update)
@router.patch("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: str, data: ItemUpdate) -> ItemResponse:
    """Update an item."""
    return await service.update_item(item_id, data)

# DELETE - 204 No Content
@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: str) -> None:
    """Delete an item."""
    await service.delete_item(item_id)
```

### 2.2 ❌ INCORRECT: Wrong status codes

```python
# WRONG - POST should be 201, not default 200
@router.post("/items")
async def create_item(data: ItemCreate):
    return await service.create_item(data)

# WRONG - DELETE should be 204, not 200
@router.delete("/items/{item_id}")
async def delete_item(item_id: str):
    await service.delete_item(item_id)

# WRONG - PATCH returning None without 204
@router.patch("/items/{item_id}")
async def update_item(item_id: str, data: ItemUpdate) -> ItemResponse:
    # Missing status_code for PATCH with return value
    return await service.update_item(item_id, data)
```

---

## 3. Response Models

### 3.1 ✅ CORRECT: Typed Response Models

```python
from pydantic import BaseModel
from typing import Optional

class ItemResponse(BaseModel):
    """Response model for items."""
    id: str
    name: str
    description: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True

@router.get("/items", response_model=list[ItemResponse])
async def list_items() -> list[ItemResponse]:
    """List items."""
    return await service.list_items()

@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str) -> ItemResponse:
    """Get single item."""
    return await service.get_item(item_id)
```

### 3.2 ❌ INCORRECT: Missing or wrong response models

```python
# WRONG - no response_model specified
@router.get("/items")
async def list_items():
    # Doesn't define return type schema
    return await service.list_items()

# WRONG - response_model doesn't match return type
@router.get("/items", response_model=ItemResponse)
async def list_items() -> list[ItemResponse]:
    # Should be response_model=list[ItemResponse]
    return await service.list_items()

# WRONG - using dict instead of Pydantic model
@router.get("/items", response_model=dict)
async def list_items() -> dict:
    # Should use typed Pydantic models
    return {}
```

---

## 4. Authentication Patterns

### 4.1 ✅ CORRECT: Optional Authentication

```python
from typing import Optional
from fastapi import Depends

@router.get("/items", response_model=list[ItemResponse])
async def list_items(
    current_user: Optional[User] = Depends(get_current_user),
) -> list[ItemResponse]:
    """List items. Authentication optional."""
    # Anyone can call this, but authenticated users may get more data
    return await service.list_items(user_id=current_user.id if current_user else None)
```

### 4.2 ✅ CORRECT: Required Authentication

```python
from fastapi import Depends

@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    data: ItemCreate,
    current_user: User = Depends(get_current_user_required),  # Required
) -> ItemResponse:
    """Create item. Authentication required."""
    return await service.create_item(data, owner_id=current_user.id)
```

### 4.3 ✅ CORRECT: Query Parameters with Validation

```python
from fastapi import Query

@router.get("/items", response_model=list[ItemResponse])
async def list_items(
    limit: int = Query(default=50, ge=1, le=100, description="Max items to return"),
    offset: int = Query(default=0, ge=0, description="Items to skip"),
) -> list[ItemResponse]:
    """List items with pagination."""
    return await service.list_items(limit=limit, offset=offset)
```

### 4.4 ❌ INCORRECT: Authentication mistakes

```python
# WRONG - using string instead of dependency
@router.post("/items")
async def create_item(data: ItemCreate, current_user: str):
    # Should use Depends(get_current_user_required)
    pass

# WRONG - Optional auth on write operation
@router.post("/items")
async def create_item(
    data: ItemCreate,
    current_user: Optional[User] = Depends(get_current_user),  # Should be required
):
    return await service.create_item(data)

# WRONG - Hardcoding user ID
@router.post("/items")
async def create_item(data: ItemCreate):
    # Missing authentication entirely
    return await service.create_item(data, owner_id="hardcoded-user")
```

---

## 5. Error Handling

### 5.1 ✅ CORRECT: Proper HTTPException Usage

```python
from fastapi import HTTPException, status

@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str) -> ItemResponse:
    """Get item by ID, with error handling."""
    item = await service.get_item(item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    return item

@router.patch("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: str,
    data: ItemUpdate,
    current_user: User = Depends(get_current_user_required),
) -> ItemResponse:
    """Update item with ownership check."""
    existing = await service.get_item(item_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    
    if existing.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this item",
        )
    
    return await service.update_item(item_id, data)
```

### 5.2 ❌ INCORRECT: Poor error handling

```python
# WRONG - returning None instead of raising exception
@router.get("/items/{item_id}")
async def get_item(item_id: str):
    item = await service.get_item(item_id)
    return item  # Returns None on missing item, no 404

# WRONG - bare exception
@router.post("/items")
async def create_item(data: ItemCreate):
    try:
        return await service.create_item(data)
    except Exception:
        return {"error": "Failed"}  # Wrong! Should use HTTPException

# WRONG - wrong status code
@router.delete("/items/{item_id}")
async def delete_item(item_id: str):
    if not await service.exists(item_id):
        raise HTTPException(
            status_code=status.HTTP_200_OK,  # WRONG - should be 404
            detail="Item not found",
        )
```

---

## 6. Async Patterns

### 6.1 ✅ CORRECT: Async Endpoints

```python
@router.get("/items", response_model=list[ItemResponse])
async def list_items(service: ItemService = Depends(get_service)) -> list[ItemResponse]:
    """All endpoints should be async."""
    return await service.list_items()

@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    data: ItemCreate,
    service: ItemService = Depends(get_service),
) -> ItemResponse:
    """Create with async service call."""
    return await service.create_item(data)
```

### 6.2 ❌ INCORRECT: Synchronous endpoints

```python
# WRONG - using def instead of async def
@router.get("/items")
def list_items(service: ItemService = Depends(get_service)):
    # FastAPI endpoints should be async for concurrent handling
    return service.list_items()

# WRONG - blocking operation without await
@router.post("/items")
async def create_item(data: ItemCreate):
    # If service is async, must use await
    return service.create_item(data)  # Missing await
```

---

## 7. Dependencies and Imports

### 7.1 ✅ CORRECT: Proper Imports

```python
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.jwt import get_current_user, get_current_user_required
from app.models.user import User
from app.models.item import ItemResponse, ItemCreate, ItemUpdate
from app.services.item_service import ItemService
```

### 7.2 ✅ CORRECT: Consistent Dependency Pattern

```python
def get_service() -> ItemService:
    """Dependency to get service instance."""
    return ItemService()

@router.get("/items")
async def list_items(service: ItemService = Depends(get_service)):
    """Using dependency injection pattern."""
    return await service.list_items()
```

### 7.3 ❌ INCORRECT: Import mistakes

```python
# WRONG - importing from wrong module
from fastapi.responses import JSONResponse
# Should use response_model parameter

# WRONG - creating service inline instead of via dependency
@router.get("/items")
async def list_items():
    service = ItemService()  # Should use Depends(get_service)
    return await service.list_items()

# WRONG - forgetting authentication function
@router.post("/items")
async def create_item(data: ItemCreate, current_user: User):
    # Missing: Depends(get_current_user_required)
    pass
```

---

## 8. Path Parameters

### 8.1 ✅ CORRECT: Typed Path Parameters

```python
from typing import Annotated
from fastapi import Path

@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: Annotated[str, Path(description="Unique item ID")]
) -> ItemResponse:
    """Get item by ID."""
    return await service.get_item(item_id)

# Or simpler form
@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str) -> ItemResponse:
    """Get item by ID."""
    return await service.get_item(item_id)
```

### 8.2 ❌ INCORRECT: Path parameter mistakes

```python
# WRONG - untyped path parameter
@router.get("/items/{item_id}")
async def get_item(item_id):
    # Should have type annotation
    return await service.get_item(item_id)

# WRONG - path parameter name mismatch
@router.get("/items/{id}")
async def get_item(item_id: str):
    # Parameter name doesn't match path: {id} vs item_id
    pass
```

---

## 9. Documentation

### 9.1 ✅ CORRECT: Docstrings and Descriptions

```python
from typing import Annotated
from fastapi import Query

@router.get(
    "/items",
    response_model=list[ItemResponse],
    summary="List all items",
    description="Retrieve a paginated list of all items in the system.",
)
async def list_items(
    limit: Annotated[int, Query(ge=1, le=100, description="Max items per page")] = 50,
    offset: Annotated[int, Query(ge=0, description="Items to skip")] = 0,
) -> list[ItemResponse]:
    """
    List items with pagination.

    - **limit**: Maximum number of items to return (1-100)
    - **offset**: Number of items to skip for pagination
    """
    return await service.list_items(limit=limit, offset=offset)
```

### 9.2 ❌ INCORRECT: Missing documentation

```python
# WRONG - no docstring
@router.get("/items")
async def list_items():
    return await service.list_items()

# WRONG - unclear descriptions
@router.get("/items", response_model=list[ItemResponse])
async def list_items(limit: int = Query(default=50)) -> list[ItemResponse]:
    # No docstring, parameter description unclear
    return await service.list_items(limit=limit)
```

---

## 10. Router Mounting

### 10.1 ✅ CORRECT: Mounting in Main App

```python
# In routers/items.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["items"])

@router.get("/items")
async def list_items():
    return []

# In main.py
from fastapi import FastAPI
from routers.items import router as items_router

app = FastAPI(title="My API")
app.include_router(items_router)
```

### 10.2 ❌ INCORRECT: Router mounting mistakes

```python
# WRONG - prefix duplication
# In routers/items.py
router = APIRouter(prefix="/api/items")

# In main.py
app.include_router(items_router, prefix="/api")  # Results in /api/api/items

# WRONG - forgetting to mount router
# In main.py
from routers.items import router
# Missing: app.include_router(router)
# Routes won't be registered
```

---

## 11. Query Parameters

### 11.1 ✅ CORRECT: Query Parameter Validation

```python
from fastapi import Query
from typing import Annotated, Optional

@router.get("/items", response_model=list[ItemResponse])
async def list_items(
    skip: Annotated[int, Query(ge=0, description="Items to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Max items")] = 50,
    search: Annotated[Optional[str], Query(min_length=1, max_length=100)] = None,
) -> list[ItemResponse]:
    """List items with optional search and pagination."""
    return await service.list_items(skip=skip, limit=limit, search=search)
```

### 11.2 ❌ INCORRECT: Query parameter mistakes

```python
# WRONG - no validation
@router.get("/items")
async def list_items(limit: int = 50):
    # No validation; limit could be negative or huge
    return await service.list_items(limit=limit)

# WRONG - query in path
@router.get("/items/{search}")  # Should be query parameter
async def search_items(search: str):
    return await service.search(search)
```

---

## 12. Complete Router Example Checklist

- [ ] Router has `prefix` and `tags`
- [ ] All endpoints are `async def`
- [ ] Each endpoint has `response_model` specified
- [ ] POST returns `status.HTTP_201_CREATED`
- [ ] DELETE returns `status.HTTP_204_NO_CONTENT`
- [ ] Authentication required for write operations (POST, PATCH, DELETE)
- [ ] Error handling with appropriate HTTPException status codes
- [ ] Query parameters have validation (Query with ge, le, etc.)
- [ ] Path parameters are typed
- [ ] Service is injected via `Depends()`
- [ ] Docstrings on all endpoints
- [ ] Imports from correct modules (fastapi, app.*, etc.)
- [ ] No hardcoded values (user IDs, secrets, etc.)

---

## 13. Anti-Patterns Summary

| Anti-Pattern | Impact | Fix |
|--------------|--------|-----|
| Using `def` instead of `async def` | Blocks event loop, poor concurrency | Change to `async def` |
| Missing `response_model` | OpenAPI schema wrong, validation skipped | Add `response_model=YourModel` |
| Wrong status codes | Confuses clients, breaks contracts | Use `status.HTTP_*` constants |
| Missing error handling | 500 errors on invalid requests | Use `HTTPException` |
| Authentication on wrong endpoints | Security vulnerability or UX issue | Required for writes, optional for reads |
| Service creation inline | Hard to test, couples logic | Use `Depends(get_service)` |
| No parameter validation | Invalid data accepted | Use `Query()`, `Path()` with constraints |
| Untyped responses | Poor API documentation | Always specify `response_model` |
