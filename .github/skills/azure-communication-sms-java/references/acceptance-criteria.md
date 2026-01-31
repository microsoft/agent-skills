# Azure Communication SMS Acceptance Criteria

**SDK**: `com.azure:azure-communication-sms`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/communication/azure-communication-sms
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Full qualified client imports
```java
import com.azure.communication.sms.SmsClient;
import com.azure.communication.sms.SmsClientBuilder;
import com.azure.communication.sms.SmsAsyncClient;
```

#### ❌ INCORRECT: Wrong package imports
```java
import com.azure.communication.messaging.SmsClient;
```

### 1.2 Model Imports
#### ✅ CORRECT: Models from sms.models package
```java
import com.azure.communication.sms.models.SmsSendResult;
import com.azure.communication.sms.models.SmsSendOptions;
```

### 1.3 Credential Imports
#### ✅ CORRECT: Authentication credentials
```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.core.credential.AzureKeyCredential;
```

---

## 2. Client Creation Patterns

### 2.1 With DefaultAzureCredential
#### ✅ CORRECT: Recommended authentication
```java
SmsClient smsClient = new SmsClientBuilder()
    .endpoint("https://<resource>.communication.azure.com")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### 2.2 With Connection String
#### ✅ CORRECT: Connection string authentication
```java
SmsClient smsClient = new SmsClientBuilder()
    .connectionString("<connection-string>")
    .buildClient();
```

### 2.3 With AzureKeyCredential
#### ✅ CORRECT: Key-based authentication
```java
SmsClient smsClient = new SmsClientBuilder()
    .endpoint("https://<resource>.communication.azure.com")
    .credential(new AzureKeyCredential("<access-key>"))
    .buildClient();
```

### 2.4 Async Client
#### ✅ CORRECT: Async client creation
```java
SmsAsyncClient smsAsyncClient = new SmsClientBuilder()
    .connectionString("<connection-string>")
    .buildAsyncClient();
```

#### ❌ INCORRECT: Missing endpoint or credential
```java
SmsClient smsClient = new SmsClientBuilder()
    .buildClient();
```

---

## 3. Send SMS Patterns

### 3.1 Single Recipient
#### ✅ CORRECT: Simple send
```java
SmsSendResult result = smsClient.send(
    "+14255550100",      // From (your ACS phone number)
    "+14255551234",      // To
    "Your verification code is 123456");

System.out.println("Message ID: " + result.getMessageId());
System.out.println("Success: " + result.isSuccessful());
```

#### ❌ INCORRECT: Non-E.164 format
```java
SmsSendResult result = smsClient.send(
    "4255550100",        // Missing + and country code
    "4255551234",
    "Message");
```

### 3.2 Multiple Recipients
#### ✅ CORRECT: Batch send with options
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
```

---

## 4. SmsSendOptions Configuration

### 4.1 Enable Delivery Reports
#### ✅ CORRECT: Full options setup
```java
SmsSendOptions options = new SmsSendOptions()
    .setDeliveryReportEnabled(true)
    .setTag("order-confirmation-12345");
```

#### ❌ INCORRECT: Missing options for critical messages
```java
// For OTP or critical messages, should enable delivery reports
smsClient.send(from, to, "Your OTP is 123456");
```

---

## 5. Response Handling

### 5.1 Check Individual Results
#### ✅ CORRECT: Iterate and check each result
```java
for (SmsSendResult result : results) {
    if (result.isSuccessful()) {
        System.out.println("Sent to " + result.getTo() + ": " + result.getMessageId());
    } else {
        System.out.println("Failed to " + result.getTo() + ": " + result.getErrorMessage());
    }
}
```

#### ❌ INCORRECT: Not checking individual results
```java
Iterable<SmsSendResult> results = smsClient.sendWithResponse(...).getValue();
// Must check isSuccessful() for each result
```

### 5.2 Full Response Handling
#### ✅ CORRECT: With HTTP response details
```java
Response<Iterable<SmsSendResult>> response = smsClient.sendWithResponse(
    "+14255550100",
    Arrays.asList("+14255551234"),
    "Hello!",
    new SmsSendOptions().setDeliveryReportEnabled(true),
    Context.NONE
);

System.out.println("Status code: " + response.getStatusCode());

for (SmsSendResult result : response.getValue()) {
    System.out.println("Message ID: " + result.getMessageId());
    System.out.println("Successful: " + result.isSuccessful());
    
    if (!result.isSuccessful()) {
        System.out.println("HTTP Status: " + result.getHttpStatusCode());
        System.out.println("Error: " + result.getErrorMessage());
    }
}
```

---

## 6. Async Operations

### 6.1 Single Async Send
#### ✅ CORRECT: Reactive async send
```java
asyncClient.send("+14255550100", "+14255551234", "Async message!")
    .subscribe(
        result -> System.out.println("Sent: " + result.getMessageId()),
        error -> System.out.println("Error: " + error.getMessage())
    );
```

### 6.2 Batch Async Send
#### ✅ CORRECT: Async batch with options
```java
SmsSendOptions options = new SmsSendOptions()
    .setDeliveryReportEnabled(true);

asyncClient.sendWithResponse(
    "+14255550100",
    Arrays.asList("+14255551111", "+14255552222"),
    "Bulk async message",
    options)
    .subscribe(response -> {
        for (SmsSendResult result : response.getValue()) {
            System.out.println("Result: " + result.getTo() + " - " + result.isSuccessful());
        }
    });
```

---

## 7. Error Handling

### 7.1 Request-Level Errors
#### ✅ CORRECT: HttpResponseException handling
```java
try {
    SmsSendResult result = smsClient.send(from, to, message);
    
    if (!result.isSuccessful()) {
        handleMessageError(result);
    }
    
} catch (HttpResponseException e) {
    System.out.println("Request failed: " + e.getMessage());
    System.out.println("Status: " + e.getResponse().getStatusCode());
}
```

### 7.2 Message-Level Errors
#### ✅ CORRECT: Status code handling
```java
private void handleMessageError(SmsSendResult result) {
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

#### ❌ INCORRECT: Catching generic exception
```java
try {
    smsClient.send(from, to, message);
} catch (Exception e) {
    // Too broad
}
```

---

## 8. SmsSendResult Properties

### 8.1 Property Access
#### ✅ CORRECT: Using all properties
```java
SmsSendResult result = smsClient.send(from, to, message);

String messageId = result.getMessageId();
String recipient = result.getTo();
boolean success = result.isSuccessful();
int httpStatus = result.getHttpStatusCode();
String errorMessage = result.getErrorMessage();
RepeatabilityResult repeatability = result.getRepeatabilityResult();
```

---

## 9. Phone Number Format

### 9.1 E.164 Format
#### ✅ CORRECT: International format
```java
// US number
PhoneNumberIdentifier phone = new PhoneNumberIdentifier("+14255551234");

// UK number
PhoneNumberIdentifier ukPhone = new PhoneNumberIdentifier("+442071234567");
```

#### ❌ INCORRECT: Local format
```java
// Missing country code
PhoneNumberIdentifier phone = new PhoneNumberIdentifier("4255551234");

// Missing +
PhoneNumberIdentifier phone = new PhoneNumberIdentifier("14255551234");
```

---

## 10. Required Dependencies

### 10.1 Maven Configuration
#### ✅ CORRECT: Current version
```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-communication-sms</artifactId>
    <version>1.2.0</version>
</dependency>
```

---

## 11. Environment Variables

### 11.1 Required Variables
```bash
AZURE_COMMUNICATION_ENDPOINT=https://<resource>.communication.azure.com
AZURE_COMMUNICATION_CONNECTION_STRING=endpoint=https://...;accesskey=...
SMS_FROM_NUMBER=+14255550100
```

---

## 12. Best Practices

### 12.1 Message Sending
- Use E.164 format for all phone numbers: `+[country code][number]`
- Enable delivery reports for critical messages (OTP, alerts)
- Use tags to correlate messages with business context

### 12.2 Error Handling
- Check `isSuccessful()` for each recipient individually
- Implement retry with backoff for 429 (rate limit) responses
- Use batch send for multiple recipients (more efficient)

### 12.3 Performance
- Batch sending is more efficient than individual sends
- Use async client for high-throughput scenarios
- Configure appropriate timeouts for your use case
