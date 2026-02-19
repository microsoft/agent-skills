# Azure Communication SMS Java SDK - Examples

Comprehensive code examples for the Azure Communication Services SMS SDK for Java.

## Table of Contents
- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Send Single SMS](#send-single-sms)
- [Send Bulk SMS](#send-bulk-sms)
- [Delivery Reports](#delivery-reports)
- [Async Operations](#async-operations)
- [Error Handling](#error-handling)
- [Complete Application Example](#complete-application-example)

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-communication-sms</artifactId>
    <version>1.2.0</version>
</dependency>
```

## Client Creation

### With DefaultAzureCredential (Recommended)

```java
import com.azure.communication.sms.SmsClient;
import com.azure.communication.sms.SmsClientBuilder;
import com.azure.identity.DefaultAzureCredentialBuilder;

SmsClient smsClient = new SmsClientBuilder()
    .endpoint("https://<resource>.communication.azure.com")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### With Connection String

```java
SmsClient smsClient = new SmsClientBuilder()
    .connectionString(System.getenv("AZURE_COMMUNICATION_CONNECTION_STRING"))
    .buildClient();
```

### With AzureKeyCredential

```java
import com.azure.core.credential.AzureKeyCredential;

SmsClient smsClient = new SmsClientBuilder()
    .endpoint("https://<resource>.communication.azure.com")
    .credential(new AzureKeyCredential("<access-key>"))
    .buildClient();
```

### Async Client

```java
import com.azure.communication.sms.SmsAsyncClient;

SmsAsyncClient asyncClient = new SmsClientBuilder()
    .connectionString(connectionString)
    .buildAsyncClient();
```

## Send Single SMS

### Simple Send

```java
import com.azure.communication.sms.models.SmsSendResult;

SmsSendResult result = smsClient.send(
    "+14255550100",      // From (your ACS phone number)
    "+14255551234",      // To
    "Your verification code is 123456"
);

System.out.println("Message ID: " + result.getMessageId());
System.out.println("Success: " + result.isSuccessful());
```

### Send with Options

```java
import com.azure.communication.sms.models.SmsSendOptions;
import com.azure.core.util.Context;
import java.util.Collections;

SmsSendOptions options = new SmsSendOptions()
    .setDeliveryReportEnabled(true)
    .setTag("verification-code");

SmsSendResult result = smsClient.sendWithResponse(
    "+14255550100",
    Collections.singletonList("+14255551234"),
    "Your verification code is 123456",
    options,
    Context.NONE
).getValue().iterator().next();
```

## Send Bulk SMS

### Send to Multiple Recipients

```java
import java.util.Arrays;
import java.util.List;

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

// Process results for each recipient
for (SmsSendResult result : results) {
    if (result.isSuccessful()) {
        System.out.printf("✓ Sent to %s: %s%n", result.getTo(), result.getMessageId());
    } else {
        System.out.printf("✗ Failed to %s: %s (HTTP %d)%n", 
            result.getTo(), 
            result.getErrorMessage(),
            result.getHttpStatusCode());
    }
}
```

### Batch SMS with Retry Logic

```java
import java.util.ArrayList;
import java.util.List;

public class SmsBatchSender {
    private final SmsClient smsClient;
    private final String fromNumber;
    
    public SmsBatchSender(SmsClient smsClient, String fromNumber) {
        this.smsClient = smsClient;
        this.fromNumber = fromNumber;
    }
    
    public List<SmsSendResult> sendBatch(List<String> recipients, String message) {
        List<SmsSendResult> allResults = new ArrayList<>();
        List<String> failedRecipients = new ArrayList<>();
        
        SmsSendOptions options = new SmsSendOptions()
            .setDeliveryReportEnabled(true);
        
        // First attempt
        Iterable<SmsSendResult> results = smsClient.sendWithResponse(
            fromNumber, recipients, message, options, Context.NONE
        ).getValue();
        
        for (SmsSendResult result : results) {
            allResults.add(result);
            if (!result.isSuccessful() && result.getHttpStatusCode() == 429) {
                failedRecipients.add(result.getTo());
            }
        }
        
        // Retry rate-limited messages after delay
        if (!failedRecipients.isEmpty()) {
            try {
                Thread.sleep(2000); // Wait 2 seconds
                Iterable<SmsSendResult> retryResults = smsClient.sendWithResponse(
                    fromNumber, failedRecipients, message, options, Context.NONE
                ).getValue();
                
                for (SmsSendResult result : retryResults) {
                    allResults.add(result);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        
        return allResults;
    }
}
```

## Delivery Reports

Delivery reports are sent via Azure Event Grid. Configure an Event Grid subscription for your ACS resource.

### Event Grid Webhook Handler

```java
import com.azure.messaging.eventgrid.EventGridEvent;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

public class SmsDeliveryReportHandler {
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    public void handleDeliveryReport(String eventJson) throws Exception {
        List<EventGridEvent> events = EventGridEvent.fromString(eventJson);
        
        for (EventGridEvent event : events) {
            if ("Microsoft.Communication.SMSDeliveryReportReceived".equals(event.getEventType())) {
                JsonNode data = objectMapper.readTree(event.getData().toString());
                
                String messageId = data.get("messageId").asText();
                String from = data.get("from").asText();
                String to = data.get("to").asText();
                String deliveryStatus = data.get("deliveryStatus").asText();
                String deliveryStatusDetails = data.get("deliveryStatusDetails").asText();
                String tag = data.has("tag") ? data.get("tag").asText() : null;
                
                System.out.printf("Delivery Report - MessageId: %s, To: %s, Status: %s%n",
                    messageId, to, deliveryStatus);
                
                // Update your database or trigger actions based on status
                switch (deliveryStatus) {
                    case "Delivered":
                        onMessageDelivered(messageId, to, tag);
                        break;
                    case "Failed":
                        onMessageFailed(messageId, to, deliveryStatusDetails, tag);
                        break;
                }
            }
        }
    }
    
    private void onMessageDelivered(String messageId, String to, String tag) {
        System.out.printf("Message %s delivered to %s (tag: %s)%n", messageId, to, tag);
    }
    
    private void onMessageFailed(String messageId, String to, String reason, String tag) {
        System.out.printf("Message %s failed to %s: %s (tag: %s)%n", 
            messageId, to, reason, tag);
    }
}
```

## Async Operations

### Async Send Single Message

```java
import reactor.core.publisher.Mono;

SmsAsyncClient asyncClient = new SmsClientBuilder()
    .connectionString(connectionString)
    .buildAsyncClient();

asyncClient.send("+14255550100", "+14255551234", "Async message!")
    .subscribe(
        result -> {
            System.out.println("Sent: " + result.getMessageId());
            System.out.println("Success: " + result.isSuccessful());
        },
        error -> System.err.println("Error: " + error.getMessage())
    );
```

### Async Bulk Send with Reactive Streams

```java
import reactor.core.publisher.Flux;

SmsSendOptions options = new SmsSendOptions()
    .setDeliveryReportEnabled(true);

asyncClient.sendWithResponse(
    "+14255550100",
    Arrays.asList("+14255551111", "+14255552222"),
    "Bulk async message",
    options)
    .flatMapMany(response -> Flux.fromIterable(response.getValue()))
    .subscribe(
        result -> {
            if (result.isSuccessful()) {
                System.out.printf("✓ %s: %s%n", result.getTo(), result.getMessageId());
            } else {
                System.out.printf("✗ %s: %s%n", result.getTo(), result.getErrorMessage());
            }
        },
        error -> System.err.println("Error: " + error.getMessage()),
        () -> System.out.println("All messages processed")
    );
```

## Error Handling

### Comprehensive Error Handling

```java
import com.azure.core.exception.HttpResponseException;

public class SmsService {
    private final SmsClient smsClient;
    private final String fromNumber;
    
    public SmsService(SmsClient smsClient, String fromNumber) {
        this.smsClient = smsClient;
        this.fromNumber = fromNumber;
    }
    
    public SmsSendResult sendSms(String to, String message) {
        try {
            SmsSendResult result = smsClient.send(fromNumber, to, message);
            
            if (!result.isSuccessful()) {
                handleMessageError(result);
            }
            
            return result;
            
        } catch (HttpResponseException e) {
            // Request-level failures (auth, network, etc.)
            System.err.printf("HTTP Error %d: %s%n", 
                e.getResponse().getStatusCode(), e.getMessage());
            throw new RuntimeException("Failed to send SMS", e);
        } catch (RuntimeException e) {
            System.err.println("Unexpected error: " + e.getMessage());
            throw e;
        }
    }
    
    private void handleMessageError(SmsSendResult result) {
        int status = result.getHttpStatusCode();
        String to = result.getTo();
        String error = result.getErrorMessage();
        
        switch (status) {
            case 400:
                System.err.printf("Invalid phone number: %s%n", to);
                break;
            case 401:
                System.err.println("Authentication failed - check credentials");
                break;
            case 403:
                System.err.printf("Not authorized to send to: %s%n", to);
                break;
            case 429:
                System.err.println("Rate limited - implement backoff retry");
                break;
            default:
                System.err.printf("Error %d sending to %s: %s%n", status, to, error);
        }
    }
}
```

## Complete Application Example

### OTP SMS Service

```java
import com.azure.communication.sms.SmsClient;
import com.azure.communication.sms.SmsClientBuilder;
import com.azure.communication.sms.models.SmsSendOptions;
import com.azure.communication.sms.models.SmsSendResult;
import com.azure.core.util.Context;
import java.security.SecureRandom;
import java.util.Collections;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class OtpSmsService {
    private final SmsClient smsClient;
    private final String fromNumber;
    private final Map<String, OtpEntry> otpStore = new ConcurrentHashMap<>();
    private final SecureRandom random = new SecureRandom();
    
    public OtpSmsService(String connectionString, String fromNumber) {
        this.smsClient = new SmsClientBuilder()
            .connectionString(connectionString)
            .buildClient();
        this.fromNumber = fromNumber;
    }
    
    public String sendOtp(String phoneNumber) {
        // Generate 6-digit OTP
        String otp = String.format("%06d", random.nextInt(1000000));
        
        // Store OTP with expiry
        otpStore.put(phoneNumber, new OtpEntry(otp, System.currentTimeMillis() + 300000));
        
        // Send SMS
        String message = String.format("Your verification code is %s. Valid for 5 minutes.", otp);
        
        SmsSendOptions options = new SmsSendOptions()
            .setDeliveryReportEnabled(true)
            .setTag("otp-" + phoneNumber);
        
        SmsSendResult result = smsClient.sendWithResponse(
            fromNumber,
            Collections.singletonList(phoneNumber),
            message,
            options,
            Context.NONE
        ).getValue().iterator().next();
        
        if (result.isSuccessful()) {
            System.out.printf("OTP sent to %s: %s%n", phoneNumber, result.getMessageId());
            return result.getMessageId();
        } else {
            throw new RuntimeException("Failed to send OTP: " + result.getErrorMessage());
        }
    }
    
    public boolean verifyOtp(String phoneNumber, String otp) {
        OtpEntry entry = otpStore.get(phoneNumber);
        
        if (entry == null) {
            return false;
        }
        
        if (System.currentTimeMillis() > entry.expiryTime) {
            otpStore.remove(phoneNumber);
            return false;
        }
        
        if (entry.otp.equals(otp)) {
            otpStore.remove(phoneNumber);
            return true;
        }
        
        return false;
    }
    
    private static class OtpEntry {
        final String otp;
        final long expiryTime;
        
        OtpEntry(String otp, long expiryTime) {
            this.otp = otp;
            this.expiryTime = expiryTime;
        }
    }
}
```

### Usage

```java
public class Main {
    public static void main(String[] args) {
        String connectionString = System.getenv("AZURE_COMMUNICATION_CONNECTION_STRING");
        String fromNumber = System.getenv("SMS_FROM_NUMBER");
        
        OtpSmsService otpService = new OtpSmsService(connectionString, fromNumber);
        
        // Send OTP
        String messageId = otpService.sendOtp("+14255551234");
        System.out.println("OTP sent with message ID: " + messageId);
        
        // Verify OTP (user enters code)
        boolean verified = otpService.verifyOtp("+14255551234", "123456");
        System.out.println("OTP verified: " + verified);
    }
}
```

## Environment Variables

```bash
AZURE_COMMUNICATION_ENDPOINT=https://<resource>.communication.azure.com
AZURE_COMMUNICATION_CONNECTION_STRING=endpoint=https://...;accesskey=...
SMS_FROM_NUMBER=+14255550100
```

## Best Practices

1. **Phone Number Format** - Use E.164 format: `+[country code][number]`
2. **Delivery Reports** - Enable for critical messages (OTP, alerts)
3. **Tagging** - Use tags to correlate messages with business context
4. **Error Handling** - Check `isSuccessful()` for each recipient individually
5. **Rate Limiting** - Implement retry with exponential backoff for 429 responses
6. **Bulk Sending** - Use batch send for multiple recipients (more efficient)
7. **Connection Reuse** - Reuse `SmsClient` instances across requests
