# Azure Communication CallingServer SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-communication-callingserver` (DEPRECATED)
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/communication/azure-communication-callingserver
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## ⚠️ DEPRECATION NOTICE

**This SDK is deprecated.** For new projects, use `azure-communication-callautomation` instead.

---

## 1. Correct Migration Pattern

### 1.1 ✅ CORRECT: Migrate to Call Automation
```java
// OLD (deprecated)
import com.azure.communication.callingserver.CallingServerClient;
import com.azure.communication.callingserver.CallingServerClientBuilder;

// NEW (use this)
import com.azure.communication.callautomation.CallAutomationClient;
import com.azure.communication.callautomation.CallAutomationClientBuilder;
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using deprecated SDK for new projects
```java
// WRONG - use CallAutomationClient for new projects
CallingServerClient client = new CallingServerClientBuilder()
    .connectionString("<connection-string>")
    .buildClient();
```

---

## 2. Legacy Client Creation (for maintenance only)

### 2.1 ✅ CORRECT: Legacy Client Creation
```java
import com.azure.communication.callingserver.CallingServerClient;
import com.azure.communication.callingserver.CallingServerClientBuilder;

// Only use this for maintaining legacy code
CallingServerClient client = new CallingServerClientBuilder()
    .connectionString(System.getenv("AZURE_COMMUNICATION_CONNECTION_STRING"))
    .buildClient();
```

---

## 3. Migration Checklist

- [ ] Replace `CallingServerClient` with `CallAutomationClient`
- [ ] Replace `CallingServerClientBuilder` with `CallAutomationClientBuilder`
- [ ] Update import statements
- [ ] Review API changes in Call Automation SDK
- [ ] Test thoroughly after migration

---

## 4. Reference

For modern call automation patterns, see `azure-communication-callautomation-java` skill.
