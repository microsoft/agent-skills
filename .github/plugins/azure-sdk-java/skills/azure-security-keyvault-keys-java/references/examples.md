# Azure Key Vault Keys SDK for Java - Examples

Comprehensive code examples for the Azure Key Vault Keys SDK for Java.

## Table of Contents
- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Creating Keys](#creating-keys)
- [Getting and Listing Keys](#getting-and-listing-keys)
- [Updating Key Properties](#updating-key-properties)
- [Deleting and Recovering Keys](#deleting-and-recovering-keys)
- [Key Rotation](#key-rotation)
- [Cryptographic Operations](#cryptographic-operations)
- [Async Client Patterns](#async-client-patterns)
- [Error Handling](#error-handling)

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-security-keyvault-keys</artifactId>
    <version>4.9.0</version>
</dependency>

<!-- Required for authentication -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
    <version>1.14.0</version>
</dependency>
```

## Client Creation

### Sync KeyClient

```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.security.keyvault.keys.KeyClient;
import com.azure.security.keyvault.keys.KeyClientBuilder;

KeyClient keyClient = new KeyClientBuilder()
    .vaultUrl("<your-key-vault-url>")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### Async KeyClient

```java
import com.azure.security.keyvault.keys.KeyAsyncClient;

KeyAsyncClient keyAsyncClient = new KeyClientBuilder()
    .vaultUrl("<your-key-vault-url>")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncClient();
```

### Sync CryptographyClient

```java
import com.azure.security.keyvault.keys.cryptography.CryptographyClient;
import com.azure.security.keyvault.keys.cryptography.CryptographyClientBuilder;

CryptographyClient cryptographyClient = new CryptographyClientBuilder()
    .keyIdentifier("<your-key-id>")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### Async CryptographyClient

```java
import com.azure.security.keyvault.keys.cryptography.CryptographyAsyncClient;

CryptographyAsyncClient cryptographyAsyncClient = new CryptographyClientBuilder()
    .keyIdentifier("<your-key-id>")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncClient();
```

### CryptographyClient with Local JsonWebKey

```java
import com.azure.security.keyvault.keys.models.JsonWebKey;

// For local cryptographic operations without Key Vault call
JsonWebKey jsonWebKey = new JsonWebKey().setId("SampleJsonWebKey");
CryptographyClient cryptographyClient = new CryptographyClientBuilder()
    .jsonWebKey(jsonWebKey)
    .buildClient();
```

## Creating Keys

### Create RSA Key

```java
import com.azure.security.keyvault.keys.models.CreateRsaKeyOptions;
import com.azure.security.keyvault.keys.models.KeyVaultKey;
import java.time.OffsetDateTime;

// Simple RSA key
CreateRsaKeyOptions createRsaKeyOptions = new CreateRsaKeyOptions("myRsaKey")
    .setKeySize(2048)
    .setNotBefore(OffsetDateTime.now().plusDays(1))
    .setExpiresOn(OffsetDateTime.now().plusYears(1));

KeyVaultKey rsaKey = keyClient.createRsaKey(createRsaKeyOptions);
System.out.printf("Created key: %s, ID: %s%n", rsaKey.getName(), rsaKey.getId());

// RSA key with 4096-bit size
keyClient.createRsaKey(new CreateRsaKeyOptions("CloudRsaKey")
    .setExpiresOn(OffsetDateTime.now().plusYears(1))
    .setKeySize(4096));
```

### Create EC (Elliptic Curve) Key

```java
import com.azure.security.keyvault.keys.models.CreateEcKeyOptions;
import com.azure.security.keyvault.keys.models.KeyCurveName;

CreateEcKeyOptions createEcKeyOptions = new CreateEcKeyOptions("myEcKey")
    .setCurveName(KeyCurveName.P_384)
    .setNotBefore(OffsetDateTime.now().plusDays(1))
    .setExpiresOn(OffsetDateTime.now().plusYears(1));

KeyVaultKey ecKey = keyClient.createEcKey(createEcKeyOptions);
System.out.printf("Created EC key: %s%n", ecKey.getName());
```

### Create Symmetric (OCT) Key

```java
import com.azure.security.keyvault.keys.models.CreateOctKeyOptions;

CreateOctKeyOptions createOctKeyOptions = new CreateOctKeyOptions("myOctKey")
    .setNotBefore(OffsetDateTime.now().plusDays(1))
    .setExpiresOn(OffsetDateTime.now().plusYears(1));

KeyVaultKey octKey = keyClient.createOctKey(createOctKeyOptions);
System.out.printf("Created OCT key: %s%n", octKey.getName());
```

### Create Key by Type

```java
import com.azure.security.keyvault.keys.models.CreateKeyOptions;
import com.azure.security.keyvault.keys.models.KeyType;

// Simple key creation
KeyVaultKey key = keyClient.createKey("myKey", KeyType.EC);

// With options
CreateKeyOptions createKeyOptions = new CreateKeyOptions("myKey", KeyType.RSA)
    .setNotBefore(OffsetDateTime.now().plusDays(1))
    .setExpiresOn(OffsetDateTime.now().plusYears(1));

KeyVaultKey optionsKey = keyClient.createKey(createKeyOptions);
```

## Getting and Listing Keys

### Get a Key

```java
// Get latest version
KeyVaultKey key = keyClient.getKey("myKey");
System.out.printf("Key name: %s, ID: %s%n", key.getName(), key.getId());

// Get specific version
String keyVersion = "<key-version>";
KeyVaultKey keyWithVersion = keyClient.getKey("myKey", keyVersion);
```

### Get Key with Response

```java
import com.azure.core.http.rest.Response;
import com.azure.core.util.Context;

Response<KeyVaultKey> getKeyResponse = keyClient.getKeyWithResponse(
    "myKey", 
    keyVersion, 
    new Context("key1", "value1")
);

System.out.printf("Status code: %d%n", getKeyResponse.getStatusCode());
System.out.printf("Key: %s%n", getKeyResponse.getValue().getName());
```

### List All Keys

```java
import com.azure.security.keyvault.keys.models.KeyProperties;

// Simple iteration
for (KeyProperties keyProperties : keyClient.listPropertiesOfKeys()) {
    KeyVaultKey key = keyClient.getKey(keyProperties.getName(), keyProperties.getVersion());
    System.out.printf("Key: %s, Type: %s%n", key.getName(), key.getKeyType());
}

// With pagination
keyClient.listPropertiesOfKeys().iterableByPage().forEach(pagedResponse -> {
    System.out.printf("Page status: %d%n", pagedResponse.getStatusCode());
    pagedResponse.getElements().forEach(keyProperties -> {
        System.out.printf("Key: %s%n", keyProperties.getName());
    });
});
```

### List Key Versions

```java
for (KeyProperties keyProperties : keyClient.listPropertiesOfKeyVersions("myKey")) {
    KeyVaultKey key = keyClient.getKey(keyProperties.getName(), keyProperties.getVersion());
    System.out.printf("Version: %s, Created: %s%n", 
        key.getProperties().getVersion(), 
        key.getProperties().getCreatedOn());
}
```

## Updating Key Properties

```java
import com.azure.security.keyvault.keys.models.KeyOperation;

// Get key first
KeyVaultKey key = keyClient.getKey("myKey");

// Update expiry time
key.getProperties().setExpiresOn(OffsetDateTime.now().plusDays(60));

// Update with allowed operations
KeyVaultKey updatedKey = keyClient.updateKeyProperties(
    key.getProperties(), 
    KeyOperation.ENCRYPT, 
    KeyOperation.DECRYPT
);

System.out.printf("Updated key: %s%n", updatedKey.getName());
```

### Update with Response

```java
Response<KeyVaultKey> updateKeyResponse = keyClient.updateKeyPropertiesWithResponse(
    key.getProperties(), 
    new Context("key1", "value1"),
    KeyOperation.ENCRYPT, 
    KeyOperation.DECRYPT
);

System.out.printf("Update status: %d%n", updateKeyResponse.getStatusCode());
```

## Deleting and Recovering Keys

### Delete a Key

```java
import com.azure.core.util.polling.PollResponse;
import com.azure.core.util.polling.SyncPoller;
import com.azure.security.keyvault.keys.models.DeletedKey;

// Begin delete (long-running operation)
SyncPoller<DeletedKey, Void> deleteKeyPoller = keyClient.beginDeleteKey("myKey");
PollResponse<DeletedKey> deleteKeyPollResponse = deleteKeyPoller.poll();

// Get deleted key info
DeletedKey deletedKey = deleteKeyPollResponse.getValue();
System.out.printf("Delete date: %s%n", deletedKey.getDeletedOn());
System.out.printf("Recovery ID: %s%n", deletedKey.getRecoveryId());

// Wait for deletion to complete
deleteKeyPoller.waitForCompletion();
```

### Get Deleted Key

```java
DeletedKey deletedKey = keyClient.getDeletedKey("myKey");
System.out.printf("Recovery ID: %s%n", deletedKey.getRecoveryId());
```

### List Deleted Keys

```java
for (DeletedKey deletedKey : keyClient.listDeletedKeys()) {
    System.out.printf("Deleted key: %s, Recovery ID: %s%n", 
        deletedKey.getName(), 
        deletedKey.getRecoveryId());
}
```

### Recover Deleted Key

```java
SyncPoller<KeyVaultKey, Void> recoverKeyPoller = keyClient.beginRecoverDeletedKey("myKey");
PollResponse<KeyVaultKey> recoverKeyPollResponse = recoverKeyPoller.poll();

KeyVaultKey recoveredKey = recoverKeyPollResponse.getValue();
System.out.printf("Recovered key: %s%n", recoveredKey.getName());

recoverKeyPoller.waitForCompletion();
```

### Purge Deleted Key

```java
// Permanently delete (cannot be recovered)
keyClient.purgeDeletedKey("myKey");
System.out.println("Key purged permanently");
```

## Key Rotation

### Rotate Key

```java
// Create new version of the key
KeyVaultKey rotatedKey = keyClient.rotateKey("myKey");
System.out.printf("New key version: %s%n", rotatedKey.getProperties().getVersion());
```

### Get Key Rotation Policy

```java
import com.azure.security.keyvault.keys.models.KeyRotationPolicy;

KeyRotationPolicy policy = keyClient.getKeyRotationPolicy("myKey");
System.out.printf("Policy ID: %s%n", policy.getId());
```

### Update Key Rotation Policy

```java
import com.azure.security.keyvault.keys.models.KeyRotationLifetimeAction;
import com.azure.security.keyvault.keys.models.KeyRotationPolicyAction;

KeyRotationPolicy policy = new KeyRotationPolicy()
    .setExpiresIn("P90D")  // Key expires in 90 days
    .setLifetimeActions(Arrays.asList(
        new KeyRotationLifetimeAction(KeyRotationPolicyAction.ROTATE)
            .setTimeBeforeExpiry("P30D")  // Rotate 30 days before expiry
    ));

KeyRotationPolicy updatedPolicy = keyClient.updateKeyRotationPolicy("myKey", policy);
```

## Cryptographic Operations

### Encrypt and Decrypt

```java
import com.azure.security.keyvault.keys.cryptography.models.EncryptionAlgorithm;
import com.azure.security.keyvault.keys.cryptography.models.EncryptResult;
import com.azure.security.keyvault.keys.cryptography.models.DecryptResult;

byte[] plaintext = "Hello, World!".getBytes();

// Encrypt
EncryptResult encryptResult = cryptographyClient.encrypt(
    EncryptionAlgorithm.RSA_OAEP, 
    plaintext
);
byte[] ciphertext = encryptResult.getCipherText();
System.out.printf("Encrypted: %d bytes%n", ciphertext.length);

// Decrypt
DecryptResult decryptResult = cryptographyClient.decrypt(
    EncryptionAlgorithm.RSA_OAEP, 
    ciphertext
);
String decryptedText = new String(decryptResult.getPlainText());
System.out.printf("Decrypted: %s%n", decryptedText);
```

### Sign and Verify

```java
import com.azure.security.keyvault.keys.cryptography.models.SignatureAlgorithm;
import com.azure.security.keyvault.keys.cryptography.models.SignResult;
import com.azure.security.keyvault.keys.cryptography.models.VerifyResult;
import java.security.MessageDigest;

byte[] data = "Data to sign".getBytes();
MessageDigest md = MessageDigest.getInstance("SHA-256");
byte[] digest = md.digest(data);

// Sign
SignResult signResult = cryptographyClient.sign(
    SignatureAlgorithm.RS256, 
    digest
);
byte[] signature = signResult.getSignature();
System.out.printf("Signature: %d bytes%n", signature.length);

// Verify
VerifyResult verifyResult = cryptographyClient.verify(
    SignatureAlgorithm.RS256, 
    digest, 
    signature
);
System.out.printf("Signature valid: %s%n", verifyResult.isValid());
```

### Wrap and Unwrap Key

```java
import com.azure.security.keyvault.keys.cryptography.models.KeyWrapAlgorithm;
import com.azure.security.keyvault.keys.cryptography.models.WrapResult;
import com.azure.security.keyvault.keys.cryptography.models.UnwrapResult;

byte[] keyToWrap = new byte[32];  // 256-bit key
new java.security.SecureRandom().nextBytes(keyToWrap);

// Wrap
WrapResult wrapResult = cryptographyClient.wrapKey(
    KeyWrapAlgorithm.RSA_OAEP, 
    keyToWrap
);
byte[] wrappedKey = wrapResult.getEncryptedKey();
System.out.printf("Wrapped key: %d bytes%n", wrappedKey.length);

// Unwrap
UnwrapResult unwrapResult = cryptographyClient.unwrapKey(
    KeyWrapAlgorithm.RSA_OAEP, 
    wrappedKey
);
byte[] unwrappedKey = unwrapResult.getKey();
System.out.printf("Unwrapped key: %d bytes%n", unwrappedKey.length);
```

## Async Client Patterns

### Create Key Async

```java
keyAsyncClient.createRsaKey(new CreateRsaKeyOptions("asyncKey").setKeySize(2048))
    .subscribe(
        key -> System.out.printf("Created key: %s%n", key.getName()),
        error -> System.err.println("Error: " + error.getMessage()),
        () -> System.out.println("Create completed")
    );
```

### List Keys Async

```java
keyAsyncClient.listPropertiesOfKeys()
    .subscribe(keyProperties -> {
        System.out.printf("Key: %s%n", keyProperties.getName());
    });
```

### Encrypt/Decrypt Async

```java
byte[] plaintext = "Hello, async!".getBytes();

cryptographyAsyncClient.encrypt(EncryptionAlgorithm.RSA_OAEP, plaintext)
    .flatMap(encryptResult -> {
        System.out.printf("Encrypted: %d bytes%n", encryptResult.getCipherText().length);
        return cryptographyAsyncClient.decrypt(
            EncryptionAlgorithm.RSA_OAEP, 
            encryptResult.getCipherText()
        );
    })
    .subscribe(
        decryptResult -> System.out.printf("Decrypted: %s%n", 
            new String(decryptResult.getPlainText())),
        error -> System.err.println("Error: " + error.getMessage())
    );
```

## Error Handling

```java
import com.azure.core.exception.HttpResponseException;
import com.azure.core.exception.ResourceNotFoundException;

try {
    KeyVaultKey key = keyClient.getKey("nonexistent-key");
} catch (ResourceNotFoundException e) {
    System.err.println("Key not found: " + e.getMessage());
} catch (HttpResponseException e) {
    System.err.println("HTTP error: " + e.getResponse().getStatusCode());
    System.err.println("Message: " + e.getMessage());
} catch (Exception e) {
    System.err.println("Unexpected error: " + e.getMessage());
}
```

### Async Error Handling

```java
keyAsyncClient.getKey("nonexistent-key")
    .subscribe(
        key -> System.out.println("Key: " + key.getName()),
        error -> {
            if (error instanceof ResourceNotFoundException) {
                System.err.println("Key not found");
            } else if (error instanceof HttpResponseException) {
                HttpResponseException httpError = (HttpResponseException) error;
                System.err.println("HTTP error: " + httpError.getResponse().getStatusCode());
            } else {
                System.err.println("Error: " + error.getMessage());
            }
        }
    );
```
