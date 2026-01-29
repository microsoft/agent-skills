# Azure Key Vault Secrets SDK for Java - Examples

Comprehensive code examples for the Azure Key Vault Secrets SDK for Java.

## Table of Contents
- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Setting Secrets](#setting-secrets)
- [Getting Secrets](#getting-secrets)
- [Listing Secrets](#listing-secrets)
- [Updating Secret Properties](#updating-secret-properties)
- [Deleting and Recovering Secrets](#deleting-and-recovering-secrets)
- [Purging Deleted Secrets](#purging-deleted-secrets)
- [Backup and Restore](#backup-and-restore)
- [Async Client Patterns](#async-client-patterns)
- [Error Handling](#error-handling)

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-security-keyvault-secrets</artifactId>
    <version>4.11.0-beta.1</version>
</dependency>

<!-- Required for authentication -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
    <version>1.18.2</version>
</dependency>
```

## Client Creation

### Sync SecretClient

```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.security.keyvault.secrets.SecretClient;
import com.azure.security.keyvault.secrets.SecretClientBuilder;

SecretClient secretClient = new SecretClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .vaultUrl("<your-key-vault-url>")
    .buildClient();
```

### Async SecretClient

```java
import com.azure.security.keyvault.secrets.SecretAsyncClient;

SecretAsyncClient secretAsyncClient = new SecretClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .vaultUrl("<your-key-vault-url>")
    .buildAsyncClient();
```

## Setting Secrets

### Simple Secret

```java
import com.azure.security.keyvault.secrets.models.KeyVaultSecret;

KeyVaultSecret secret = secretClient.setSecret("<secret-name>", "<secret-value>");
System.out.printf("Secret created with name \"%s\" and value \"%s\"%n", 
    secret.getName(), secret.getValue());
```

### Secret with Properties (Expiration)

```java
import com.azure.security.keyvault.secrets.models.SecretProperties;
import java.time.OffsetDateTime;

KeyVaultSecret newSecret = new KeyVaultSecret("secretName", "secretValue")
    .setProperties(new SecretProperties().setExpiresOn(OffsetDateTime.now().plusDays(60)));

KeyVaultSecret returnedSecret = secretClient.setSecret(newSecret);
System.out.printf("Secret created with name %s and value %s%n", 
    returnedSecret.getName(), returnedSecret.getValue());
```

### With Response (includes HTTP metadata)

```java
import com.azure.core.util.Context;

KeyVaultSecret newSecret = new KeyVaultSecret("secretName", "secretValue")
    .setProperties(new SecretProperties().setExpiresOn(OffsetDateTime.now().plusDays(60)));

KeyVaultSecret secret = secretClient.setSecretWithResponse(newSecret, new Context("key1", "value1"))
    .getValue();
System.out.printf("Secret created with name %s%n", secret.getName());
```

## Getting Secrets

### Get Current Version

```java
KeyVaultSecret secret = secretClient.getSecret("secretName");
System.out.printf("Secret returned with name %s and value %s%n",
    secret.getName(), secret.getValue());
```

### Get Specific Version

```java
String secretVersion = "6A385B124DEF4096AF1361A85B16C204";
KeyVaultSecret secretWithVersion = secretClient.getSecret("secretName", secretVersion);
System.out.printf("Secret returned with name %s and value %s%n",
    secretWithVersion.getName(), secretWithVersion.getValue());
```

### Get with Response

```java
import com.azure.core.util.Context;

String secretVersion = "6A385B124DEF4096AF1361A85B16C204";
KeyVaultSecret secret = secretClient.getSecretWithResponse(
    "secretName", 
    secretVersion,
    new Context("key1", "value1")
).getValue();
System.out.printf("Secret returned with name %s%n", secret.getName());
```

## Listing Secrets

### List All Secrets

```java
import com.azure.security.keyvault.secrets.models.SecretProperties;

// Note: List operations don't return secret values - call getSecret for each
for (SecretProperties secretProps : secretClient.listPropertiesOfSecrets()) {
    KeyVaultSecret secretWithValue = secretClient.getSecret(
        secretProps.getName(), 
        secretProps.getVersion()
    );
    System.out.printf("Secret: %s = %s%n", 
        secretWithValue.getName(), 
        secretWithValue.getValue());
}
```

### List with Pagination

```java
secretClient.listPropertiesOfSecrets().iterableByPage().forEach(page -> {
    System.out.printf("Status code: %d, URL: %s%n", 
        page.getStatusCode(), 
        page.getRequest().getUrl());
    
    page.getItems().forEach(secretProps -> {
        KeyVaultSecret secret = secretClient.getSecret(
            secretProps.getName(), 
            secretProps.getVersion()
        );
        System.out.printf("Secret: %s%n", secret.getName());
    });
});
```

### List Secret Versions

```java
for (SecretProperties secretProps : secretClient.listPropertiesOfSecretVersions("secretName")) {
    KeyVaultSecret secret = secretClient.getSecret(
        secretProps.getName(), 
        secretProps.getVersion()
    );
    System.out.printf("Version: %s, Value: %s%n", 
        secretProps.getVersion(), 
        secret.getValue());
}
```

## Updating Secret Properties

```java
// Get the secret first
SecretProperties secretProperties = secretClient.getSecret("secretName").getProperties();

// Update the expiry time
secretProperties.setExpiresOn(OffsetDateTime.now().plusDays(60));
SecretProperties updatedProperties = secretClient.updateSecretProperties(secretProperties);

// Get the updated secret
KeyVaultSecret updatedSecret = secretClient.getSecret(updatedProperties.getName());
System.out.printf("Updated secret expires: %s%n", 
    updatedSecret.getProperties().getExpiresOn());
```

**Note**: `updateSecretProperties()` cannot change the secret value - only metadata like expiration, enabled status, tags, etc. To change the value, call `setSecret()` which creates a new version.

## Deleting and Recovering Secrets

### Delete Secret (with Polling)

```java
import com.azure.core.util.polling.PollResponse;
import com.azure.core.util.polling.SyncPoller;
import com.azure.security.keyvault.secrets.models.DeletedSecret;

SyncPoller<DeletedSecret, Void> deleteSecretPoller = secretClient.beginDeleteSecret("secretName");

// Deleted Secret is accessible as soon as polling begins
PollResponse<DeletedSecret> pollResponse = deleteSecretPoller.poll();

// Deletion date only works for SoftDelete-enabled Key Vault
System.out.printf("Deleted Date: %s%n", pollResponse.getValue().getDeletedOn());
System.out.printf("Recovery Id: %s%n", pollResponse.getValue().getRecoveryId());

// Wait for deletion to complete on server
deleteSecretPoller.waitForCompletion();
```

### Get Deleted Secret

```java
DeletedSecret deletedSecret = secretClient.getDeletedSecret("secretName");
System.out.printf("Recovery Id: %s%n", deletedSecret.getRecoveryId());
```

### List Deleted Secrets

```java
for (DeletedSecret deletedSecret : secretClient.listDeletedSecrets()) {
    System.out.printf("Deleted secret: %s, Recovery Id: %s%n", 
        deletedSecret.getName(),
        deletedSecret.getRecoveryId());
}
```

### Recover Deleted Secret

```java
SyncPoller<KeyVaultSecret, Void> recoverPoller = 
    secretClient.beginRecoverDeletedSecret("deletedSecretName");

// Recovered secret accessible as soon as polling begins
PollResponse<KeyVaultSecret> pollResponse = recoverPoller.poll();
System.out.printf("Recovered secret: %s%n", pollResponse.getValue().getName());

// Wait for recovery to complete on server
recoverPoller.waitForCompletion();
```

## Purging Deleted Secrets

```java
// Permanently delete (cannot be recovered after this)
secretClient.purgeDeletedSecret("secretName");
System.out.println("Secret purged permanently");
```

## Backup and Restore

### Backup Secret

```java
byte[] secretBackup = secretClient.backupSecret("secretName");
System.out.printf("Secret backup size: %d bytes%n", secretBackup.length);

// Store the backup securely (e.g., to a file or blob storage)
```

### Restore Secret

```java
// Restore from backup bytes
KeyVaultSecret restoredSecret = secretClient.restoreSecretBackup(secretBackup);
System.out.printf("Restored secret: %s%n", restoredSecret.getName());
```

## Async Client Patterns

### Set Secret Async

```java
secretAsyncClient.setSecret("asyncSecretName", "asyncSecretValue")
    .subscribe(
        secret -> System.out.printf("Created secret: %s%n", secret.getName()),
        error -> System.err.println("Error: " + error.getMessage()),
        () -> System.out.println("Operation completed")
    );
```

### Get Secret Async

```java
secretAsyncClient.getSecret("secretName")
    .subscribe(
        secret -> System.out.printf("Secret value: %s%n", secret.getValue()),
        error -> System.err.println("Error: " + error.getMessage())
    );
```

### List Secrets Async

```java
secretAsyncClient.listPropertiesOfSecrets()
    .flatMap(secretProps -> secretAsyncClient.getSecret(
        secretProps.getName(), 
        secretProps.getVersion()
    ))
    .subscribe(
        secret -> System.out.printf("Secret: %s%n", secret.getName()),
        error -> System.err.println("Error: " + error.getMessage())
    );
```

### Delete Secret Async

```java
secretAsyncClient.beginDeleteSecret("secretName")
    .subscribe(pollResponse -> {
        System.out.printf("Delete status: %s%n", pollResponse.getStatus());
        System.out.printf("Deleted secret: %s%n", pollResponse.getValue().getName());
    });
```

### Chain Operations

```java
secretAsyncClient.setSecret("mySecret", "myValue")
    .flatMap(created -> {
        System.out.printf("Created: %s%n", created.getName());
        return secretAsyncClient.getSecret(created.getName());
    })
    .flatMap(retrieved -> {
        System.out.printf("Retrieved: %s%n", retrieved.getValue());
        retrieved.getProperties().setExpiresOn(OffsetDateTime.now().plusDays(30));
        return secretAsyncClient.updateSecretProperties(retrieved.getProperties());
    })
    .subscribe(
        updated -> System.out.printf("Updated, expires: %s%n", updated.getExpiresOn()),
        error -> System.err.println("Error: " + error.getMessage())
    );
```

## Error Handling

### Sync Error Handling

```java
import com.azure.core.exception.HttpResponseException;
import com.azure.core.exception.ResourceNotFoundException;

try {
    KeyVaultSecret secret = secretClient.getSecret("nonexistent-secret");
} catch (ResourceNotFoundException e) {
    System.err.println("Secret not found: " + e.getMessage());
} catch (HttpResponseException e) {
    System.err.println("HTTP error: " + e.getResponse().getStatusCode());
    System.err.println("Message: " + e.getMessage());
} catch (Exception e) {
    System.err.println("Unexpected error: " + e.getMessage());
}
```

### Async Error Handling

```java
secretAsyncClient.getSecret("nonexistent-secret")
    .subscribe(
        secret -> System.out.println("Secret: " + secret.getName()),
        error -> {
            if (error instanceof ResourceNotFoundException) {
                System.err.println("Secret not found");
            } else if (error instanceof HttpResponseException) {
                HttpResponseException httpError = (HttpResponseException) error;
                System.err.println("HTTP error: " + httpError.getResponse().getStatusCode());
            } else {
                System.err.println("Error: " + error.getMessage());
            }
        }
    );
```

### Common Error Scenarios

| Status Code | Exception | Cause |
|-------------|-----------|-------|
| 401 | ClientAuthenticationException | Invalid credentials |
| 403 | HttpResponseException | Access denied (missing permissions) |
| 404 | ResourceNotFoundException | Secret not found |
| 409 | HttpResponseException | Conflict (secret already exists/deleted) |
| 429 | HttpResponseException | Rate limited |
