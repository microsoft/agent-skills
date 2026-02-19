# Azure Key Vault Keys SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-security-keyvault-keys`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/keyvault-v2/azure-security-keyvault-keys
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Key and Cryptography Clients
```java
import com.azure.security.keyvault.keys.KeyClient;
import com.azure.security.keyvault.keys.KeyClientBuilder;
import com.azure.security.keyvault.keys.KeyAsyncClient;
import com.azure.security.keyvault.keys.cryptography.CryptographyClient;
import com.azure.security.keyvault.keys.cryptography.CryptographyClientBuilder;
```

#### ✅ CORRECT: Authentication
```java
import com.azure.identity.DefaultAzureCredentialBuilder;
```

### 1.2 Model Imports

#### ✅ CORRECT: Key Models
```java
import com.azure.security.keyvault.keys.models.KeyVaultKey;
import com.azure.security.keyvault.keys.models.KeyProperties;
import com.azure.security.keyvault.keys.models.CreateRsaKeyOptions;
import com.azure.security.keyvault.keys.models.CreateEcKeyOptions;
import com.azure.security.keyvault.keys.models.KeyOperation;
import com.azure.security.keyvault.keys.models.KeyCurveName;
import com.azure.security.keyvault.keys.models.DeletedKey;
```

#### ✅ CORRECT: Cryptography Models
```java
import com.azure.security.keyvault.keys.cryptography.models.EncryptionAlgorithm;
import com.azure.security.keyvault.keys.cryptography.models.EncryptResult;
import com.azure.security.keyvault.keys.cryptography.models.DecryptResult;
import com.azure.security.keyvault.keys.cryptography.models.SignatureAlgorithm;
import com.azure.security.keyvault.keys.cryptography.models.SignResult;
import com.azure.security.keyvault.keys.cryptography.models.VerifyResult;
import com.azure.security.keyvault.keys.cryptography.models.KeyWrapAlgorithm;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: KeyClient with DefaultAzureCredential
```java
String vaultUrl = System.getenv("AZURE_KEYVAULT_URL");

KeyClient keyClient = new KeyClientBuilder()
    .vaultUrl(vaultUrl)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### 2.2 ✅ CORRECT: CryptographyClient
```java
CryptographyClient cryptoClient = new CryptographyClientBuilder()
    .keyIdentifier(vaultUrl + "/keys/my-key")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

---

## 3. Key Operations

### 3.1 ✅ CORRECT: Create RSA Key
```java
KeyVaultKey rsaKey = keyClient.createRsaKey(new CreateRsaKeyOptions("my-rsa-key")
    .setKeySize(2048)
    .setKeyOperations(KeyOperation.ENCRYPT, KeyOperation.DECRYPT));
```

### 3.2 ✅ CORRECT: Create EC Key
```java
KeyVaultKey ecKey = keyClient.createEcKey(new CreateEcKeyOptions("my-ec-key")
    .setCurveName(KeyCurveName.P_256));
```

### 3.3 ✅ CORRECT: Get and List Keys
```java
KeyVaultKey key = keyClient.getKey("my-key");

for (KeyProperties keyProps : keyClient.listPropertiesOfKeys()) {
    System.out.println("Key: " + keyProps.getName());
}
```

### 3.4 ✅ CORRECT: Delete Key
```java
SyncPoller<DeletedKey, Void> deletePoller = keyClient.beginDeleteKey("my-key");
deletePoller.waitForCompletion();
```

---

## 4. Cryptographic Operations

### 4.1 ✅ CORRECT: Encrypt/Decrypt
```java
byte[] plaintext = "Hello, World!".getBytes(StandardCharsets.UTF_8);

EncryptResult encryptResult = cryptoClient.encrypt(EncryptionAlgorithm.RSA_OAEP, plaintext);
byte[] ciphertext = encryptResult.getCipherText();

DecryptResult decryptResult = cryptoClient.decrypt(EncryptionAlgorithm.RSA_OAEP, ciphertext);
String decrypted = new String(decryptResult.getPlainText(), StandardCharsets.UTF_8);
```

### 4.2 ✅ CORRECT: Sign/Verify
```java
byte[] digest = MessageDigest.getInstance("SHA-256").digest(data);

SignResult signResult = cryptoClient.sign(SignatureAlgorithm.RS256, digest);
byte[] signature = signResult.getSignature();

VerifyResult verifyResult = cryptoClient.verify(SignatureAlgorithm.RS256, digest, signature);
System.out.println("Valid: " + verifyResult.isValid());
```

---

## 5. Error Handling

### 5.1 ✅ CORRECT: Exception Handling
```java
import com.azure.core.exception.HttpResponseException;
import com.azure.core.exception.ResourceNotFoundException;

try {
    keyClient.getKey("non-existent-key");
} catch (ResourceNotFoundException e) {
    System.out.println("Key not found");
} catch (HttpResponseException e) {
    System.out.println("HTTP error: " + e.getResponse().getStatusCode());
}
```

---

## 6. Best Practices Checklist

- [ ] Use DefaultAzureCredential for authentication
- [ ] Use environment variables for vault URL
- [ ] Use HSM keys for production (`setHardwareProtected(true)`)
- [ ] Enable soft delete on vault
- [ ] Set up key rotation policies
- [ ] Use separate keys for different operations
