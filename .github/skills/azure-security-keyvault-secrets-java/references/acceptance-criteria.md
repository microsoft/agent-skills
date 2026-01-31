# Azure Key Vault Secrets SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-security-keyvault-secrets`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/keyvault/azure-security-keyvault-secrets
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: SecretClient and Builder Imports
```java
import com.azure.security.keyvault.secrets.SecretClient;
import com.azure.security.keyvault.secrets.SecretClientBuilder;
import com.azure.security.keyvault.secrets.SecretAsyncClient;
```
#### ❌ INCORRECT: Wrong Package or Class Names
```java
import com.azure.keyvault.secrets.SecretClient;  // Wrong package
import com.azure.security.keyvault.SecretsClient;  // Wrong class name
import com.azure.security.keyvault.secrets.KeyVaultSecretClient;  // Wrong name
```

### 1.2 Model Imports
#### ✅ CORRECT: Secret Models
```java
import com.azure.security.keyvault.secrets.models.KeyVaultSecret;
import com.azure.security.keyvault.secrets.models.SecretProperties;
import com.azure.security.keyvault.secrets.models.DeletedSecret;
```
#### ❌ INCORRECT: Wrong Model Names
```java
import com.azure.security.keyvault.secrets.models.Secret;  // Wrong name
import com.azure.security.keyvault.secrets.models.VaultSecret;  // Wrong name
```

### 1.3 Credential Import
#### ✅ CORRECT: Azure Identity
```java
import com.azure.identity.DefaultAzureCredentialBuilder;
```

---

## 2. Client Creation Patterns

### 2.1 Synchronous Client
#### ✅ CORRECT: Using VaultUrl and Credential
```java
SecretClient secretClient = new SecretClientBuilder()
    .vaultUrl("https://<vault-name>.vault.azure.net")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```
#### ❌ INCORRECT: Missing VaultUrl or Wrong Method
```java
SecretClient secretClient = new SecretClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();  // Missing vaultUrl

SecretClient secretClient = new SecretClientBuilder()
    .endpoint("https://<vault-name>.vault.azure.net")  // Wrong method name
    .credential(credential)
    .buildClient();
```

### 2.2 Asynchronous Client
#### ✅ CORRECT: Building Async Client
```java
SecretAsyncClient secretAsyncClient = new SecretClientBuilder()
    .vaultUrl("https://<vault-name>.vault.azure.net")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncClient();
```
#### ❌ INCORRECT: Wrong Build Method
```java
SecretAsyncClient secretAsyncClient = new SecretClientBuilder()
    .vaultUrl("https://vault.vault.azure.net")
    .credential(credential)
    .buildClient();  // Returns sync client, not async
```

---

## 3. Create/Set Secret Operations

### 3.1 Simple Secret
#### ✅ CORRECT: Using setSecret with Name and Value
```java
KeyVaultSecret secret = secretClient.setSecret("database-password", "P@ssw0rd123!");
System.out.println("Secret name: " + secret.getName());
System.out.println("Secret ID: " + secret.getId());
```
#### ❌ INCORRECT: Wrong Method Name
```java
secretClient.createSecret("name", "value");  // Method doesn't exist
secretClient.addSecret("name", "value");  // Method doesn't exist
```

### 3.2 Secret with Options
#### ✅ CORRECT: Using KeyVaultSecret with Properties
```java
KeyVaultSecret secretWithOptions = secretClient.setSecret(
    new KeyVaultSecret("api-key", "sk_live_abc123xyz")
        .setProperties(new SecretProperties()
            .setContentType("application/json")
            .setExpiresOn(OffsetDateTime.now().plusYears(1))
            .setNotBefore(OffsetDateTime.now())
            .setEnabled(true)
            .setTags(Map.of(
                "environment", "production",
                "service", "payment-api"
            ))
        )
);
```
#### ❌ INCORRECT: Setting Properties Directly on Secret
```java
KeyVaultSecret secret = new KeyVaultSecret("name", "value");
secret.setContentType("text/plain");  // Wrong - must use setProperties()
```

---

## 4. Get Secret Operations

### 4.1 Get Latest Version
#### ✅ CORRECT: Get by Name
```java
KeyVaultSecret secret = secretClient.getSecret("database-password");
String value = secret.getValue();
System.out.println("Secret value: " + value);
```
#### ❌ INCORRECT: Wrong Return Type Expectation
```java
String value = secretClient.getSecret("name");  // Returns KeyVaultSecret, not String
```

### 4.2 Get Specific Version
#### ✅ CORRECT: Get with Version ID
```java
KeyVaultSecret specificVersion = secretClient.getSecret("database-password", "<version-id>");
```

### 4.3 Get Properties Only
#### ✅ CORRECT: Access Properties without Value
```java
SecretProperties props = secretClient.getSecret("database-password").getProperties();
System.out.println("Enabled: " + props.isEnabled());
System.out.println("Created: " + props.getCreatedOn());
```

---

## 5. Update Secret Properties

### 5.1 Update Properties
#### ✅ CORRECT: Modify and Update
```java
KeyVaultSecret secret = secretClient.getSecret("api-key");

secret.getProperties()
    .setEnabled(false)
    .setExpiresOn(OffsetDateTime.now().plusMonths(6))
    .setTags(Map.of("status", "rotating"));

SecretProperties updated = secretClient.updateSecretProperties(secret.getProperties());
System.out.println("Updated: " + updated.getUpdatedOn());
```
#### ❌ INCORRECT: Trying to Update Value
```java
// Cannot update value - must create new version
secret.setValue("new-value");  // Method doesn't exist
secretClient.updateSecret(secret);  // Method doesn't exist
```

---

## 6. List Secrets Operations

### 6.1 List All Secrets
#### ✅ CORRECT: Iterate SecretProperties
```java
for (SecretProperties secretProps : secretClient.listPropertiesOfSecrets()) {
    System.out.println("Secret: " + secretProps.getName());
    System.out.println("  Enabled: " + secretProps.isEnabled());
    System.out.println("  Created: " + secretProps.getCreatedOn());
    System.out.println("  Content-Type: " + secretProps.getContentType());
    
    // Get value if needed
    if (secretProps.isEnabled()) {
        KeyVaultSecret fullSecret = secretClient.getSecret(secretProps.getName());
        System.out.println("  Value: " + fullSecret.getValue().substring(0, 5) + "...");
    }
}
```
#### ❌ INCORRECT: Expecting KeyVaultSecret
```java
for (KeyVaultSecret secret : secretClient.listSecrets()) {  // Wrong method and return type
    // listPropertiesOfSecrets returns SecretProperties
}
```

### 6.2 List Secret Versions
#### ✅ CORRECT: Listing Versions
```java
for (SecretProperties version : secretClient.listPropertiesOfSecretVersions("database-password")) {
    System.out.println("Version: " + version.getVersion());
    System.out.println("Created: " + version.getCreatedOn());
    System.out.println("Enabled: " + version.isEnabled());
}
```

---

## 7. Delete Secret Operations

### 7.1 Begin Delete Secret
#### ✅ CORRECT: Using SyncPoller
```java
import com.azure.core.util.polling.SyncPoller;

SyncPoller<DeletedSecret, Void> deletePoller = secretClient.beginDeleteSecret("old-secret");

DeletedSecret deletedSecret = deletePoller.poll().getValue();
System.out.println("Deleted on: " + deletedSecret.getDeletedOn());
System.out.println("Scheduled purge: " + deletedSecret.getScheduledPurgeDate());

deletePoller.waitForCompletion();
```
#### ❌ INCORRECT: Synchronous Delete
```java
secretClient.deleteSecret("old-secret");  // Method doesn't exist, use beginDeleteSecret
```

### 7.2 List Deleted Secrets
#### ✅ CORRECT: Iterating Deleted Secrets
```java
for (DeletedSecret deleted : secretClient.listDeletedSecrets()) {
    System.out.println("Deleted: " + deleted.getName());
    System.out.println("Deletion date: " + deleted.getDeletedOn());
}
```

### 7.3 Recover Deleted Secret
#### ✅ CORRECT: Using SyncPoller for Recovery
```java
SyncPoller<KeyVaultSecret, Void> recoverPoller = secretClient.beginRecoverDeletedSecret("old-secret");
recoverPoller.waitForCompletion();

KeyVaultSecret recovered = recoverPoller.getFinalResult();
System.out.println("Recovered: " + recovered.getName());
```

### 7.4 Purge Deleted Secret
#### ✅ CORRECT: Permanent Deletion
```java
DeletedSecret deleted = secretClient.getDeletedSecret("old-secret");
System.out.println("Will purge: " + deleted.getName());
secretClient.purgeDeletedSecret("old-secret");
```

---

## 8. Backup and Restore

### 8.1 Backup Secret
#### ✅ CORRECT: Backup All Versions
```java
byte[] backup = secretClient.backupSecret("important-secret");
Files.write(Paths.get("secret-backup.blob"), backup);
```

### 8.2 Restore Secret
#### ✅ CORRECT: Restore from Backup
```java
byte[] backupData = Files.readAllBytes(Paths.get("secret-backup.blob"));
KeyVaultSecret restored = secretClient.restoreSecretBackup(backupData);
System.out.println("Restored: " + restored.getName());
```

---

## 9. Async Operations

### 9.1 Async Set Secret
#### ✅ CORRECT: Reactive Patterns
```java
asyncClient.setSecret("async-secret", "async-value")
    .subscribe(
        secret -> System.out.println("Created: " + secret.getName()),
        error -> System.out.println("Error: " + error.getMessage())
    );
```
#### ❌ INCORRECT: Blocking on Async Client
```java
asyncClient.setSecret("secret", "value").block();  // Avoid blocking
```

### 9.2 Async Get Secret
#### ✅ CORRECT: Subscribe to Result
```java
asyncClient.getSecret("async-secret")
    .subscribe(secret -> System.out.println("Value: " + secret.getValue()));
```

### 9.3 Async List Secrets
#### ✅ CORRECT: Flux Processing
```java
asyncClient.listPropertiesOfSecrets()
    .doOnNext(props -> System.out.println("Found: " + props.getName()))
    .subscribe();
```

---

## 10. Error Handling

### 10.1 Exception Handling
#### ✅ CORRECT: Specific Exception Types
```java
import com.azure.core.exception.HttpResponseException;
import com.azure.core.exception.ResourceNotFoundException;

try {
    KeyVaultSecret secret = secretClient.getSecret("my-secret");
    System.out.println("Value: " + secret.getValue());
} catch (ResourceNotFoundException e) {
    System.out.println("Secret not found");
} catch (HttpResponseException e) {
    int status = e.getResponse().getStatusCode();
    if (status == 403) {
        System.out.println("Access denied - check permissions");
    } else if (status == 429) {
        System.out.println("Rate limited - retry later");
    } else {
        System.out.println("HTTP error: " + status);
    }
}
```
#### ❌ INCORRECT: Generic Exception Only
```java
try {
    KeyVaultSecret secret = secretClient.getSecret("secret");
} catch (Exception e) {
    // Missing specific error handling
}
```

---

## 11. Configuration Patterns

### 11.1 Load Multiple Secrets
#### ✅ CORRECT: Service Pattern
```java
public class ConfigLoader {
    private final SecretClient client;
    
    public ConfigLoader(String vaultUrl) {
        this.client = new SecretClientBuilder()
            .vaultUrl(vaultUrl)
            .credential(new DefaultAzureCredentialBuilder().build())
            .buildClient();
    }
    
    public Map<String, String> loadSecrets(List<String> secretNames) {
        Map<String, String> secrets = new HashMap<>();
        for (String name : secretNames) {
            try {
                KeyVaultSecret secret = client.getSecret(name);
                secrets.put(name, secret.getValue());
            } catch (ResourceNotFoundException e) {
                System.out.println("Secret not found: " + name);
            }
        }
        return secrets;
    }
}
```
#### ❌ INCORRECT: Creating New Client Per Request
```java
public String getSecret(String name) {
    // Don't create client every time
    SecretClient client = new SecretClientBuilder()
        .vaultUrl(vaultUrl)
        .credential(new DefaultAzureCredentialBuilder().build())
        .buildClient();
    return client.getSecret(name).getValue();
}
```

### 11.2 Secret Rotation Pattern
#### ✅ CORRECT: Disable Old and Create New
```java
public void rotateSecret(String secretName, String newValue) {
    // Get current secret
    KeyVaultSecret current = secretClient.getSecret(secretName);
    
    // Disable old version
    current.getProperties().setEnabled(false);
    secretClient.updateSecretProperties(current.getProperties());
    
    // Create new version with new value
    KeyVaultSecret newSecret = secretClient.setSecret(secretName, newValue);
    System.out.println("Rotated to version: " + newSecret.getProperties().getVersion());
}
```

---

## 12. Common Secret Types

### 12.1 Database Connection String
#### ✅ CORRECT: With Appropriate Content Type and Tags
```java
secretClient.setSecret(new KeyVaultSecret("db-connection", 
    "Server=myserver.database.windows.net;Database=mydb;...")
    .setProperties(new SecretProperties()
        .setContentType("text/plain")
        .setTags(Map.of("type", "connection-string"))));
```

### 12.2 API Key
#### ✅ CORRECT: With Expiration
```java
secretClient.setSecret(new KeyVaultSecret("stripe-api-key", "sk_live_...")
    .setProperties(new SecretProperties()
        .setContentType("text/plain")
        .setExpiresOn(OffsetDateTime.now().plusYears(1))));
```

### 12.3 JSON Configuration
#### ✅ CORRECT: JSON Content Type
```java
secretClient.setSecret(new KeyVaultSecret("app-config", 
    "{\"endpoint\":\"https://...\",\"key\":\"...\"}")
    .setProperties(new SecretProperties()
        .setContentType("application/json")));
```
