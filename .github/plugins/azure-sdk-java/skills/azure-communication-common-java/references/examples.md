# Azure Communication Common Java SDK - Examples

Comprehensive code examples for the Azure Communication Services Common SDK for Java.

## Table of Contents
- [Maven Dependency](#maven-dependency)
- [Communication Token Credential](#communication-token-credential)
- [Communication Identifiers](#communication-identifiers)
- [Token Refresh Patterns](#token-refresh-patterns)
- [Entra ID Authentication](#entra-id-authentication)
- [Complete Application Example](#complete-application-example)

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-communication-common</artifactId>
    <version>1.4.0</version>
</dependency>
```

## Communication Token Credential

### Static Token (Short-lived Clients)

```java
import com.azure.communication.common.CommunicationTokenCredential;

String userToken = "<user-access-token>";
CommunicationTokenCredential credential = new CommunicationTokenCredential(userToken);
```

### Proactive Token Refresh (Long-lived Clients)

```java
import com.azure.communication.common.CommunicationTokenRefreshOptions;
import java.util.concurrent.Callable;

Callable<String> tokenRefresher = () -> {
    // Call your server to get a fresh token
    return fetchNewTokenFromServer();
};

CommunicationTokenRefreshOptions refreshOptions = new CommunicationTokenRefreshOptions(tokenRefresher)
    .setRefreshProactively(true)
    .setInitialToken(currentToken);

CommunicationTokenCredential credential = new CommunicationTokenCredential(refreshOptions);
```

### Token Refresh with HTTP Client

```java
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.URI;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

public class TokenService {
    private final HttpClient httpClient = HttpClient.newHttpClient();
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final String tokenEndpoint;
    private final String userId;
    
    public TokenService(String tokenEndpoint, String userId) {
        this.tokenEndpoint = tokenEndpoint;
        this.userId = userId;
    }
    
    public String fetchToken() throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(tokenEndpoint + "/api/token?userId=" + userId))
            .GET()
            .build();
        
        HttpResponse<String> response = httpClient.send(request, 
            HttpResponse.BodyHandlers.ofString());
        
        if (response.statusCode() == 200) {
            JsonNode json = objectMapper.readTree(response.body());
            return json.get("token").asText();
        }
        throw new RuntimeException("Failed to fetch token: " + response.statusCode());
    }
    
    public CommunicationTokenCredential createCredential(String initialToken) {
        CommunicationTokenRefreshOptions options = new CommunicationTokenRefreshOptions(this::fetchToken)
            .setRefreshProactively(true)
            .setInitialToken(initialToken);
        
        return new CommunicationTokenCredential(options);
    }
}
```

## Communication Identifiers

### CommunicationUserIdentifier

```java
import com.azure.communication.common.CommunicationUserIdentifier;

// Create identifier for ACS user
CommunicationUserIdentifier user = new CommunicationUserIdentifier("8:acs:resource-id_user-id");
String rawId = user.getId();
```

### PhoneNumberIdentifier

```java
import com.azure.communication.common.PhoneNumberIdentifier;

// E.164 format
PhoneNumberIdentifier phone = new PhoneNumberIdentifier("+14255551234");
String phoneNumber = phone.getPhoneNumber();  // "+14255551234"
String rawId = phone.getRawId();              // "4:+14255551234"
```

### MicrosoftTeamsUserIdentifier

```java
import com.azure.communication.common.MicrosoftTeamsUserIdentifier;
import com.azure.communication.common.CommunicationCloudEnvironment;

// Teams user
MicrosoftTeamsUserIdentifier teamsUser = new MicrosoftTeamsUserIdentifier("<teams-user-id>")
    .setCloudEnvironment(CommunicationCloudEnvironment.PUBLIC);

// Anonymous Teams user
MicrosoftTeamsUserIdentifier anonymousTeamsUser = new MicrosoftTeamsUserIdentifier("<teams-user-id>")
    .setAnonymous(true);
```

### Identifier Parsing

```java
import com.azure.communication.common.*;

public class IdentifierParser {
    
    public CommunicationIdentifier parseIdentifier(String rawId) {
        if (rawId.startsWith("8:acs:")) {
            return new CommunicationUserIdentifier(rawId);
        } else if (rawId.startsWith("4:")) {
            String phone = rawId.substring(2);
            return new PhoneNumberIdentifier(phone);
        } else if (rawId.startsWith("8:orgid:")) {
            String teamsId = rawId.substring(8);
            return new MicrosoftTeamsUserIdentifier(teamsId);
        } else {
            return new UnknownIdentifier(rawId);
        }
    }
    
    public void processIdentifier(CommunicationIdentifier identifier) {
        if (identifier instanceof CommunicationUserIdentifier) {
            CommunicationUserIdentifier user = (CommunicationUserIdentifier) identifier;
            System.out.println("ACS User: " + user.getId());
            
        } else if (identifier instanceof PhoneNumberIdentifier) {
            PhoneNumberIdentifier phone = (PhoneNumberIdentifier) identifier;
            System.out.println("Phone: " + phone.getPhoneNumber());
            
        } else if (identifier instanceof MicrosoftTeamsUserIdentifier) {
            MicrosoftTeamsUserIdentifier teams = (MicrosoftTeamsUserIdentifier) identifier;
            System.out.println("Teams User: " + teams.getUserId());
            System.out.println("Anonymous: " + teams.isAnonymous());
            
        } else if (identifier instanceof UnknownIdentifier) {
            UnknownIdentifier unknown = (UnknownIdentifier) identifier;
            System.out.println("Unknown: " + unknown.getId());
        }
    }
}
```

## Token Refresh Patterns

### Async Token Refresh

```java
import java.util.concurrent.CompletableFuture;

public class AsyncTokenService {
    
    public CompletableFuture<String> fetchTokenAsync() {
        return CompletableFuture.supplyAsync(() -> {
            try {
                // Simulate async HTTP call
                Thread.sleep(100);
                return "new-token-value";
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new RuntimeException(e);
            }
        });
    }
    
    public CommunicationTokenCredential createCredential() {
        Callable<String> asyncRefresher = () -> {
            CompletableFuture<String> future = fetchTokenAsync();
            return future.get();
        };
        
        CommunicationTokenRefreshOptions options = new CommunicationTokenRefreshOptions(asyncRefresher)
            .setRefreshProactively(true);
        
        return new CommunicationTokenCredential(options);
    }
}
```

### Token Refresh with Retry

```java
import java.util.concurrent.Callable;

public class ResilientTokenService {
    private final String tokenEndpoint;
    private final int maxRetries;
    
    public ResilientTokenService(String tokenEndpoint, int maxRetries) {
        this.tokenEndpoint = tokenEndpoint;
        this.maxRetries = maxRetries;
    }
    
    public String fetchTokenWithRetry() throws Exception {
        Exception lastException = null;
        
        for (int attempt = 0; attempt < maxRetries; attempt++) {
            try {
                return fetchToken();
            } catch (Exception e) {
                lastException = e;
                if (attempt < maxRetries - 1) {
                    long delay = (long) Math.pow(2, attempt) * 1000;
                    Thread.sleep(delay);
                }
            }
        }
        
        throw new RuntimeException("Failed to fetch token after " + maxRetries + " attempts", lastException);
    }
    
    private String fetchToken() throws Exception {
        // HTTP call to token endpoint
        return "token-value";
    }
    
    public CommunicationTokenCredential createCredential(String initialToken) {
        CommunicationTokenRefreshOptions options = new CommunicationTokenRefreshOptions(this::fetchTokenWithRetry)
            .setRefreshProactively(true)
            .setInitialToken(initialToken);
        
        return new CommunicationTokenCredential(options);
    }
}
```

## Entra ID Authentication

### Teams Phone Extensibility

```java
import com.azure.identity.InteractiveBrowserCredentialBuilder;
import com.azure.identity.InteractiveBrowserCredential;
import com.azure.communication.common.EntraCommunicationTokenCredentialOptions;
import java.util.Arrays;
import java.util.List;

InteractiveBrowserCredential entraCredential = new InteractiveBrowserCredentialBuilder()
    .clientId("<your-client-id>")
    .tenantId("<your-tenant-id>")
    .redirectUrl("<your-redirect-uri>")
    .build();

String resourceEndpoint = "https://<resource>.communication.azure.com";
List<String> scopes = Arrays.asList(
    "https://auth.msft.communication.azure.com/TeamsExtension.ManageCalls"
);

EntraCommunicationTokenCredentialOptions entraOptions = 
    new EntraCommunicationTokenCredentialOptions(entraCredential, resourceEndpoint)
        .setScopes(scopes);

CommunicationTokenCredential credential = new CommunicationTokenCredential(entraOptions);
```

## Complete Application Example

### Chat Client Factory with Token Management

```java
import com.azure.communication.chat.ChatClient;
import com.azure.communication.chat.ChatClientBuilder;
import com.azure.communication.common.*;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;

public class ChatClientFactory {
    private final String endpoint;
    private final TokenService tokenService;
    private final Map<String, CommunicationTokenCredential> credentialCache = new ConcurrentHashMap<>();
    
    public ChatClientFactory(String endpoint, TokenService tokenService) {
        this.endpoint = endpoint;
        this.tokenService = tokenService;
    }
    
    public ChatClient createChatClient(String userId, String initialToken) {
        CommunicationTokenCredential credential = getOrCreateCredential(userId, initialToken);
        
        return new ChatClientBuilder()
            .endpoint(endpoint)
            .credential(credential)
            .buildClient();
    }
    
    private CommunicationTokenCredential getOrCreateCredential(String userId, String initialToken) {
        return credentialCache.computeIfAbsent(userId, id -> {
            Callable<String> refresher = () -> tokenService.fetchTokenForUser(id);
            
            CommunicationTokenRefreshOptions options = new CommunicationTokenRefreshOptions(refresher)
                .setRefreshProactively(true)
                .setInitialToken(initialToken);
            
            return new CommunicationTokenCredential(options);
        });
    }
    
    public void removeCredential(String userId) {
        CommunicationTokenCredential credential = credentialCache.remove(userId);
        if (credential != null) {
            credential.close();
        }
    }
    
    public void close() {
        credentialCache.values().forEach(CommunicationTokenCredential::close);
        credentialCache.clear();
    }
}

class TokenService {
    public String fetchTokenForUser(String userId) {
        // Fetch token from your server
        return "token-for-" + userId;
    }
}
```

### Multi-Tenant Communication Service

```java
import com.azure.communication.common.*;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class MultiTenantCommunicationService {
    private final Map<String, TenantContext> tenantContexts = new ConcurrentHashMap<>();
    
    public void registerTenant(String tenantId, String endpoint, String connectionString) {
        TenantContext context = new TenantContext(tenantId, endpoint, connectionString);
        tenantContexts.put(tenantId, context);
    }
    
    public CommunicationTokenCredential getCredentialForUser(String tenantId, String userId, String token) {
        TenantContext context = tenantContexts.get(tenantId);
        if (context == null) {
            throw new IllegalArgumentException("Unknown tenant: " + tenantId);
        }
        
        return context.getOrCreateCredential(userId, token);
    }
    
    public CommunicationUserIdentifier createUserIdentifier(String tenantId, String userId) {
        // Format: 8:acs:resourceId_userId
        TenantContext context = tenantContexts.get(tenantId);
        String rawId = "8:acs:" + context.getResourceId() + "_" + userId;
        return new CommunicationUserIdentifier(rawId);
    }
    
    private static class TenantContext {
        private final String tenantId;
        private final String endpoint;
        private final String resourceId;
        private final Map<String, CommunicationTokenCredential> userCredentials = new ConcurrentHashMap<>();
        
        TenantContext(String tenantId, String endpoint, String connectionString) {
            this.tenantId = tenantId;
            this.endpoint = endpoint;
            this.resourceId = extractResourceId(endpoint);
        }
        
        String getResourceId() {
            return resourceId;
        }
        
        CommunicationTokenCredential getOrCreateCredential(String userId, String token) {
            return userCredentials.computeIfAbsent(userId, id -> 
                new CommunicationTokenCredential(token));
        }
        
        private String extractResourceId(String endpoint) {
            // Extract resource ID from endpoint URL
            return endpoint.replace("https://", "").replace(".communication.azure.com", "");
        }
    }
}
```

## Environment Variables

```bash
AZURE_COMMUNICATION_ENDPOINT=https://<resource>.communication.azure.com
AZURE_COMMUNICATION_USER_TOKEN=<user-access-token>
```

## Best Practices

1. **Proactive Refresh** - Always use `setRefreshProactively(true)` for long-lived clients
2. **Token Security** - Never log or expose full tokens
3. **Close Credentials** - Dispose of credentials when no longer needed
4. **Error Handling** - Handle token refresh failures gracefully
5. **Identifier Types** - Use specific identifier types, not raw strings
6. **Connection Reuse** - Reuse credentials across requests to the same user
7. **Caching** - Cache credentials per user to avoid unnecessary token refreshes
