# Azure Key Vault Keys SDK Acceptance Criteria (.NET)

**SDK**: `Azure.Security.KeyVault.Keys`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/keyvault/Azure.Security.KeyVault.Keys
**NuGet Package**: https://www.nuget.org/packages/Azure.Security.KeyVault.Keys/
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Imports

### 1.1 ✅ CORRECT: Client Imports
```csharp
using Azure.Security.KeyVault.Keys;
using Azure.Security.KeyVault.Keys.Cryptography;
using Azure.Identity;
```

### 1.2 ✅ CORRECT: Model Imports for Key Options
```csharp
using Azure.Security.KeyVault.Keys;
// CreateRsaKeyOptions, CreateEcKeyOptions, etc. are in the main namespace
```

### 1.3 ❌ INCORRECT: Wrong import paths
```csharp
// WRONG - Cryptography client is in .Cryptography namespace
using Azure.Security.KeyVault.Keys;
var cryptoClient = new CryptographyClient(keyId, credential); // CryptographyClient not imported

// WRONG - Using old Microsoft.Azure.KeyVault package
using Microsoft.Azure.KeyVault;

// WRONG - Using KeyVault.Secrets namespace for keys
using Azure.Security.KeyVault.Secrets;
```

---

## 2. Authentication

### 2.1 ✅ CORRECT: DefaultAzureCredential (Recommended)
```csharp
var client = new KeyClient(
    vaultUri: new Uri("https://my-vault.vault.azure.net/"),
    credential: new DefaultAzureCredential());
```

### 2.2 ✅ CORRECT: Environment Variables for Vault URI
```csharp
string vaultUrl = Environment.GetEnvironmentVariable("AZURE_KEYVAULT_URL")
    ?? throw new InvalidOperationException("AZURE_KEYVAULT_URL not set");

var client = new KeyClient(new Uri(vaultUrl), new DefaultAzureCredential());
```

### 2.3 ❌ INCORRECT: Hardcoded vault URL or credentials
```csharp
// WRONG - hardcoded vault URL in production code
var client = new KeyClient(
    vaultUri: new Uri("https://production-vault.vault.azure.net/"),
    credential: new DefaultAzureCredential());

// WRONG - using deprecated authentication
var client = new KeyClient(
    vaultUri: new Uri(vaultUrl),
    credential: new InteractiveBrowserCredential()); // Not recommended for production
```

---

## 3. KeyClient Operations

### 3.1 ✅ CORRECT: Create RSA Key (Sync)
```csharp
// Create a basic RSA key
KeyVaultKey key = client.CreateKey("rsa-key-name", KeyType.Rsa);

Console.WriteLine(key.Name);
Console.WriteLine(key.KeyType);

// Create with specific options
var rsaOptions = new CreateRsaKeyOptions("rsa-key-with-options", hardwareProtected: false)
{
    KeySize = 2048,
    ExpiresOn = DateTimeOffset.UtcNow.AddYears(1)
};
KeyVaultKey rsaKey = client.CreateRsaKey(rsaOptions);
```

### 3.2 ✅ CORRECT: Create EC Key (Sync)
```csharp
var ecOptions = new CreateEcKeyOptions("ec-key-name", hardwareProtected: false)
{
    CurveName = KeyCurveName.P256
};
KeyVaultKey ecKey = client.CreateEcKey(ecOptions);
```

### 3.3 ✅ CORRECT: Retrieve Key
```csharp
KeyVaultKey key = client.GetKey("key-name");

Console.WriteLine(key.Name);
Console.WriteLine(key.KeyType);
Console.WriteLine(key.Properties.Version);
```

### 3.4 ✅ CORRECT: Update Key Properties
```csharp
KeyVaultKey key = client.GetKey("key-name");

// Modify properties
key.Properties.Tags["environment"] = "production";
key.Properties.ExpiresOn = DateTimeOffset.UtcNow.AddYears(2);

KeyVaultKey updatedKey = client.UpdateKeyProperties(key.Properties);
```

### 3.5 ✅ CORRECT: List Keys
```csharp
Pageable<KeyProperties> allKeys = client.GetPropertiesOfKeys();

foreach (KeyProperties keyProperties in allKeys)
{
    Console.WriteLine(keyProperties.Name);
}
```

### 3.6 ✅ CORRECT: Delete and Purge Key
```csharp
DeleteKeyOperation operation = client.StartDeleteKey("key-name");

// Wait for completion before purging
while (!operation.HasCompleted)
{
    Thread.Sleep(2000);
    operation.UpdateStatus();
}

DeletedKey deletedKey = operation.Value;
Console.WriteLine($"Deleted: {deletedKey.Name} on {deletedKey.DeletedOn}");

// Purge if soft-delete is enabled
client.PurgeDeletedKey(deletedKey.Name);
```

### 3.7 ❌ INCORRECT: Not waiting for delete operation
```csharp
// WRONG - attempting to purge without waiting for delete to complete
DeleteKeyOperation operation = client.StartDeleteKey("key-name");
client.PurgeDeletedKey("key-name"); // Will fail - key not yet deleted
```

---

## 4. CryptographyClient Operations

### 4.1 ✅ CORRECT: Get CryptographyClient from KeyClient
```csharp
KeyVaultKey key = client.CreateKey("crypto-key", KeyType.Rsa);

// Get CryptographyClient from the KeyClient (recommended)
CryptographyClient cryptoClient = client.GetCryptographyClient(key.Name, key.Properties.Version);
```

### 4.2 ✅ CORRECT: Encrypt and Decrypt
```csharp
byte[] plaintext = Encoding.UTF8.GetBytes("Sensitive data to encrypt");

// Encrypt
EncryptResult encryptResult = cryptoClient.Encrypt(EncryptionAlgorithm.RsaOaep256, plaintext);
byte[] ciphertext = encryptResult.Ciphertext;

// Decrypt
DecryptResult decryptResult = cryptoClient.Decrypt(EncryptionAlgorithm.RsaOaep256, ciphertext);
string decryptedText = Encoding.UTF8.GetString(decryptResult.Plaintext);
```

### 4.3 ✅ CORRECT: Sign and Verify
```csharp
// For signing, you typically sign a hash (digest) of the data
byte[] data = Encoding.UTF8.GetBytes("Data to sign");
using var sha256 = SHA256.Create();
byte[] digest = sha256.ComputeHash(data);

// Sign the digest
SignResult signResult = cryptoClient.Sign(SignatureAlgorithm.RS256, digest);
byte[] signature = signResult.Signature;

// Verify the signature
VerifyResult verifyResult = cryptoClient.Verify(SignatureAlgorithm.RS256, digest, signature);
Console.WriteLine($"Signature valid: {verifyResult.IsValid}");
```

### 4.4 ✅ CORRECT: Wrap and Unwrap Key
```csharp
byte[] keyToWrap = new byte[32]; // e.g., AES-256 key
RandomNumberGenerator.Fill(keyToWrap);

// Wrap the key
WrapResult wrapResult = cryptoClient.WrapKey(KeyWrapAlgorithm.RsaOaep256, keyToWrap);
byte[] wrappedKey = wrapResult.EncryptedKey;

// Unwrap the key
UnwrapResult unwrapResult = cryptoClient.UnwrapKey(KeyWrapAlgorithm.RsaOaep256, wrappedKey);
byte[] unwrappedKey = unwrapResult.Key;
```

### 4.5 ❌ INCORRECT: Wrong algorithm for key type
```csharp
// WRONG - Using RSA algorithm with EC key
KeyVaultKey ecKey = client.CreateEcKey(new CreateEcKeyOptions("ec-key"));
CryptographyClient cryptoClient = client.GetCryptographyClient(ecKey.Name, ecKey.Properties.Version);

// This will fail - RSA-OAEP doesn't work with EC keys
EncryptResult result = cryptoClient.Encrypt(EncryptionAlgorithm.RsaOaep, plaintext);
```

---

## 5. Async Variants

### 5.1 ✅ CORRECT: Async Key Operations
```csharp
// Create key asynchronously
KeyVaultKey key = await client.CreateKeyAsync("async-key", KeyType.Rsa);

// Get key asynchronously
key = await client.GetKeyAsync("async-key");

// List keys asynchronously
AsyncPageable<KeyProperties> allKeys = client.GetPropertiesOfKeysAsync();
await foreach (KeyProperties keyProperties in allKeys)
{
    Console.WriteLine(keyProperties.Name);
}
```

### 5.2 ✅ CORRECT: Async Delete with WaitForCompletion
```csharp
DeleteKeyOperation operation = await client.StartDeleteKeyAsync("key-name");

// Wait for completion asynchronously
await operation.WaitForCompletionAsync();

DeletedKey key = operation.Value;
await client.PurgeDeletedKeyAsync(key.Name);
```

### 5.3 ✅ CORRECT: Async Cryptography Operations
```csharp
EncryptResult encryptResult = await cryptoClient.EncryptAsync(
    EncryptionAlgorithm.RsaOaep256, plaintext);

DecryptResult decryptResult = await cryptoClient.DecryptAsync(
    EncryptionAlgorithm.RsaOaep256, encryptResult.Ciphertext);
```

---

## 6. Error Handling

### 6.1 ✅ CORRECT: Handle RequestFailedException
```csharp
try
{
    KeyVaultKey key = await client.GetKeyAsync("non-existent-key");
}
catch (RequestFailedException ex) when (ex.Status == 404)
{
    Console.WriteLine($"Key not found: {ex.Message}");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Key Vault error: {ex.Status} - {ex.Message}");
}
```

### 6.2 ❌ INCORRECT: Swallowing exceptions
```csharp
// WRONG - empty catch block hides errors
try
{
    KeyVaultKey key = await client.GetKeyAsync("key-name");
}
catch (Exception)
{
    // Silent failure
}
```

---

## 7. Best Practices

### 7.1 ✅ CORRECT: Reuse Client Instance
```csharp
// Create once and reuse - clients are thread-safe
public class KeyVaultService
{
    private readonly KeyClient _client;

    public KeyVaultService(string vaultUrl)
    {
        _client = new KeyClient(new Uri(vaultUrl), new DefaultAzureCredential());
    }

    public async Task<KeyVaultKey> GetKeyAsync(string keyName) =>
        await _client.GetKeyAsync(keyName);
}
```

### 7.2 ✅ CORRECT: Use Key Versioning
```csharp
// List all versions of a key
AsyncPageable<KeyProperties> versions = client.GetPropertiesOfKeyVersionsAsync("key-name");

await foreach (KeyProperties version in versions)
{
    Console.WriteLine($"Version: {version.Version}, Created: {version.CreatedOn}");
}

// Get specific version
KeyVaultKey specificVersion = await client.GetKeyAsync("key-name", "version-id");
```

### 7.3 ❌ INCORRECT: Creating new client for each operation
```csharp
// WRONG - wasteful to create new client for each operation
public async Task<KeyVaultKey> GetKey(string keyName)
{
    var client = new KeyClient(new Uri(vaultUrl), new DefaultAzureCredential());
    return await client.GetKeyAsync(keyName);
}
```

---

## 8. HSM-Protected Keys

### 8.1 ✅ CORRECT: Create HSM-Protected Key
```csharp
// Requires Premium tier Azure Key Vault
var rsaHsmOptions = new CreateRsaKeyOptions("rsa-hsm-key", hardwareProtected: true)
{
    KeySize = 2048
};
KeyVaultKey hsmKey = await client.CreateRsaKeyAsync(rsaHsmOptions);

// Verify it's HSM-protected
Console.WriteLine($"Key Type: {hsmKey.KeyType}"); // Should be "RSA-HSM"
```

### 8.2 ❌ INCORRECT: Assuming HSM without Premium tier
```csharp
// WRONG - HSM keys require Premium tier; this will fail on Standard tier
var hsmOptions = new CreateRsaKeyOptions("hsm-key", hardwareProtected: true);
KeyVaultKey key = await client.CreateRsaKeyAsync(hsmOptions); // Fails on Standard tier
```
