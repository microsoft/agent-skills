# GitHub Issue Creator Acceptance Criteria

**Tool**: GitHub Issue Creator Skill
**Purpose**: Skill testing acceptance criteria for validating generated issue reports

---

## 1. Issue Structure

### 1.1 Required Sections

#### ✅ CORRECT: Complete Issue Structure
```markdown
## Summary
[One-line description of the issue]

## Environment
- **Product/Service**: 
- **Region/Version**: 
- **Browser/OS**: (if relevant)

## Reproduction Steps
1. [Step]
2. [Step]
3. [Step]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Error Details
```
[Error message/code if applicable]
```

## Visual Evidence
[Reference to attached screenshots/GIFs]

## Impact
[Severity: Critical/High/Medium/Low + brief explanation]

## Additional Context
[Any other relevant details]
```

#### ❌ INCORRECT: Missing key sections
```markdown
## Bug Report

Something is broken. Please fix.
```

---

## 2. Summary Section

### 2.1 Summary Quality

#### ✅ CORRECT: Concise and specific
```markdown
## Summary
Agent deployment fails silently - no error displayed, agent disappears from list
```

#### ✅ CORRECT: Action-oriented
```markdown
## Summary
403 PERMISSION_DENIED error when publishing to Teams channel
```

#### ❌ INCORRECT: Vague or verbose
```markdown
## Summary
There's a problem with the system and it's not working properly when I try to do things
```

---

## 3. Environment Section

### 3.1 Environment Details

#### ✅ CORRECT: Specific environment details
```markdown
## Environment
- **Product/Service**: Azure AI Foundry
- **Region/Version**: westus2 / v2.1.0
- **Browser/OS**: Chrome 120 / Windows 11
```

#### ✅ CORRECT: Placeholder for sensitive data
```markdown
## Environment
- **Product/Service**: [PROJECT_NAME]
- **Subscription**: [SUBSCRIPTION_ID]
```

#### ❌ INCORRECT: No environment context
```markdown
## Environment
- N/A
```

---

## 4. Reproduction Steps

### 4.1 Step Quality

#### ✅ CORRECT: Clear numbered steps
```markdown
## Reproduction Steps
1. Navigate to agent deployment page
2. Configure agent with default settings
3. Click "Deploy" button
4. Observe workflow completes
5. Check agent list
```

#### ❌ INCORRECT: Unclear or missing steps
```markdown
## Reproduction Steps
Just try to deploy and you'll see
```

---

## 5. Error Details

### 5.1 Error Formatting

#### ✅ CORRECT: Formatted error with code block
```markdown
## Error Details
```
Error: PERMISSION_DENIED
Code: 403
RequestId: abc123-def456
Timestamp: 2024-01-15T10:30:00Z
```
```

#### ✅ CORRECT: Stack trace in code block
```markdown
## Error Details
```python
Traceback (most recent call last):
  File "main.py", line 42, in process
    result = client.deploy(config)
  File "client.py", line 156, in deploy
    raise DeploymentError("Insufficient permissions")
DeploymentError: Insufficient permissions
```
```

#### ❌ INCORRECT: Unformatted error
```markdown
## Error Details
Error: PERMISSION_DENIED Code: 403 RequestId: abc123
```

---

## 6. Impact Assessment

### 6.1 Severity Levels

#### ✅ CORRECT: Critical severity
```markdown
## Impact
**Critical** - Service completely down, affecting all users, data loss possible
```

#### ✅ CORRECT: High severity
```markdown
## Impact
**High** - Major feature broken, no workaround available, blocks user workflow
```

#### ✅ CORRECT: Medium severity
```markdown
## Impact
**Medium** - Feature impaired but workaround exists, affects some users
```

#### ✅ CORRECT: Low severity
```markdown
## Impact
**Low** - Minor cosmetic issue, does not affect functionality
```

#### ❌ INCORRECT: No severity assessment
```markdown
## Impact
This is a bug
```

---

## 7. Visual Evidence

### 7.1 Image References

#### ✅ CORRECT: Inline image reference
```markdown
## Visual Evidence
![Error dialog showing permission denied](./screenshots/error-dialog.png)
![Network tab showing 403 response](./screenshots/network-403.png)
```

#### ✅ CORRECT: GIF for reproduction
```markdown
## Visual Evidence
![Reproduction steps animation](./recordings/repro-steps.gif)
```

#### ❌ INCORRECT: Missing alt text
```markdown
## Visual Evidence
![](screenshot.png)
```

---

## 8. File Naming

### 8.1 Issue File Names

#### ✅ CORRECT: Date-prefixed descriptive name
```
/issues/2024-01-15-agent-deployment-silent-failure.md
/issues/2024-01-15-teams-publish-403-error.md
```

#### ❌ INCORRECT: Non-descriptive names
```
/issues/bug.md
/issues/issue1.md
```
