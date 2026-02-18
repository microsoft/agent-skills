---
name: robot-framework-py
description: >-
  Robot Framework skill for Python-centric test automation. USE FOR: creating
  or refactoring .robot suites, .resource files, RequestsLibrary API tests, and
  custom Python keyword libraries; enforcing valid Robot Framework sections,
  reusable resource layering, tags/variables strategy, and BuiltIn or
  OperatingSystem usage. DO NOT USE FOR: Selenium, Browser, Appium, or other UI
  automation stacks unless the user explicitly requests those libraries.
---

# Robot Framework (Python)

Use this skill to produce deterministic, maintainable Robot Framework code for API and service-level automation.

## Apply this project structure by default

```text
tests/
resources/
libraries/
variables/
```

- Place suite files in `tests/`.
- Place reusable keywords in `resources/`.
- Place custom Python keyword libraries in `libraries/`.
- Place environment-specific variable files in `variables/`.

## Generate valid Robot Framework files

- Emit standard sections when creating suite files:
  - `*** Settings ***`
  - `*** Variables ***` (when variables are needed)
  - `*** Test Cases ***`
  - `*** Keywords ***` (when local keywords are needed)
- Emit reusable sections only when creating `.resource` files:
  - `*** Settings ***`
  - `*** Variables ***` (optional)
  - `*** Keywords ***`
- Prefer BuiltIn assertions (`Should Be Equal`, `Should Contain`, `Should Be True`) over ad-hoc assertion logic.

## Design for scale and reuse

- Keep test cases short and move repeated flows into resource keywords.
- Use `Suite Setup` and `Suite Teardown` for shared lifecycle steps.
- Apply consistent tags (for example: `smoke`, `api`, `regression`, domain tags).
- Keep secrets out of source files; read secrets from environment variables or secure variable files.

## Use standard libraries deliberately

- Use BuiltIn for assertions, logging, and control flow.
- Use OperatingSystem for file and environment checks.
- Use Collections, String, Process, and XML libraries only when their keywords are explicitly needed.
- Name imported libraries explicitly in `*** Settings ***`.

## Follow the RequestsLibrary API testing path

- Install with `pip install robotframework-requests`.
- Create sessions with `Create Session`.
- Reuse sessions for related requests.
- Build auth headers and common request data in reusable keywords.
- Assert both HTTP status and critical response fields.

### Minimal RequestsLibrary example

```robotframework
*** Settings ***
Library    RequestsLibrary

*** Variables ***
${BASE_URL}    https://api.example.com

*** Test Cases ***
Get Health Endpoint
    Create Session    api    ${BASE_URL}
    ${resp}=    GET On Session    api    /health
    Should Be Equal As Integers    ${resp.status_code}    200
```

## Implement Python keyword libraries safely

- Keep each keyword focused on one responsibility.
- Return values in simple serializable types whenever possible.
- Raise clear assertion failures for invalid inputs or state.

### Module-style keyword library

```python
from robot.api.deco import keyword

@keyword("Normalize Text")
def normalize_text(value: str) -> str:
    return " ".join(value.split()).strip().lower()
```

### Class-style keyword library

```python
from robot.api.deco import keyword

class MathKeywords:
    @keyword("Add Integers")
    def add_integers(self, left: int, right: int) -> int:
        return int(left) + int(right)
```

## Prevent hallucinations

- State which library provides each non-trivial keyword pattern.
- If a keyword or library is not built in and not explicitly requested, label it as external or optional.
- Do not present unknown keywords as standard Robot Framework keywords.

## Execute with this checklist

1. Identify output type (`.robot` suite, `.resource`, or Python library file).
2. Identify required libraries (BuiltIn, OperatingSystem, RequestsLibrary, custom library).
3. Choose variable and secret handling approach.
4. Generate deterministic assertions and reusable keywords.
5. Refactor duplication into resource files.
6. Add run commands only when requested.

## References

- Robot Framework User Guide: https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html
- Standard Libraries overview: https://docs.robotframework.org/docs/different_libraries/standard
- BuiltIn library docs: https://robotframework.org/robotframework/latest/libraries/BuiltIn.html
- OperatingSystem library docs: https://robotframework.org/robotframework/latest/libraries/OperatingSystem.html
- Python library extension guide: https://docs.robotframework.org/docs/extending_robot_framework/custom-libraries/python_library
- Robot Framework API docs: https://robot-framework.readthedocs.io/
- RequestsLibrary docs: https://docs.robotframework.org/docs/different_libraries/requests
