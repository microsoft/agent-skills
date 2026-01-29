# Azure Identity SDK for Java - Examples

Comprehensive code examples for the Azure Identity SDK for Java.

## Table of Contents
- [Maven Dependency](#maven-dependency)
- [DefaultAzureCredential](#defaultazurecredential)
- [ChainedTokenCredential](#chainedtokencredential)
- [ClientSecretCredential](#clientsecretcredential)
- [ClientCertificateCredential](#clientcertificatecredential)
- [ManagedIdentityCredential](#managedidentitycredential)
- [EnvironmentCredential](#environmentcredential)
- [InteractiveBrowserCredential](#interactivebrowsercredential)
- [DeviceCodeCredential](#devicecodecredential)
- [AzureCliCredential](#azureclicredential)
- [Using Credentials with Azure SDK Clients](#using-credentials-with-azure-sdk-clients)

## Maven Dependency

```xml
<!-- Using Azure SDK BOM (recommended) -->
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.azure</groupId>
            <artifactId>azure-sdk-bom</artifactId>
            <version>1.2.29</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <dependency>
        <groupId>com.azure</groupId>
        <artifactId>azure-identity</artifactId>
    </dependency>
</dependencies>

<!-- Or direct dependency -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
    <version>1.18.2</version>
</dependency>
```

## DefaultAzureCredential

The recommended credential for most scenarios. Tries multiple authentication methods in order.

### Basic Usage

```java
import com.azure.identity.DefaultAzureCredential;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.security.keyvault.secrets.SecretClient;
import com.azure.security.keyvault.secrets.SecretClientBuilder;

// Basic usage
DefaultAzureCredential credential = new DefaultAzureCredentialBuilder().build();

// Use with Azure SDK clients
SecretClient client = new SecretClientBuilder()
    .vaultUrl("https://{YOUR_VAULT_NAME}.vault.azure.net")
    .credential(credential)
    .buildClient();
```

### With User-Assigned Managed Identity

```java
DefaultAzureCredential credential = new DefaultAzureCredentialBuilder()
    .managedIdentityClientId("<MANAGED_IDENTITY_CLIENT_ID>")
    .build();

SecretClient client = new SecretClientBuilder()
    .vaultUrl("https://{YOUR_VAULT_NAME}.vault.azure.net")
    .credential(credential)
    .buildClient();
```

### Authentication Order

DefaultAzureCredential tries these methods in order:
1. EnvironmentCredential
2. WorkloadIdentityCredential
3. ManagedIdentityCredential
4. AzureDeveloperCliCredential
5. IntelliJCredential
6. AzureCliCredential
7. AzurePowerShellCredential

## ChainedTokenCredential

Create a custom chain of credentials to try in sequence.

### Managed Identity with Interactive Browser Fallback

```java
import com.azure.identity.ChainedTokenCredential;
import com.azure.identity.ChainedTokenCredentialBuilder;
import com.azure.identity.ManagedIdentityCredential;
import com.azure.identity.ManagedIdentityCredentialBuilder;
import com.azure.identity.InteractiveBrowserCredential;
import com.azure.identity.InteractiveBrowserCredentialBuilder;

ManagedIdentityCredential managedIdentityCredential = new ManagedIdentityCredentialBuilder().build();
InteractiveBrowserCredential interactiveBrowserCredential = new InteractiveBrowserCredentialBuilder()
    .clientId(clientId)
    .redirectUrl("https://localhost:8765")
    .build();

ChainedTokenCredential credential = new ChainedTokenCredentialBuilder()
    .addLast(managedIdentityCredential)
    .addLast(interactiveBrowserCredential)
    .build();
```

### Azure CLI with IntelliJ for Development

```java
import com.azure.identity.AzureCliCredential;
import com.azure.identity.AzureCliCredentialBuilder;
import com.azure.identity.IntelliJCredential;
import com.azure.identity.IntelliJCredentialBuilder;

AzureCliCredential cliCredential = new AzureCliCredentialBuilder().build();
IntelliJCredential ijCredential = new IntelliJCredentialBuilder().build();

ChainedTokenCredential credential = new ChainedTokenCredentialBuilder()
    .addLast(cliCredential)
    .addLast(ijCredential)
    .build();
```

## ClientSecretCredential

Authenticate a service principal using a client secret.

### Basic Usage

```java
import com.azure.identity.ClientSecretCredential;
import com.azure.identity.ClientSecretCredentialBuilder;

String tenantId = System.getenv("AZURE_TENANT_ID");
String clientId = System.getenv("AZURE_CLIENT_ID");
String clientSecret = System.getenv("AZURE_CLIENT_SECRET");

ClientSecretCredential credential = new ClientSecretCredentialBuilder()
    .tenantId(tenantId)
    .clientId(clientId)
    .clientSecret(clientSecret)
    .build();

SecretClient client = new SecretClientBuilder()
    .vaultUrl("https://{YOUR_VAULT_NAME}.vault.azure.net")
    .credential(credential)
    .buildClient();
```

### With Proxy Configuration

```java
import com.azure.core.http.ProxyOptions;
import com.azure.core.http.ProxyOptions.Type;
import java.net.InetSocketAddress;

ClientSecretCredential credential = new ClientSecretCredentialBuilder()
    .tenantId(tenantId)
    .clientId(clientId)
    .clientSecret(clientSecret)
    .proxyOptions(new ProxyOptions(Type.HTTP, new InetSocketAddress("10.21.32.43", 5465)))
    .build();
```

## ClientCertificateCredential

Authenticate a service principal using a certificate.

### Using PEM Certificate File

```java
import com.azure.identity.ClientCertificateCredential;
import com.azure.identity.ClientCertificateCredentialBuilder;

ClientCertificateCredential credential = new ClientCertificateCredentialBuilder()
    .tenantId(tenantId)
    .clientId(clientId)
    .pemCertificate("<PATH-TO-PEM-CERTIFICATE>")
    .build();

SecretClient client = new SecretClientBuilder()
    .vaultUrl("https://{YOUR_VAULT_NAME}.vault.azure.net")
    .credential(credential)
    .buildClient();
```

### Using PFX Certificate with Password

```java
ClientCertificateCredential credential = new ClientCertificateCredentialBuilder()
    .tenantId(tenantId)
    .clientId(clientId)
    .pfxCertificate("<PATH-TO-PFX-CERTIFICATE>", "P@s$w0rd")
    .build();
```

### Using Certificate from InputStream

```java
import java.io.ByteArrayInputStream;
import java.nio.file.Files;
import java.nio.file.Paths;

byte[] certificateBytes = Files.readAllBytes(Paths.get("certificate.pem"));
ByteArrayInputStream certificateStream = new ByteArrayInputStream(certificateBytes);

ClientCertificateCredential credential = new ClientCertificateCredentialBuilder()
    .tenantId(tenantId)
    .clientId(clientId)
    .pemCertificate(certificateStream)
    .build();
```

### With Proxy Configuration

```java
ClientCertificateCredential credential = new ClientCertificateCredentialBuilder()
    .tenantId(tenantId)
    .clientId(clientId)
    .pfxCertificate("<PATH-TO-PFX-CERTIFICATE>", "P@s$w0rd")
    .proxyOptions(new ProxyOptions(Type.HTTP, new InetSocketAddress("10.21.32.43", 5465)))
    .build();
```

## ManagedIdentityCredential

Authenticate using Azure managed identity (system-assigned or user-assigned).

### System-Assigned Managed Identity

```java
import com.azure.identity.ManagedIdentityCredential;
import com.azure.identity.ManagedIdentityCredentialBuilder;

// No clientId needed for system-assigned
ManagedIdentityCredential credential = new ManagedIdentityCredentialBuilder().build();

SecretClient client = new SecretClientBuilder()
    .vaultUrl("https://{YOUR_VAULT_NAME}.vault.azure.net")
    .credential(credential)
    .buildClient();
```

### User-Assigned Managed Identity (by Client ID)

```java
ManagedIdentityCredential credential = new ManagedIdentityCredentialBuilder()
    .clientId("<USER-ASSIGNED-MANAGED-IDENTITY-CLIENT-ID>")
    .build();

SecretClient client = new SecretClientBuilder()
    .vaultUrl("https://{YOUR_VAULT_NAME}.vault.azure.net")
    .credential(credential)
    .buildClient();
```

### User-Assigned Managed Identity (by Resource ID)

```java
ManagedIdentityCredential credential = new ManagedIdentityCredentialBuilder()
    .resourceId("/subscriptions/<subscriptionID>/resourcegroups/<resource-group>/providers/Microsoft.ManagedIdentity/userAssignedIdentities/<MI-name>")
    .build();
```

### User-Assigned Managed Identity (by Object ID)

```java
ManagedIdentityCredential credential = new ManagedIdentityCredentialBuilder()
    .objectId("<USER-ASSIGNED-MANAGED-IDENTITY-OBJECT-ID>")
    .build();
```

## EnvironmentCredential

Authenticates using environment variables. Supports service principal with secret, certificate, or username/password.

### Required Environment Variables

For service principal with secret:
```bash
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_CLIENT_SECRET=<client-secret>
```

For service principal with certificate:
```bash
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_CLIENT_CERTIFICATE_PATH=<path-to-certificate>
AZURE_CLIENT_CERTIFICATE_PASSWORD=<certificate-password>  # Optional
```

For username/password:
```bash
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_USERNAME=<username>
AZURE_PASSWORD=<password>
```

### Usage

```java
import com.azure.identity.EnvironmentCredential;
import com.azure.identity.EnvironmentCredentialBuilder;

EnvironmentCredential credential = new EnvironmentCredentialBuilder().build();

SecretClient client = new SecretClientBuilder()
    .vaultUrl("https://{YOUR_VAULT_NAME}.vault.azure.net")
    .credential(credential)
    .buildClient();
```

## InteractiveBrowserCredential

Authenticate interactively via browser. Suitable for development.

```java
import com.azure.identity.InteractiveBrowserCredential;
import com.azure.identity.InteractiveBrowserCredentialBuilder;

InteractiveBrowserCredential credential = new InteractiveBrowserCredentialBuilder()
    .clientId("<client-id>")
    .redirectUrl("http://localhost:8765")
    .build();

SecretClient client = new SecretClientBuilder()
    .vaultUrl("https://{YOUR_VAULT_NAME}.vault.azure.net")
    .credential(credential)
    .buildClient();
```

### With Tenant ID

```java
InteractiveBrowserCredential credential = new InteractiveBrowserCredentialBuilder()
    .clientId("<client-id>")
    .tenantId("<tenant-id>")
    .redirectUrl("http://localhost:8765")
    .build();
```

## DeviceCodeCredential

Authenticate using device code flow. User enters code at microsoft.com/devicelogin.

```java
import com.azure.identity.DeviceCodeCredential;
import com.azure.identity.DeviceCodeCredentialBuilder;

DeviceCodeCredential credential = new DeviceCodeCredentialBuilder()
    .clientId("<client-id>")
    .challengeConsumer(challenge -> {
        // Display the device code message to the user
        System.out.println(challenge.getMessage());
    })
    .build();

SecretClient client = new SecretClientBuilder()
    .vaultUrl("https://{YOUR_VAULT_NAME}.vault.azure.net")
    .credential(credential)
    .buildClient();
```

## AzureCliCredential

Authenticate using Azure CLI. User must be logged in via `az login`.

```java
import com.azure.identity.AzureCliCredential;
import com.azure.identity.AzureCliCredentialBuilder;

AzureCliCredential credential = new AzureCliCredentialBuilder().build();

SecretClient client = new SecretClientBuilder()
    .vaultUrl("https://{YOUR_VAULT_NAME}.vault.azure.net")
    .credential(credential)
    .buildClient();
```

### With Specific Tenant

```java
AzureCliCredential credential = new AzureCliCredentialBuilder()
    .tenantId("<tenant-id>")
    .build();
```

## Using Credentials with Azure SDK Clients

### Key Vault Secrets

```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.security.keyvault.secrets.SecretClient;
import com.azure.security.keyvault.secrets.SecretClientBuilder;

SecretClient client = new SecretClientBuilder()
    .vaultUrl("https://{vault-name}.vault.azure.net")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();

// Use the client
String secretValue = client.getSecret("my-secret").getValue();
```

### Blob Storage

```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.storage.blob.BlobServiceClient;
import com.azure.storage.blob.BlobServiceClientBuilder;

BlobServiceClient client = new BlobServiceClientBuilder()
    .endpoint("https://{storage-account}.blob.core.windows.net")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### Cosmos DB

```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.cosmos.CosmosClientBuilder;
import com.azure.cosmos.CosmosClient;

CosmosClient client = new CosmosClientBuilder()
    .endpoint("https://{cosmos-account}.documents.azure.com:443/")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### Event Hubs

```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.messaging.eventhubs.EventHubClientBuilder;
import com.azure.messaging.eventhubs.EventHubProducerClient;

EventHubProducerClient producer = new EventHubClientBuilder()
    .fullyQualifiedNamespace("{namespace}.servicebus.windows.net")
    .eventHubName("{event-hub-name}")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildProducerClient();
```

### Service Bus

```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.messaging.servicebus.ServiceBusClientBuilder;
import com.azure.messaging.servicebus.ServiceBusSenderClient;

ServiceBusSenderClient sender = new ServiceBusClientBuilder()
    .fullyQualifiedNamespace("{namespace}.servicebus.windows.net")
    .credential(new DefaultAzureCredentialBuilder().build())
    .sender()
    .queueName("{queue-name}")
    .buildClient();
```

## Error Handling

```java
import com.azure.core.exception.ClientAuthenticationException;
import com.azure.identity.CredentialUnavailableException;

try {
    DefaultAzureCredential credential = new DefaultAzureCredentialBuilder().build();
    // Use credential...
} catch (CredentialUnavailableException e) {
    System.err.println("No credential available: " + e.getMessage());
} catch (ClientAuthenticationException e) {
    System.err.println("Authentication failed: " + e.getMessage());
}
```

## Logging and Debugging

Enable logging to troubleshoot authentication issues:

```java
import com.azure.core.util.logging.ClientLogger;

// Set environment variable
// AZURE_LOG_LEVEL=verbose

// Or programmatically
System.setProperty("AZURE_LOG_LEVEL", "verbose");
```
