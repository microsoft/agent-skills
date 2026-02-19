# Azure Key Vault Secrets SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-security-keyvault-secrets`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/keyvault-v2/azure-security-keyvault-secrets
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Secret Clients
```java
import com.azure.security.keyvault.secrets.SecretClient;
import com.azure.security.keyvault.secrets.SecretClientBuilder;
import com.azure.security.keyvault.secrets.SecretAsyncClient;
```

#### ✅ CORRECT: Authentication
```java
import com.azure.identity.DefaultAzureCredentialBuilder;
```

### 1.2 Model Imports

#### ✅ CORRECT: Secret Models
```java
import com.azure.security.keyvault.secrets.models.KeyVaultSecret;
import com.azure.security.keyvault.secrets.models.SecretProperties;
import com.azure.security.keyvault.secrets.models.DeletedSecret;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Builder with DefaultAzureCredential
```java
String vaultUrl = System.getenv("AZURE_KEYVAULT_URL");

SecretClient secretClient = new SecretClientBuilder()
    .vaultUrl(vaultUrl)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### 2.2 ✅ CORRECT: Async Client
```java
SecretAsyncClient secretAsyncClient = new SecretClientBuilder()
    .vaultUrl(vaultUrl)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncClient();
```

---

## 3. Secret Operations

### 3.1 ✅ CORRECT: Set Secret
```java
KeyVaultSecret secret = secretClient.setSecret("database-password", "P@ssw0rd123!");
System.out.println("Secret name: " + secret.getName());
```

### 3.2 ✅ CORRECT: Set Secret with Options
```java
KeyVaultSecret secretWithOptions = secretClient.setSecret(
    new KeyVaultSecret("api-key", "sk_live_abc123xyz")
        .setProperties(new SecretProperties()
            .setContentType("text/plain")
            .setExpiresOn(OffsetDateTime.now().plusYears(1))
            .setTags(Map.of("environment", "production"))));
```

### 3.3 ✅ CORRECT: Get Secret
```java
KeyVaultSecret secret = secretClient.getSecret("database-password");
String value = secret.getValue();
```

### 3.4 ✅ CORRECT: List Secrets
```java
for (SecretProperties props : secretClient.listPropertiesOfSecrets()) {
    System.out.println("Secret: " + props.getName());
}
```

### 3.5 ✅ CORRECT: Delete Secret
```java
SyncPoller<DeletedSecret, Void> deletePoller = secretClient.beginDeleteSecret("old-secret");
deletePoller.waitForCompletion();
```

---

## 4. Secret Rotation Pattern

### 4.1 ✅ CORRECT: Rotate Secret
```java
public void rotateSecret(String secretName, String newValue) {
    KeyVaultSecret current = secretClient.getSecret(secretName);
    
    // Disable old version
    current.getProperties().setEnabled(false);
    secretClient.updateSecretProperties(current.getProperties());
    
    // Create new version
    KeyVaultSecret newSecret = secretClient.setSecret(secretName, newValue);
    System.out.println("Rotated to version: " + newSecret.getProperties().getVersion());
}
```

---

## 5. Backup and Restore

### 5.1 ✅ CORRECT: Backup and Restore
```java
// Backup
byte[] backup = secretClient.backupSecret("important-secret");
Files.write(Paths.get("secret-backup.blob"), backup);

// Restore
byte[] backupData = Files.readAllBytes(Paths.get("secret-backup.blob"));
KeyVaultSecret restored = secretClient.restoreSecretBackup(backupData);
```

---

## 6. Error Handling

### 6.1 ✅ CORRECT: Exception Handling
```java
import com.azure.core.exception.HttpResponseException;
import com.azure.core.exception.ResourceNotFoundException;

try {
    KeyVaultSecret secret = secretClient.getSecret("my-secret");
} catch (ResourceNotFoundException e) {
    System.out.println("Secret not found");
} catch (HttpResponseException e) {
    int status = e.getResponse().getStatusCode();
    if (status == 403) {
        System.out.println("Access denied");
    } else if (status == 429) {
        System.out.println("Rate limited");
    }
}
```

---

## 7. Best Practices Checklist

- [ ] Use DefaultAzureCredential for authentication
- [ ] Use environment variables for vault URL
- [ ] Enable soft delete on vault
- [ ] Use tags to organize secrets
- [ ] Set expiration dates for credentials
- [ ] Set content type to indicate format
- [ ] Don't delete old versions immediately during rotation
- [ ] Enable diagnostic logging on Key Vault
