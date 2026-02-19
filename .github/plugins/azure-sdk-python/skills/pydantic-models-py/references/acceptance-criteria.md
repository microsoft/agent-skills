# Pydantic Models Acceptance Criteria

**SDK**: `pydantic` (v2)
**Documentation**: https://docs.pydantic.dev/latest/
**Purpose**: Skill testing acceptance criteria for validating Pydantic model patterns

---

## 1. Import Patterns

### 1.1 Base Imports

#### ✅ CORRECT: Standard Pydantic Imports
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
```

#### ✅ CORRECT: Field with Configuration
```python
from pydantic import BaseModel, Field, ConfigDict
```

#### ✅ CORRECT: Validators (v2)
```python
from pydantic import BaseModel, field_validator, model_validator
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Old Pydantic v1 Config Pattern
```python
class MyModel(BaseModel):
    name: str
    
    class Config:  # v1 pattern - should use ConfigDict
        orm_mode = True
```

#### ❌ INCORRECT: Missing Required Imports
```python
# WRONG - Field is not imported
class MyModel(BaseModel):
    name: str = Field(...)  # NameError
```

#### ❌ INCORRECT: Wrong Module Paths
```python
# WRONG - wrong import locations
from pydantic.main import BaseModel
from pydantic.fields import Field
```

---

## 2. Base Model Pattern

### 2.1 ✅ CORRECT: Minimal Base Model
```python
from pydantic import BaseModel, Field
from typing import Optional

class ProjectBase(BaseModel):
    """Base model with common fields."""
    
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    
    class Config:
        populate_by_name = True  # Accept both snake_case and camelCase
```

### 2.2 ✅ CORRECT: Base with Field Aliases (camelCase)
```python
class ProjectBase(BaseModel):
    """Base model with camelCase aliases."""
    
    name: str = Field(..., description="Project name")
    owner_id: str = Field(..., alias="ownerId")
    created_at: datetime = Field(..., alias="createdAt")
    
    class Config:
        populate_by_name = True
```

### 2.3 ✅ CORRECT: ConfigDict (Pydantic v2)
```python
from pydantic import BaseModel, ConfigDict

class ProjectBase(BaseModel):
    """Using ConfigDict for Pydantic v2."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    name: str = Field(...)
```

### 2.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Invalid Field Usage
```python
# WRONG - Field ellipsis without required flag
class MyModel(BaseModel):
    name: str = Field(min_length=1)  # Should be Field(..., min_length=1)
```

#### ❌ INCORRECT: Missing populate_by_name
```python
# WRONG - aliases not accepted
class MyModel(BaseModel):
    owner_id: str = Field(..., alias="ownerId")
    # Missing: populate_by_name = True in Config
```

#### ❌ INCORRECT: Mixing Config Styles
```python
# WRONG - mixing v1 and v2 styles
class MyModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    class Config:  # Don't mix styles
        orm_mode = True
```

---

## 3. Create Model Pattern

### 3.1 ✅ CORRECT: Create Model with Required Fields
```python
class ProjectCreate(ProjectBase):
    """Request model for creating a project."""
    
    workspace_id: str = Field(..., alias="workspaceId")
    tags: Optional[list[str]] = Field(None, min_items=1)
```

### 3.2 ✅ CORRECT: Create with Additional Required Fields
```python
class ProjectCreate(ProjectBase):
    """Create inherits common fields, adds specific ones."""
    
    workspace_id: str = Field(..., description="Parent workspace ID")
    visibility: str = Field("private", pattern="^(private|public)$")
```

### 3.3 ✅ CORRECT: Create Without Extra Inheritance
```python
class ProjectCreate(BaseModel):
    """Can inherit directly from BaseModel if needed."""
    
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    workspace_id: str = Field(...)
    
    class Config:
        populate_by_name = True
```

### 3.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Optional Required Fields
```python
# WRONG - Field(...) means required, not optional
class ProjectCreate(ProjectBase):
    workspace_id: Optional[str] = Field(...)  # Contradictory
```

#### ❌ INCORRECT: Not Inheriting Base
```python
# WRONG - duplicates base fields instead of inheriting
class ProjectCreate(BaseModel):
    name: str = Field(...)  # Duplicated from Base
    description: Optional[str] = None  # Duplicated from Base
    workspace_id: str = Field(...)
```

---

## 4. Update Model Pattern

### 4.1 ✅ CORRECT: All Fields Optional
```python
from typing import Optional

class ProjectUpdate(BaseModel):
    """All fields optional for PATCH requests."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    visibility: Optional[str] = Field(None, pattern="^(private|public)$")
    
    class Config:
        populate_by_name = True
```

### 4.2 ✅ CORRECT: Update with Validation
```python
class ProjectUpdate(BaseModel):
    """Update with constraints on optional fields."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    tags: Optional[list[str]] = Field(None, min_items=1, max_items=10)
    
    class Config:
        populate_by_name = True
```

### 4.3 ✅ CORRECT: Exclude Certain Fields from Update
```python
class ProjectUpdate(BaseModel):
    """Update - excludes id and timestamps."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    # Note: id, created_at, updated_at are NOT included (immutable)
    
    class Config:
        populate_by_name = True
```

### 4.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Required Fields in Update
```python
# WRONG - Update should have all optional fields
class ProjectUpdate(BaseModel):
    name: str = Field(...)  # Should be Optional[str]
    description: Optional[str] = None
```

#### ❌ INCORRECT: Inheriting from Create
```python
# WRONG - Update and Create have different patterns
class ProjectUpdate(ProjectCreate):  # Create has required fields!
    pass
```

#### ❌ INCORRECT: Missing Config
```python
# WRONG - Update needs Config for camelCase aliases
class ProjectUpdate(BaseModel):
    owner_id: Optional[str] = Field(None, alias="ownerId")
    # Missing: populate_by_name = True
```

---

## 5. Response Model Pattern

### 5.1 ✅ CORRECT: Response Inheriting Base
```python
from datetime import datetime

class Project(ProjectBase):
    """Response model with all fields.
    
    Returned from API GET endpoints.
    """
    
    id: str = Field(..., description="Unique identifier")
    workspace_id: str = Field(..., alias="workspaceId")
    author_id: str = Field(..., alias="authorId")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    
    class Config:
        from_attributes = True  # Enable ORM mode
        populate_by_name = True
```

### 5.2 ✅ CORRECT: Response with from_attributes (ORM Support)
```python
class Project(ProjectBase):
    """Response with ORM mode for SQLAlchemy objects."""
    
    id: str
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    
    class Config:
        from_attributes = True
        populate_by_name = True
```

### 5.3 ✅ CORRECT: Response with Nested Models
```python
class WorkspaceRef(BaseModel):
    """Reference to parent workspace."""
    id: str
    name: str

class Project(ProjectBase):
    """Response with nested model."""
    
    id: str
    workspace: WorkspaceRef
    created_at: datetime = Field(..., alias="createdAt")
    
    class Config:
        populate_by_name = True
```

### 5.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing ORM Mode
```python
# WRONG - can't deserialize from ORM objects without from_attributes
class Project(ProjectBase):
    id: str
    created_at: datetime
    # Missing: from_attributes = True
```

#### ❌ INCORRECT: Response with Optional ID
```python
# WRONG - response should always have id
class Project(ProjectBase):
    id: Optional[str] = None  # Should be required
```

#### ❌ INCORRECT: Including Update Fields
```python
# WRONG - response shouldn't allow field modification
class Project(ProjectBase):
    id: str
    workspace_id: str = Field(..., description="Can be updated")  # Response is immutable
```

---

## 6. InDB (Database) Model Pattern

### 6.1 ✅ CORRECT: InDB with doc_type
```python
class ProjectInDB(Project):
    """Database document model.
    
    Includes doc_type for Cosmos DB partitioning and queries.
    """
    
    doc_type: str = "project"
```

### 6.2 ✅ CORRECT: InDB with Inheritance Chain
```python
# Inheritance: ProjectInDB -> Project -> ProjectBase
class ProjectInDB(Project):
    """Database model inherits all fields from Response."""
    
    doc_type: str = "project"
    # Automatically includes: id, name, description, created_at, etc.
```

### 6.3 ✅ CORRECT: InDB with Additional Fields
```python
class ProjectInDB(Project):
    """Database model with storage-specific fields."""
    
    doc_type: str = "project"
    _partition_key: str = Field(..., description="Cosmos DB partition key")
    _etag: Optional[str] = None  # For optimistic concurrency
```

### 6.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: doc_type as Optional
```python
# WRONG - doc_type should be a constant string
class ProjectInDB(Project):
    doc_type: Optional[str] = None  # Should be: doc_type: str = "project"
```

#### ❌ INCORRECT: Not Inheriting Response
```python
# WRONG - should inherit from Response model
class ProjectInDB(ProjectBase):  # Missing intermediate Response
    doc_type: str = "project"
```

#### ❌ INCORRECT: Repeating Fields from Response
```python
# WRONG - don't redefine inherited fields
class ProjectInDB(Project):
    id: str = Field(...)  # Already in Project
    doc_type: str = "project"
```

---

## 7. Field Validation Patterns

### 7.1 ✅ CORRECT: Field Constraints
```python
class Project(BaseModel):
    """Model with various field constraints."""
    
    name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    age: int = Field(..., ge=0, le=150)
    tags: list[str] = Field(default_factory=list, min_items=0, max_items=10)
    priority: int = Field(default=1, ge=1, le=5)
```

### 7.2 ✅ CORRECT: Custom Validators (v2)
```python
from pydantic import field_validator

class Project(BaseModel):
    name: str
    
    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
```

### 7.3 ✅ CORRECT: Model Validators
```python
from pydantic import model_validator

class Project(BaseModel):
    start_date: datetime
    end_date: datetime
    
    @model_validator(mode='after')
    def validate_dates(self):
        if self.start_date >= self.end_date:
            raise ValueError('start_date must be before end_date')
        return self
```

### 7.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using v1 Validator Syntax
```python
# WRONG - v1 syntax in v2 code
from pydantic import validator

class Project(BaseModel):
    name: str
    
    @validator('name')  # v1 decorator
    def validate_name(cls, v):
        return v
```

#### ❌ INCORRECT: Validator Not Using classmethod
```python
# WRONG - validator must be classmethod
@field_validator('name')
def name_validator(self, v):  # Missing @classmethod
    return v
```

#### ❌ INCORRECT: Overly Complex Validation
```python
# WRONG - validation logic in Field that belongs in validator
name: str = Field(
    ...,
    validation_alias="proj_name",  # This is for deserialization, not validation
)
```

---

## 8. Type Hints and Optional Pattern

### 8.1 ✅ CORRECT: Optional Fields
```python
from typing import Optional
from datetime import datetime

class Project(BaseModel):
    name: str  # Required
    description: Optional[str] = None  # Optional with default None
    created_at: datetime  # Required
    updated_at: Optional[datetime] = None  # Optional with default None
```

### 8.2 ✅ CORRECT: Modern Python Type Syntax
```python
from datetime import datetime

class Project(BaseModel):
    name: str  # Required
    description: str | None = None  # Python 3.10+ union syntax
    tags: list[str] = []  # Required list, default empty
    metadata: dict[str, str] | None = None  # Optional dict
```

### 8.3 ✅ CORRECT: Complex Types
```python
from typing import Optional, Literal

class Project(BaseModel):
    status: Literal["active", "inactive", "archived"]
    priorities: list[int] = []
    config: dict[str, str | int | bool] = {}
```

### 8.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Confusing Optional with Required
```python
# WRONG - Optional with Field(...) is contradictory
class Project(BaseModel):
    description: Optional[str] = Field(...)  # Should be: Field(None)
```

#### ❌ INCORRECT: Missing Type Hints
```python
# WRONG - no type hints
class Project(BaseModel):
    name = Field(...)  # Missing: : str
```

#### ❌ INCORRECT: Wrong Optional Pattern
```python
# WRONG - don't use Union syntax when Optional exists
from typing import Union
description: Union[str, None] = None  # Use Optional[str] instead
```

---

## 9. Inheritance and Model Relationships

### 9.1 ✅ CORRECT: Linear Inheritance Chain
```python
# ProjectBase -> Project -> ProjectInDB
class ProjectBase(BaseModel):
    name: str

class Project(ProjectBase):
    id: str
    created_at: datetime

class ProjectInDB(Project):
    doc_type: str = "project"
```

### 9.2 ✅ CORRECT: Multiple Model Variants
```python
# All inherit from Base, no circular dependencies
class ProjectBase(BaseModel):
    name: str

class ProjectCreate(ProjectBase):
    workspace_id: str

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    workspace_id: Optional[str] = None

class Project(ProjectBase):
    id: str

class ProjectInDB(Project):
    doc_type: str = "project"
```

### 9.3 ✅ CORRECT: Shared Base with Different Traits
```python
class ProjectBase(BaseModel):
    """All projects have name and description."""
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    """Create adds workspace requirement."""
    workspace_id: str

class ProjectResponse(ProjectBase):
    """Response adds id and timestamps."""
    id: str
    created_at: datetime
```

### 9.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Circular Inheritance
```python
# WRONG - circular dependency
class ProjectCreate(ProjectResponse):  # Response has id
    pass

class ProjectResponse(ProjectCreate):  # Create is subset
    id: str
```

#### ❌ INCORRECT: Deep Multi-Level Inheritance
```python
# WRONG - unnecessarily deep hierarchy
class A(BaseModel): pass
class B(A): pass
class C(B): pass
class D(C): pass  # Too many levels
```

#### ❌ INCORRECT: Duplicate Fields in Hierarchy
```python
# WRONG - name defined in both Base and Create
class ProjectBase(BaseModel):
    name: str

class ProjectCreate(ProjectBase):
    name: str = Field(...)  # Already inherited!
```

---

## 10. Configuration and Settings

### 10.1 ✅ CORRECT: Modern ConfigDict (v2)
```python
from pydantic import BaseModel, ConfigDict

class Project(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        str_strip_whitespace=True,
    )
    
    name: str
```

### 10.2 ✅ CORRECT: Class Config (v2)
```python
class Project(BaseModel):
    name: str
    
    class Config:
        populate_by_name = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "name": "My Project",
                "workspace_id": "ws_123"
            }
        }
```

### 10.3 ✅ CORRECT: Validation Context
```python
from pydantic import field_validator, ValidationInfo

class Project(BaseModel):
    name: str
    owner_id: str
    
    @field_validator('owner_id')
    @classmethod
    def validate_owner(cls, v, info: ValidationInfo):
        context = info.context or {}
        allowed_owners = context.get('allowed_owners', [])
        if allowed_owners and v not in allowed_owners:
            raise ValueError(f'Owner {v} not allowed')
        return v
```

### 10.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using orm_mode (deprecated in v2)
```python
# WRONG - orm_mode was renamed in v2
class Project(BaseModel):
    class Config:
        orm_mode = True  # Should be: from_attributes = True
```

---

## 11. Common Mistakes and Fixes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Missing Field import | `NameError: Field not defined` | `from pydantic import BaseModel, Field` |
| Optional without default | `ValidationError: field required` | `field: Optional[str] = None` |
| Wrong alias config | camelCase not accepted | Add `populate_by_name = True` |
| Using v1 syntax | `ImportError, TypeError` | Use `@field_validator`, `from_attributes` |
| `doc_type` optional | Query failures in Cosmos DB | Use `doc_type: str = "resource_name"` |
| Not inheriting Base | Code duplication | `class Create(Base):` |
| All fields optional in Create | Validation not catching missing data | Create should inherit required Base fields |
| Response inherits Create | Update fields exposed | Response should inherit Base, not Create |
| Circular imports | `ImportError` | Use forward references: `from __future__ import annotations` |

---

## 12. Test Scenarios Checklist

### Model Pattern Creation
- [ ] Base model with common fields and populate_by_name
- [ ] Create model inheriting Base with required fields
- [ ] Update model with all optional fields
- [ ] Response model with id and timestamps
- [ ] InDB model with doc_type constant

### Type and Validation
- [ ] Field constraints (min_length, max_length, pattern, ge, le)
- [ ] Optional vs required fields correctly used
- [ ] Custom validators with field_validator
- [ ] Model-level validation with model_validator
- [ ] Complex types (list, dict, unions, Literals)

### Configuration
- [ ] populate_by_name for alias acceptance
- [ ] from_attributes for ORM support
- [ ] Proper inheritance chain (Base -> Response -> InDB)
- [ ] No circular dependencies

### Common Patterns
- [ ] camelCase aliases with snake_case fields
- [ ] Create includes required workspace_id
- [ ] Update excludes immutable fields (id, created_at)
- [ ] Response includes all display fields
- [ ] InDB is append-only (only adds doc_type)

---

## 13. SDK Version Info

- **Pydantic**: v2.x (current)
- **Python**: 3.9+
- **Key Breaking Changes from v1**:
  - `from pydantic import validator` → `from pydantic import field_validator`
  - `Config.orm_mode` → `Config.from_attributes`
  - `Config.json_schema_extra` replaces `schema_extra`
  - Validators require `@classmethod`
  - Type hints are now mandatory
