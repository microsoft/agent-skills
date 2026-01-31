# Azure Key Vault Keys SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-security-keyvault-keys`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/keyvault/azure-security-keyvault-keys
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: KeyClient and CryptographyClient Imports
```java
import com.azure.security.keyvault.keys.KeyClient;
import com.azure.security.keyvault.keys.KeyClientBuilder;
import com.azure.security.keyvault.keys.KeyAsyncClient;
import com.azure.security.keyvault.keys.cryptography.CryptographyClient;
import com.azure.security.keyvault.keys.cryptography.CryptographyClientBuilder;
```
#### ❌ INCORRECT: Wrong Package or Class Names
```java
import com.azure.keyvault.keys.KeyClient;  // Wrong package
import com.azure.security.keyvault.KeyClient;  // Missing keys
import com.azure.security.keyvault.keys.KeyVaultClient;  // Wrong class name
```

### 1.2 Model Imports
#### ✅ CORRECT: Key Models
```java
import com.azure.security.keyvault.keys.models.KeyVaultKey;
import com.azure.security.keyvault.keys.models.CreateRsaKeyOptions;
import com.azure.security.keyvault.keys.models.CreateEcKeyOptions;
import com.azure.security.keyvault.keys.models.CreateOctKeyOptions;
import com.azure.security.keyvault.keys.models.KeyProperties;
import com.azure.security.keyvault.keys.models.KeyOperation;
import com.azure.security.keyvault.keys.models.KeyCurveName;
import com.azure.security.keyvault.keys.models.DeletedKey;
import com.azure.security.keyvault.keys.models.KeyRotationPolicy;
```
#### ❌ INCORRECT: Wrong Model Names
```java
import com.azure.security.keyvault.keys.models.Key;  // Wrong name
import com.azure.security.keyvault.keys.models.RsaKeyOptions;  // Wrong name
```

### 1.3 Cryptography Model Imports
#### ✅ CORRECT: Cryptography Operation Models
```java
import com.azure.security.keyvault.keys.cryptography.models.EncryptionAlgorithm;
import com.azure.security.keyvault.keys.cryptography.models.EncryptResult;
import com.azure.security.keyvault.keys.cryptography.models.DecryptResult;
import com.azure.security.keyvault.keys.cryptography.models.SignatureAlgorithm;
import com.azure.security.keyvault.keys.cryptography.models.SignResult;
import com.azure.security.keyvault.keys.cryptography.models.VerifyResult;
import com.azure.security.keyvault.keys.cryptography.models.KeyWrapAlgorithm;
import com.azure.security.keyvault.keys.cryptography.models.WrapResult;
import com.azure.security.keyvault.keys.cryptography.models.UnwrapResult;
```

---

## 2. Client Creation Patterns

### 2.1 KeyClient Creation
#### ✅ CORRECT: Using VaultUrl and Credential
```java
import com.azure.identity.DefaultAzureCredentialBuilder;

KeyClient keyClient = new KeyClientBuilder()
    .vaultUrl("https://<vault-name>.vault.azure.net")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```
#### ❌ INCORRECT: Missing VaultUrl or Wrong Method
```java
KeyClient keyClient = new KeyClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();  // Missing vaultUrl

KeyClient keyClient = new KeyClientBuilder()
    .endpoint("https://<vault-name>.vault.azure.net")  // Wrong method name
    .credential(credential)
    .buildClient();
```

### 2.2 KeyAsyncClient Creation
#### ✅ CORRECT: Building Async Client
```java
KeyAsyncClient keyAsyncClient = new KeyClientBuilder()
    .vaultUrl("https://<vault-name>.vault.azure.net")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncClient();
```
#### ❌ INCORRECT: Wrong Build Method
```java
KeyAsyncClient keyAsyncClient = new KeyClientBuilder()
    .vaultUrl("https://vault.vault.azure.net")
    .credential(credential)
    .buildClient();  // Returns sync client
```

### 2.3 CryptographyClient Creation
#### ✅ CORRECT: Using Key Identifier
```java
CryptographyClient cryptoClient = new CryptographyClientBuilder()
    .keyIdentifier("https://<vault-name>.vault.azure.net/keys/<key-name>/<key-version>")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```
#### ❌ INCORRECT: Wrong Method Names
```java
CryptographyClient cryptoClient = new CryptographyClientBuilder()
    .keyUrl("...")  // Wrong method name
    .credential(credential)
    .buildClient();

CryptographyClient cryptoClient = new CryptographyClientBuilder()
    .vaultUrl("...")  // Should be keyIdentifier
    .keyName("...")
    .buildClient();
```

---

## 3. Create Key Operations

### 3.1 Create RSA Key
#### ✅ CORRECT: Using CreateRsaKeyOptions
```java
KeyVaultKey rsaKey = keyClient.createRsaKey(new CreateRsaKeyOptions("my-rsa-key")
    .setKeySize(2048));

System.out.println("Key name: " + rsaKey.getName());
System.out.println("Key ID: " + rsaKey.getId());
System.out.println("Key type: " + rsaKey.getKeyType());
```
#### ❌ INCORRECT: Wrong Method or Missing Options
```java
keyClient.createKey("my-rsa-key", KeyType.RSA);  // Less specific method
keyClient.createRsaKey("my-rsa-key");  // Missing options object
```

### 3.2 RSA Key with Options
#### ✅ CORRECT: Full Options Configuration
```java
KeyVaultKey rsaKey = keyClient.createRsaKey(new CreateRsaKeyOptions("my-rsa-key")
    .setKeySize(4096)
    .setExpiresOn(OffsetDateTime.now().plusYears(1))
    .setNotBefore(OffsetDateTime.now())
    .setEnabled(true)
    .setKeyOperations(KeyOperation.ENCRYPT, KeyOperation.DECRYPT, 
                       KeyOperation.WRAP_KEY, KeyOperation.UNWRAP_KEY)
    .setTags(Map.of("environment", "production")));
```
#### ❌ INCORRECT: Wrong Key Size or Operation Names
```java
new CreateRsaKeyOptions("key")
    .setKeySize(1024);  // Too small, minimum is 2048

new CreateRsaKeyOptions("key")
    .setKeyOperations(KeyOperation.SIGN);  // RSA signing requires different options
```

### 3.3 HSM-Backed RSA Key
#### ✅ CORRECT: Setting Hardware Protection
```java
KeyVaultKey hsmKey = keyClient.createRsaKey(new CreateRsaKeyOptions("my-hsm-key")
    .setKeySize(2048)
    .setHardwareProtected(true));
```

### 3.4 Create EC Key
#### ✅ CORRECT: Using CreateEcKeyOptions with Curve
```java
KeyVaultKey ecKey = keyClient.createEcKey(new CreateEcKeyOptions("my-ec-key")
    .setCurveName(KeyCurveName.P_256));

KeyVaultKey ecKey384 = keyClient.createEcKey(new CreateEcKeyOptions("my-ec-key-384")
    .setCurveName(KeyCurveName.P_384));
```
#### ❌ INCORRECT: String Curve Name
```java
new CreateEcKeyOptions("key").setCurveName("P-256");  // Should be KeyCurveName enum
```

### 3.5 Create Symmetric Key (Managed HSM Only)
#### ✅ CORRECT: Using CreateOctKeyOptions
```java
KeyVaultKey octKey = keyClient.createOctKey(new CreateOctKeyOptions("my-symmetric-key")
    .setKeySize(256)
    .setHardwareProtected(true));
```

---

## 4. Get and List Key Operations

### 4.1 Get Key
#### ✅ CORRECT: Get Latest or Specific Version
```java
// Get latest version
KeyVaultKey key = keyClient.getKey("my-key");

// Get specific version
KeyVaultKey keyVersion = keyClient.getKey("my-key", "<version-id>");
```
#### ❌ INCORRECT: Wrong Parameter Types
```java
keyClient.getKey(123);  // Should be String name
```

### 4.2 List Keys
#### ✅ CORRECT: Iterating Key Properties
```java
for (KeyProperties keyProps : keyClient.listPropertiesOfKeys()) {
    System.out.println("Key: " + keyProps.getName());
    System.out.println("  Enabled: " + keyProps.isEnabled());
    System.out.println("  Created: " + keyProps.getCreatedOn());
}
```
#### ❌ INCORRECT: Expecting Full Key Object
```java
for (KeyVaultKey key : keyClient.listKeys()) {  // Wrong method name
    // listPropertiesOfKeys returns KeyProperties, not KeyVaultKey
}
```

### 4.3 List Key Versions
#### ✅ CORRECT: Listing Versions
```java
for (KeyProperties version : keyClient.listPropertiesOfKeyVersions("my-key")) {
    System.out.println("Version: " + version.getVersion());
    System.out.println("Created: " + version.getCreatedOn());
}
```

---

## 5. Update Key Operations

### 5.1 Update Key Properties
#### ✅ CORRECT: Modify and Update Properties
```java
KeyVaultKey key = keyClient.getKey("my-key");

key.getProperties()
    .setEnabled(false)
    .setExpiresOn(OffsetDateTime.now().plusMonths(6))
    .setTags(Map.of("status", "archived"));

KeyVaultKey updatedKey = keyClient.updateKeyProperties(key.getProperties(),
    KeyOperation.ENCRYPT, KeyOperation.DECRYPT);
```
#### ❌ INCORRECT: Direct Value Update
```java
key.setEnabled(false);  // KeyVaultKey doesn't have setters
keyClient.updateKey(key);  // Wrong method name
```

---

## 6. Delete Key Operations

### 6.1 Begin Delete Key
#### ✅ CORRECT: Using SyncPoller
```java
import com.azure.core.util.polling.SyncPoller;

SyncPoller<DeletedKey, Void> deletePoller = keyClient.beginDeleteKey("my-key");

DeletedKey deletedKey = deletePoller.poll().getValue();
System.out.println("Deleted: " + deletedKey.getDeletedOn());

deletePoller.waitForCompletion();
```
#### ❌ INCORRECT: Synchronous Delete Call
```java
keyClient.deleteKey("my-key");  // Method doesn't exist, must use beginDeleteKey
```

### 6.2 Purge Deleted Key
#### ✅ CORRECT: Permanent Deletion
```java
keyClient.purgeDeletedKey("my-key");
```

### 6.3 Recover Deleted Key
#### ✅ CORRECT: Using SyncPoller for Recovery
```java
SyncPoller<KeyVaultKey, Void> recoverPoller = keyClient.beginRecoverDeletedKey("my-key");
recoverPoller.waitForCompletion();
```

---

## 7. Cryptographic Operations

### 7.1 Encrypt/Decrypt
#### ✅ CORRECT: Using EncryptionAlgorithm Enum
```java
byte[] plaintext = "Hello, World!".getBytes(StandardCharsets.UTF_8);

// Encrypt
EncryptResult encryptResult = cryptoClient.encrypt(EncryptionAlgorithm.RSA_OAEP, plaintext);
byte[] ciphertext = encryptResult.getCipherText();

// Decrypt
DecryptResult decryptResult = cryptoClient.decrypt(EncryptionAlgorithm.RSA_OAEP, ciphertext);
String decrypted = new String(decryptResult.getPlainText(), StandardCharsets.UTF_8);
```
#### ❌ INCORRECT: String Algorithm
```java
cryptoClient.encrypt("RSA-OAEP", plaintext);  // Should be EncryptionAlgorithm enum
```

### 7.2 Sign/Verify
#### ✅ CORRECT: Sign Digest with SignatureAlgorithm
```java
import java.security.MessageDigest;

byte[] data = "Data to sign".getBytes(StandardCharsets.UTF_8);
MessageDigest md = MessageDigest.getInstance("SHA-256");
byte[] digest = md.digest(data);

// Sign
SignResult signResult = cryptoClient.sign(SignatureAlgorithm.RS256, digest);
byte[] signature = signResult.getSignature();

// Verify
VerifyResult verifyResult = cryptoClient.verify(SignatureAlgorithm.RS256, digest, signature);
System.out.println("Valid signature: " + verifyResult.isValid());
```
#### ❌ INCORRECT: Signing Raw Data
```java
// Don't sign raw data, sign the digest
cryptoClient.sign(SignatureAlgorithm.RS256, rawData);  // Should be digest
```

### 7.3 Wrap/Unwrap Key
#### ✅ CORRECT: Key Wrapping Operations
```java
byte[] keyToWrap = new byte[32];
new SecureRandom().nextBytes(keyToWrap);

// Wrap
WrapResult wrapResult = cryptoClient.wrapKey(KeyWrapAlgorithm.RSA_OAEP, keyToWrap);
byte[] wrappedKey = wrapResult.getEncryptedKey();

// Unwrap
UnwrapResult unwrapResult = cryptoClient.unwrapKey(KeyWrapAlgorithm.RSA_OAEP, wrappedKey);
byte[] unwrappedKey = unwrapResult.getKey();
```

---

## 8. Key Rotation

### 8.1 Rotate Key
#### ✅ CORRECT: Creating New Version
```java
KeyVaultKey rotatedKey = keyClient.rotateKey("my-key");
System.out.println("New version: " + rotatedKey.getProperties().getVersion());
```

### 8.2 Set Rotation Policy
#### ✅ CORRECT: Configuring Rotation Policy
```java
KeyRotationPolicy policy = new KeyRotationPolicy()
    .setExpiresIn("P90D")
    .setLifetimeActions(Arrays.asList(
        new KeyRotationLifetimeAction(KeyRotationPolicyAction.ROTATE)
            .setTimeBeforeExpiry("P30D")));

keyClient.updateKeyRotationPolicy("my-key", policy);
```
#### ❌ INCORRECT: Wrong Duration Format
```java
new KeyRotationPolicy().setExpiresIn("90 days");  // Should be ISO 8601 duration (P90D)
```

---

## 9. Backup and Restore

### 9.1 Backup Key
#### ✅ CORRECT: Backup to Byte Array
```java
byte[] backup = keyClient.backupKey("my-key");
Files.write(Paths.get("key-backup.blob"), backup);
```

### 9.2 Restore Key
#### ✅ CORRECT: Restore from Backup
```java
byte[] backupData = Files.readAllBytes(Paths.get("key-backup.blob"));
KeyVaultKey restoredKey = keyClient.restoreKeyBackup(backupData);
```

---

## 10. Error Handling

### 10.1 Exception Handling
#### ✅ CORRECT: Specific Exception Types
```java
import com.azure.core.exception.HttpResponseException;
import com.azure.core.exception.ResourceNotFoundException;

try {
    KeyVaultKey key = keyClient.getKey("non-existent-key");
} catch (ResourceNotFoundException e) {
    System.out.println("Key not found: " + e.getMessage());
} catch (HttpResponseException e) {
    System.out.println("HTTP error " + e.getResponse().getStatusCode());
    System.out.println("Message: " + e.getMessage());
}
```
#### ❌ INCORRECT: Generic Exception Only
```java
try {
    KeyVaultKey key = keyClient.getKey("key");
} catch (Exception e) {
    // Missing specific error handling
}
```

---

## 11. Algorithm Reference

### 11.1 Encryption Algorithms
#### ✅ CORRECT: Using Appropriate Algorithms
```java
// RSA algorithms
EncryptionAlgorithm.RSA1_5      // RSAES-PKCS1-v1_5
EncryptionAlgorithm.RSA_OAEP    // RSAES with OAEP (recommended)
EncryptionAlgorithm.RSA_OAEP_256 // RSAES with OAEP using SHA-256

// Symmetric algorithms (Managed HSM only)
EncryptionAlgorithm.A128GCM     // AES-GCM 128-bit
EncryptionAlgorithm.A256GCM     // AES-GCM 256-bit
```

### 11.2 Signature Algorithms
#### ✅ CORRECT: RSA and EC Signature Algorithms
```java
// RSA algorithms
SignatureAlgorithm.RS256  // RSA with SHA-256
SignatureAlgorithm.RS384  // RSA with SHA-384
SignatureAlgorithm.RS512  // RSA with SHA-512
SignatureAlgorithm.PS256  // RSA-PSS with SHA-256

// EC algorithms
SignatureAlgorithm.ES256  // ECDSA with P-256 and SHA-256
SignatureAlgorithm.ES384  // ECDSA with P-384 and SHA-384
SignatureAlgorithm.ES512  // ECDSA with P-521 and SHA-512
```