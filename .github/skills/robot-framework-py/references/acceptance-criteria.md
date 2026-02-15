# Acceptance Criteria: robot-framework-py

## Robot Framework Section Syntax

### Correct

```robotframework
*** Settings ***
```

```robotframework
*** Test Cases ***
```

```robotframework
*** Keywords ***
```

```robotframework
*** Variables ***
```

### Incorrect

```robotframework
*** Setting ***
```

```robotframework
*** TestCase ***
```

## BuiltIn Assertion Patterns

### Correct

```robotframework
Should Be Equal
```

```robotframework
Should Be Equal As Integers
```

```robotframework
Should Not Be Empty
```

### Incorrect

```robotframework
assert response.status_code == 200
```

```robotframework
assert actual == expected
```

## RequestsLibrary API Flow

### Correct

```robotframework
Library    RequestsLibrary
```

```robotframework
Create Session
```

```robotframework
GET On Session
```

```robotframework
POST On Session
```

### Incorrect

```python
requests.get(
```

```python
requests.post(
```

```bash
curl https://
```

## Reuse and Resource Layering

### Correct

```robotframework
Resource    ../resources/common.resource
```

```robotframework
Open API Session
```

### Incorrect

```text
TODO
```

```text
FIXME
```

## Python Keyword Libraries

### Correct

```python
from robot.api.deco import keyword
```

```python
@keyword("Normalize Text")
```

```python
@keyword("Add Integers")
```

```python
class MathKeywords:
```

### Incorrect

```python
print(
```

```python
input(
```

```python
eval(
```

## OperatingSystem Library Usage

### Correct

```robotframework
Library    OperatingSystem
```

```robotframework
Get Environment Variable
```

```robotframework
File Should Exist
```

### Incorrect

```python
os.environ
```

```python
pathlib.Path(
```

## Security Hygiene

### Correct

```robotframework
${token}=    Get Environment Variable    API_TOKEN
```

### Incorrect

```text
password=
```

```text
secret=
```
