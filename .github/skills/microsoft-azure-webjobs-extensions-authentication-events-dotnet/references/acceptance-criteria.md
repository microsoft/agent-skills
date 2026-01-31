# Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents Acceptance Criteria

**SDK**: `Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/entra/Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Core Imports
#### ✅ CORRECT: Standard authentication events imports
```csharp
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents;
using Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents.TokenIssuanceStart;
using Microsoft.Extensions.Logging;
```

#### ✅ CORRECT: Attribute collection imports
```csharp
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents;
using Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents.Framework;
using Microsoft.Extensions.Logging;
```

#### ❌ INCORRECT: Missing extension imports
```csharp
using Microsoft.Azure.WebJobs;
// Missing Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents
```

#### ❌ INCORRECT: Using non-existent namespaces
```csharp
using Microsoft.Identity.AuthenticationEvents;
using Azure.Identity.AuthenticationEvents;
```

---

## 2. Function Trigger Patterns

### 2.1 Token Issuance Start Trigger
#### ✅ CORRECT: Synchronous function signature
```csharp
[FunctionName("OnTokenIssuanceStart")]
public static WebJobsAuthenticationEventResponse Run(
    [WebJobsAuthenticationEventsTrigger] WebJobsTokenIssuanceStartRequest request,
    ILogger log)
{
    // Implementation
}
```

#### ✅ CORRECT: Async function signature
```csharp
[FunctionName("OnTokenIssuanceStartAsync")]
public static async Task<WebJobsAuthenticationEventResponse> Run(
    [WebJobsAuthenticationEventsTrigger] WebJobsTokenIssuanceStartRequest request,
    ILogger log)
{
    // Implementation
}
```

#### ❌ INCORRECT: Wrong trigger attribute
```csharp
[FunctionName("OnTokenIssuanceStart")]
public static WebJobsAuthenticationEventResponse Run(
    [HttpTrigger] HttpRequest request,  // Wrong - use WebJobsAuthenticationEventsTrigger
    ILogger log)
```

#### ❌ INCORRECT: Wrong request type
```csharp
[FunctionName("OnTokenIssuanceStart")]
public static WebJobsAuthenticationEventResponse Run(
    [WebJobsAuthenticationEventsTrigger] object request,  // Use specific request type
    ILogger log)
```

---

## 3. Token Enrichment (Add Claims)

### 3.1 Provide Claims for Token
#### ✅ CORRECT: Add custom claims
```csharp
var response = new WebJobsTokenIssuanceStartResponse();
response.Actions.Add(new WebJobsProvideClaimsForToken
{
    Claims = new Dictionary<string, string>
    {
        { "customClaim1", "value1" },
        { "department", "Engineering" },
        { "costCenter", "CC-12345" }
    }
});
return response;
```

#### ❌ INCORRECT: Not using Actions collection
```csharp
var response = new WebJobsTokenIssuanceStartResponse();
response.Claims = new Dictionary<string, string> { /* ... */ };  // Wrong property
return response;
```

#### ❌ INCORRECT: Returning wrong response type
```csharp
return new WebJobsAttributeCollectionStartResponse();  // Wrong type for token issuance
```

### 3.2 Access Request Context
#### ✅ CORRECT: Access user information from request
```csharp
string? userId = request.Data?.AuthenticationContext?.User?.Id;
string? correlationId = request.Data?.AuthenticationContext?.CorrelationId.ToString();

log.LogInformation("Processing token for user: {UserId}", userId);
```

#### ❌ INCORRECT: Not null-checking nested properties
```csharp
string userId = request.Data.AuthenticationContext.User.Id;  // May throw NullReferenceException
```

---

## 4. Attribute Collection Events

### 4.1 Attribute Collection Start
#### ✅ CORRECT: Continue with default behavior
```csharp
[FunctionName("OnAttributeCollectionStart")]
public static WebJobsAuthenticationEventResponse Run(
    [WebJobsAuthenticationEventsTrigger] WebJobsAttributeCollectionStartRequest request,
    ILogger log)
{
    var response = new WebJobsAttributeCollectionStartResponse();
    response.Actions.Add(new WebJobsContinueWithDefaultBehavior());
    return response;
}
```

#### ✅ CORRECT: Prefill attribute values
```csharp
var response = new WebJobsAttributeCollectionStartResponse();
response.Actions.Add(new WebJobsSetPrefillValues
{
    Attributes = new Dictionary<string, string>
    {
        { "city", "Seattle" },
        { "country", "USA" }
    }
});
return response;
```

#### ✅ CORRECT: Show block page
```csharp
var response = new WebJobsAttributeCollectionStartResponse();
response.Actions.Add(new WebJobsShowBlockPage
{
    Message = "Sign-up is currently disabled."
});
return response;
```

### 4.2 Attribute Collection Submit
#### ✅ CORRECT: Validate and show errors
```csharp
[FunctionName("OnAttributeCollectionSubmit")]
public static WebJobsAuthenticationEventResponse Run(
    [WebJobsAuthenticationEventsTrigger] WebJobsAttributeCollectionSubmitRequest request,
    ILogger log)
{
    var response = new WebJobsAttributeCollectionSubmitResponse();
    var attributes = request.Data?.UserSignUpInfo?.Attributes;
    
    string? displayName = attributes?["displayName"]?.ToString();
    
    if (string.IsNullOrEmpty(displayName) || displayName.Length < 3)
    {
        response.Actions.Add(new WebJobsShowValidationError
        {
            Message = "Display name must be at least 3 characters.",
            AttributeErrors = new Dictionary<string, string>
            {
                { "displayName", "Name is too short" }
            }
        });
        return response;
    }
    
    response.Actions.Add(new WebJobsContinueWithDefaultBehavior());
    return response;
}
```

#### ✅ CORRECT: Modify attribute values
```csharp
response.Actions.Add(new WebJobsModifyAttributeValues
{
    Attributes = new Dictionary<string, string>
    {
        { "displayName", displayName.Trim() },
        { "city", city?.ToUpperInvariant() ?? "" }
    }
});
```

---

## 5. Custom OTP Events

### 5.1 OTP Send Event
#### ✅ CORRECT: Handle OTP send success
```csharp
[FunctionName("OnOtpSend")]
public static async Task<WebJobsAuthenticationEventResponse> Run(
    [WebJobsAuthenticationEventsTrigger] WebJobsOnOtpSendRequest request,
    ILogger log)
{
    var response = new WebJobsOnOtpSendResponse();
    
    string? phoneNumber = request.Data?.OtpContext?.Identifier;
    string? otp = request.Data?.OtpContext?.OneTimeCode;
    
    try
    {
        await SendSmsAsync(phoneNumber, $"Your code is: {otp}");
        response.Actions.Add(new WebJobsOnOtpSendSuccess());
    }
    catch (Exception ex)
    {
        log.LogError(ex, "Failed to send OTP");
        response.Actions.Add(new WebJobsOnOtpSendFailed
        {
            Error = "Failed to send verification code"
        });
    }
    
    return response;
}
```

#### ❌ INCORRECT: Not handling both success and failure
```csharp
var response = new WebJobsOnOtpSendResponse();
await SendSmsAsync(phoneNumber, otp);
// Missing: response.Actions.Add(new WebJobsOnOtpSendSuccess())
return response;
```

---

## 6. Error Handling

### 6.1 Graceful Error Handling
#### ✅ CORRECT: Return empty response on error (don't fail auth)
```csharp
[FunctionName("OnTokenIssuanceStart")]
public static WebJobsAuthenticationEventResponse Run(
    [WebJobsAuthenticationEventsTrigger] WebJobsTokenIssuanceStartRequest request,
    ILogger log)
{
    try
    {
        var response = new WebJobsTokenIssuanceStartResponse();
        response.Actions.Add(new WebJobsProvideClaimsForToken
        {
            Claims = new Dictionary<string, string> { { "claim", "value" } }
        });
        return response;
    }
    catch (Exception ex)
    {
        log.LogError(ex, "Error processing token issuance event");
        // Return empty response - authentication continues without custom claims
        return new WebJobsTokenIssuanceStartResponse();
    }
}
```

#### ❌ INCORRECT: Throwing exceptions (fails authentication)
```csharp
try
{
    // ... logic
}
catch (Exception ex)
{
    throw;  // This will fail the entire authentication flow
}
```

---

## 7. Logging Best Practices

### 7.1 Correlation ID Logging
#### ✅ CORRECT: Log with correlation ID
```csharp
log.LogInformation("Token issuance event. CorrelationId: {CorrelationId}, UserId: {UserId}",
    request.Data?.AuthenticationContext?.CorrelationId,
    request.Data?.AuthenticationContext?.User?.Id);
```

#### ❌ INCORRECT: Not logging correlation ID
```csharp
log.LogInformation("Processing request");  // No context for troubleshooting
```

---

## 8. Request/Response Type Reference

### 8.1 Token Issuance
| Type | Purpose |
|------|---------|
| `WebJobsTokenIssuanceStartRequest` | Input request for token issuance |
| `WebJobsTokenIssuanceStartResponse` | Response with claims to add |
| `WebJobsProvideClaimsForToken` | Action to provide custom claims |

### 8.2 Attribute Collection
| Type | Purpose |
|------|---------|
| `WebJobsAttributeCollectionStartRequest` | Input for collection start |
| `WebJobsAttributeCollectionStartResponse` | Response for collection start |
| `WebJobsAttributeCollectionSubmitRequest` | Input for submission |
| `WebJobsAttributeCollectionSubmitResponse` | Response for submission |
| `WebJobsSetPrefillValues` | Action to prefill form values |
| `WebJobsShowBlockPage` | Action to block with message |
| `WebJobsShowValidationError` | Action to show validation errors |
| `WebJobsModifyAttributeValues` | Action to modify submitted values |
| `WebJobsContinueWithDefaultBehavior` | Action to continue normally |

### 8.3 OTP Events
| Type | Purpose |
|------|---------|
| `WebJobsOnOtpSendRequest` | Input for OTP send event |
| `WebJobsOnOtpSendResponse` | Response for OTP send event |
| `WebJobsOnOtpSendSuccess` | Action indicating successful send |
| `WebJobsOnOtpSendFailed` | Action indicating failed send |

---

## 9. Function App Configuration

### 9.1 host.json
#### ✅ CORRECT: Minimal host.json configuration
```json
{
  "version": "2.0",
  "extensions": {
    "http": {
      "routePrefix": ""
    }
  }
}
```

### 9.2 local.settings.json
#### ✅ CORRECT: Local development settings
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "dotnet"
  }
}
```

---

## Summary Checklist

- [ ] Uses `WebJobsAuthenticationEventsTrigger` attribute
- [ ] Uses correct request type for each event (e.g., `WebJobsTokenIssuanceStartRequest`)
- [ ] Uses correct response type for each event
- [ ] Adds actions to `response.Actions` collection
- [ ] Handles errors gracefully (returns empty response, doesn't throw)
- [ ] Logs correlation ID for troubleshooting
- [ ] Uses null-conditional operators for nested property access
- [ ] For OTP events, handles both success and failure cases
- [ ] For validation, uses `WebJobsShowValidationError` with `AttributeErrors`
- [ ] Function name follows event naming convention (e.g., "OnTokenIssuanceStart")
