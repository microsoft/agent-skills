# Azure Communication SMS SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-communication-sms`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/communication/azure-communication-sms
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Client and Builder
```java
import com.azure.communication.sms.SmsClient;
import com.azure.communication.sms.SmsClientBuilder;
import com.azure.communication.sms.SmsAsyncClient;
```

#### ✅ CORRECT: Authentication
```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.core.credential.AzureKeyCredential;
```

### 1.2 Model Imports

#### ✅ CORRECT: SMS Models
```java
import com.azure.communication.sms.models.SmsSendResult;
import com.azure.communication.sms.models.SmsSendOptions;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Builder with DefaultAzureCredential
```java
String endpoint = System.getenv("AZURE_COMMUNICATION_ENDPOINT");

SmsClient smsClient = new SmsClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### 2.2 ✅ CORRECT: Builder with Connection String
```java
String connectionString = System.getenv("AZURE_COMMUNICATION_CONNECTION_STRING");

SmsClient smsClient = new SmsClientBuilder()
    .connectionString(connectionString)
    .buildClient();
```

### 2.3 ✅ CORRECT: Async Client
```java
SmsAsyncClient smsAsyncClient = new SmsClientBuilder()
    .connectionString(connectionString)
    .buildAsyncClient();
```

### 2.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials
```java
// WRONG - hardcoded values
SmsClient smsClient = new SmsClientBuilder()
    .connectionString("endpoint=https://...;accesskey=...")
    .buildClient();
```

---

## 3. Send SMS Patterns

### 3.1 ✅ CORRECT: Send to Single Recipient
```java
SmsSendResult result = smsClient.send(
    "+14255550100",      // From (your ACS phone number)
    "+14255551234",      // To
    "Your verification code is 123456");

System.out.println("Message ID: " + result.getMessageId());
System.out.println("Success: " + result.isSuccessful());
```

### 3.2 ✅ CORRECT: Send to Multiple Recipients with Options
```java
List<String> recipients = Arrays.asList(
    "+14255551111",
    "+14255552222",
    "+14255553333"
);

SmsSendOptions options = new SmsSendOptions()
    .setDeliveryReportEnabled(true)
    .setTag("marketing-campaign-001");

Iterable<SmsSendResult> results = smsClient.sendWithResponse(
    "+14255550100",
    recipients,
    "Flash sale! 50% off today only.",
    options,
    Context.NONE
).getValue();

for (SmsSendResult result : results) {
    if (result.isSuccessful()) {
        System.out.println("Sent to " + result.getTo() + ": " + result.getMessageId());
    } else {
        System.out.println("Failed to " + result.getTo() + ": " + result.getErrorMessage());
    }
}
```

### 3.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded phone numbers
```java
// WRONG - hardcoded phone numbers
SmsSendResult result = smsClient.send(
    "+14255550100",
    "+14255551234",
    "message");
```

---

## 4. Error Handling

### 4.1 ✅ CORRECT: Handle Per-Recipient Errors
```java
SmsSendResult result = smsClient.send(from, to, message);

if (!result.isSuccessful()) {
    int status = result.getHttpStatusCode();
    String error = result.getErrorMessage();
    
    if (status == 400) {
        System.out.println("Invalid phone number: " + result.getTo());
    } else if (status == 429) {
        System.out.println("Rate limited - retry later");
    } else {
        System.out.println("Error " + status + ": " + error);
    }
}
```

### 4.2 ✅ CORRECT: HTTP Exception Handling
```java
import com.azure.core.exception.HttpResponseException;

try {
    SmsSendResult result = smsClient.send(from, to, message);
} catch (HttpResponseException e) {
    System.out.println("Request failed: " + e.getMessage());
    System.out.println("Status: " + e.getResponse().getStatusCode());
}
```

---

## 5. Best Practices Checklist

- [ ] Use E.164 format for phone numbers: `+[country code][number]`
- [ ] Use environment variables for credentials and phone numbers
- [ ] Enable delivery reports for critical messages
- [ ] Use tags to correlate messages with business context
- [ ] Check `isSuccessful()` for each recipient individually
- [ ] Implement retry with backoff for 429 responses
- [ ] Use batch send for multiple recipients (more efficient)
