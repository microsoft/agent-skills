# Azure App Configuration SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-data-appconfiguration`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/appconfiguration-v2/azure-data-appconfiguration
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Client Builder and Clients
```java
import com.azure.data.appconfiguration.ConfigurationClient;
import com.azure.data.appconfiguration.ConfigurationClientBuilder;
import com.azure.data.appconfiguration.ConfigurationAsyncClient;
```

#### ✅ CORRECT: Authentication
```java
import com.azure.identity.DefaultAzureCredentialBuilder;
```

### 1.2 Model Imports

#### ✅ CORRECT: Configuration Models
```java
import com.azure.data.appconfiguration.models.ConfigurationSetting;
import com.azure.data.appconfiguration.models.SettingSelector;
import com.azure.data.appconfiguration.models.FeatureFlagConfigurationSetting;
import com.azure.data.appconfiguration.models.FeatureFlagFilter;
import com.azure.data.appconfiguration.models.SecretReferenceConfigurationSetting;
import com.azure.data.appconfiguration.models.ConfigurationSnapshot;
import com.azure.data.appconfiguration.models.ConfigurationSettingsFilter;
import com.azure.data.appconfiguration.models.SnapshotSelector;
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong import paths
```java
// WRONG - Using old package names
import com.azure.appconfiguration.ConfigurationClient;

// WRONG - Models not in models package
import com.azure.data.appconfiguration.ConfigurationSetting;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Builder with Connection String
```java
String connectionString = System.getenv("AZURE_APPCONFIG_CONNECTION_STRING");

ConfigurationClient client = new ConfigurationClientBuilder()
    .connectionString(connectionString)
    .buildClient();
```

### 2.2 ✅ CORRECT: Builder with Entra ID (DefaultAzureCredential)
```java
String endpoint = System.getenv("AZURE_APPCONFIG_ENDPOINT");

ConfigurationClient client = new ConfigurationClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint)
    .buildClient();
```

### 2.3 ✅ CORRECT: Async Client
```java
ConfigurationAsyncClient asyncClient = new ConfigurationClientBuilder()
    .connectionString(connectionString)
    .buildAsyncClient();
```

### 2.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded connection string
```java
.connectionString("Endpoint=https://example.azconfig.io;Id=xxx;Secret=xxx")
```

#### ❌ INCORRECT: Hardcoded endpoint URL
```java
.endpoint("https://example.azconfig.io")
```

---

## 3. Configuration Setting Operations

### 3.1 ✅ CORRECT: Add Configuration Setting
```java
ConfigurationSetting setting = client.addConfigurationSetting(
    "app/database/connection", 
    "Production", 
    "Server=prod.db.com;Database=myapp"
);
```

### 3.2 ✅ CORRECT: Set (Create or Update) Configuration Setting
```java
ConfigurationSetting setting = client.setConfigurationSetting(
    "app/cache/enabled", 
    "Production", 
    "true"
);
```

### 3.3 ✅ CORRECT: Get Configuration Setting
```java
ConfigurationSetting setting = client.getConfigurationSetting(
    "app/database/connection", 
    "Production"
);
System.out.println("Value: " + setting.getValue());
System.out.println("Last Modified: " + setting.getLastModified());
```

### 3.4 ✅ CORRECT: Delete Configuration Setting
```java
ConfigurationSetting deleted = client.deleteConfigurationSetting(
    "app/cache/enabled", 
    "Production"
);
```

---

## 4. List and Filter Settings

### 4.1 ✅ CORRECT: List by Key Pattern
```java
import com.azure.core.http.rest.PagedIterable;

SettingSelector selector = new SettingSelector()
    .setKeyFilter("app/*");

PagedIterable<ConfigurationSetting> settings = client.listConfigurationSettings(selector);
for (ConfigurationSetting s : settings) {
    System.out.println(s.getKey() + " = " + s.getValue());
}
```

### 4.2 ✅ CORRECT: List by Label
```java
SettingSelector selector = new SettingSelector()
    .setKeyFilter("*")
    .setLabelFilter("Production");

PagedIterable<ConfigurationSetting> settings = client.listConfigurationSettings(selector);
```

### 4.3 ✅ CORRECT: List Revisions
```java
SettingSelector selector = new SettingSelector()
    .setKeyFilter("app/database/connection");

PagedIterable<ConfigurationSetting> revisions = client.listRevisions(selector);
for (ConfigurationSetting revision : revisions) {
    System.out.println("Value: " + revision.getValue() + ", Modified: " + revision.getLastModified());
}
```

---

## 5. Feature Flags

### 5.1 ✅ CORRECT: Create Feature Flag
```java
FeatureFlagFilter percentageFilter = new FeatureFlagFilter("Microsoft.Percentage")
    .addParameter("Value", 50);

FeatureFlagConfigurationSetting featureFlag = new FeatureFlagConfigurationSetting("beta-feature", true)
    .setDescription("Beta feature rollout")
    .setClientFilters(Arrays.asList(percentageFilter));

FeatureFlagConfigurationSetting created = (FeatureFlagConfigurationSetting)
    client.addConfigurationSetting(featureFlag);
```

### 5.2 ✅ CORRECT: Get Feature Flag
```java
FeatureFlagConfigurationSetting flag = (FeatureFlagConfigurationSetting)
    client.getConfigurationSetting(featureFlag);

System.out.println("Feature: " + flag.getFeatureId());
System.out.println("Enabled: " + flag.isEnabled());
```

---

## 6. Secret References

### 6.1 ✅ CORRECT: Create Secret Reference
```java
SecretReferenceConfigurationSetting secretRef = new SecretReferenceConfigurationSetting(
    "app/secrets/api-key",
    "https://myvault.vault.azure.net/secrets/api-key"
);

SecretReferenceConfigurationSetting created = (SecretReferenceConfigurationSetting)
    client.addConfigurationSetting(secretRef);
```

---

## 7. Snapshots

### 7.1 ✅ CORRECT: Create Snapshot
```java
import com.azure.core.util.polling.SyncPoller;
import com.azure.core.util.polling.PollOperationDetails;
import java.time.Duration;

List<ConfigurationSettingsFilter> filters = new ArrayList<>();
filters.add(new ConfigurationSettingsFilter("app/*"));

SyncPoller<PollOperationDetails, ConfigurationSnapshot> poller = client.beginCreateSnapshot(
    "release-v1.0",
    new ConfigurationSnapshot(filters),
    Context.NONE
);
poller.setPollInterval(Duration.ofSeconds(10));
poller.waitForCompletion();

ConfigurationSnapshot snapshot = poller.getFinalResult();
System.out.println("Snapshot: " + snapshot.getName());
```

### 7.2 ✅ CORRECT: List Settings in Snapshot
```java
PagedIterable<ConfigurationSetting> settings = 
    client.listConfigurationSettingsForSnapshot("release-v1.0");

for (ConfigurationSetting setting : settings) {
    System.out.println(setting.getKey() + " = " + setting.getValue());
}
```

---

## 8. Error Handling

### 8.1 ✅ CORRECT: HTTP Exception Handling
```java
import com.azure.core.exception.HttpResponseException;

try {
    client.getConfigurationSetting("nonexistent", null);
} catch (HttpResponseException e) {
    if (e.getResponse().getStatusCode() == 404) {
        System.err.println("Setting not found");
    } else {
        System.err.println("Error: " + e.getMessage());
    }
}
```

---

## 9. Best Practices Checklist

- [ ] Use Entra ID authentication (DefaultAzureCredential) over connection strings
- [ ] Use environment variables for connection configuration
- [ ] Use labels to separate configurations by environment
- [ ] Use snapshots for release management
- [ ] Store sensitive values in Key Vault via SecretReferenceConfigurationSetting
- [ ] Use feature flags for gradual rollouts
- [ ] Use ETags for optimistic concurrency
- [ ] Lock critical production settings with setReadOnly
- [ ] Use async client for high-throughput scenarios
