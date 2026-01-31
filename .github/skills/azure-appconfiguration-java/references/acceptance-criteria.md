# Azure App Configuration SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-data-appconfiguration`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/appconfiguration/azure-data-appconfiguration
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Azure SDK Client Imports
```java
import com.azure.data.appconfiguration.ConfigurationClient;
import com.azure.data.appconfiguration.ConfigurationClientBuilder;
import com.azure.data.appconfiguration.ConfigurationAsyncClient;
```

#### ❌ INCORRECT: Non-existent or Wrong Package
```java
import com.azure.appconfiguration.ConfigurationClient;  // Wrong package path
import com.azure.data.appconfiguration.AppConfigClient;  // Wrong class name
```

### 1.2 Model Imports
#### ✅ CORRECT: Model Classes from Models Package
```java
import com.azure.data.appconfiguration.models.ConfigurationSetting;
import com.azure.data.appconfiguration.models.FeatureFlagConfigurationSetting;
import com.azure.data.appconfiguration.models.SecretReferenceConfigurationSetting;
import com.azure.data.appconfiguration.models.SettingSelector;
import com.azure.data.appconfiguration.models.ConfigurationSnapshot;
```

#### ❌ INCORRECT: Wrong Model Package
```java
import com.azure.data.appconfiguration.ConfigurationSetting;  // Missing models subpackage
```

---

## 2. Client Creation Patterns

### 2.1 With Connection String
#### ✅ CORRECT: Using ConfigurationClientBuilder
```java
ConfigurationClient configClient = new ConfigurationClientBuilder()
    .connectionString(System.getenv("AZURE_APPCONFIG_CONNECTION_STRING"))
    .buildClient();
```

#### ❌ INCORRECT: Direct Instantiation
```java
ConfigurationClient client = new ConfigurationClient(connectionString);
```

### 2.2 Async Client
#### ✅ CORRECT: Using buildAsyncClient
```java
ConfigurationAsyncClient asyncClient = new ConfigurationClientBuilder()
    .connectionString(connectionString)
    .buildAsyncClient();
```

### 2.3 With Entra ID (Recommended)
#### ✅ CORRECT: Using DefaultAzureCredentialBuilder
```java
import com.azure.identity.DefaultAzureCredentialBuilder;

ConfigurationClient configClient = new ConfigurationClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(System.getenv("AZURE_APPCONFIG_ENDPOINT"))
    .buildClient();
```

#### ❌ INCORRECT: Direct DefaultAzureCredential
```java
ConfigurationClient client = new ConfigurationClientBuilder()
    .credential(new DefaultAzureCredential())  // Must use builder
    .buildClient();
```

---

## 3. Configuration Setting Operations

### 3.1 Create Setting (Add)
#### ✅ CORRECT: addConfigurationSetting
```java
ConfigurationSetting setting = configClient.addConfigurationSetting(
    "app/database/connection", 
    "Production", 
    "Server=prod.db.com;Database=myapp"
);
```

### 3.2 Create or Update Setting (Set)
#### ✅ CORRECT: setConfigurationSetting
```java
ConfigurationSetting setting = configClient.setConfigurationSetting(
    "app/cache/enabled", 
    "Production", 
    "true"
);
```

### 3.3 Get Setting
#### ✅ CORRECT: getConfigurationSetting
```java
ConfigurationSetting setting = configClient.getConfigurationSetting(
    "app/database/connection", 
    "Production"
);
System.out.println("Value: " + setting.getValue());
System.out.println("Content-Type: " + setting.getContentType());
System.out.println("Last Modified: " + setting.getLastModified());
```

### 3.4 Conditional Get
#### ✅ CORRECT: getConfigurationSettingWithResponse with ifChanged
```java
import com.azure.core.http.rest.Response;
import com.azure.core.util.Context;

Response<ConfigurationSetting> response = configClient.getConfigurationSettingWithResponse(
    setting,
    null,
    true,  // ifChanged
    Context.NONE
);

if (response.getStatusCode() == 304) {
    System.out.println("Setting not modified");
} else {
    ConfigurationSetting updated = response.getValue();
}
```

### 3.5 Conditional Update
#### ✅ CORRECT: setConfigurationSettingWithResponse with ifUnchanged
```java
Response<ConfigurationSetting> response = configClient.setConfigurationSettingWithResponse(
    setting,
    true,  // ifUnchanged
    Context.NONE
);
```

### 3.6 Delete Setting
#### ✅ CORRECT: deleteConfigurationSetting
```java
ConfigurationSetting deleted = configClient.deleteConfigurationSetting(
    "app/cache/enabled", 
    "Production"
);
```

---

## 4. Listing and Filtering

### 4.1 List by Key Pattern
#### ✅ CORRECT: SettingSelector with setKeyFilter
```java
import com.azure.data.appconfiguration.models.SettingSelector;
import com.azure.core.http.rest.PagedIterable;

SettingSelector selector = new SettingSelector()
    .setKeyFilter("app/*");

PagedIterable<ConfigurationSetting> settings = configClient.listConfigurationSettings(selector);
for (ConfigurationSetting s : settings) {
    System.out.println(s.getKey() + " = " + s.getValue());
}
```

### 4.2 List by Label
#### ✅ CORRECT: SettingSelector with setLabelFilter
```java
SettingSelector selector = new SettingSelector()
    .setKeyFilter("*")
    .setLabelFilter("Production");

PagedIterable<ConfigurationSetting> settings = configClient.listConfigurationSettings(selector);
```

### 4.3 List Revisions
#### ✅ CORRECT: listRevisions
```java
SettingSelector selector = new SettingSelector()
    .setKeyFilter("app/database/connection");

PagedIterable<ConfigurationSetting> revisions = configClient.listRevisions(selector);
for (ConfigurationSetting revision : revisions) {
    System.out.println("Value: " + revision.getValue() + ", Modified: " + revision.getLastModified());
}
```

---

## 5. Feature Flags

### 5.1 Create Feature Flag
#### ✅ CORRECT: FeatureFlagConfigurationSetting
```java
import com.azure.data.appconfiguration.models.FeatureFlagConfigurationSetting;
import com.azure.data.appconfiguration.models.FeatureFlagFilter;
import java.util.Arrays;

FeatureFlagFilter percentageFilter = new FeatureFlagFilter("Microsoft.Percentage")
    .addParameter("Value", 50);

FeatureFlagConfigurationSetting featureFlag = new FeatureFlagConfigurationSetting("beta-feature", true)
    .setDescription("Beta feature rollout")
    .setClientFilters(Arrays.asList(percentageFilter));

FeatureFlagConfigurationSetting created = (FeatureFlagConfigurationSetting)
    configClient.addConfigurationSetting(featureFlag);
```

### 5.2 Get Feature Flag
#### ✅ CORRECT: Cast to FeatureFlagConfigurationSetting
```java
FeatureFlagConfigurationSetting flag = (FeatureFlagConfigurationSetting)
    configClient.getConfigurationSetting(featureFlag);

System.out.println("Feature: " + flag.getFeatureId());
System.out.println("Enabled: " + flag.isEnabled());
System.out.println("Filters: " + flag.getClientFilters());
```

### 5.3 Update Feature Flag
#### ✅ CORRECT: Modify and Set
```java
featureFlag.setEnabled(false);
FeatureFlagConfigurationSetting updated = (FeatureFlagConfigurationSetting)
    configClient.setConfigurationSetting(featureFlag);
```

---

## 6. Secret References

### 6.1 Create Secret Reference
#### ✅ CORRECT: SecretReferenceConfigurationSetting
```java
import com.azure.data.appconfiguration.models.SecretReferenceConfigurationSetting;

SecretReferenceConfigurationSetting secretRef = new SecretReferenceConfigurationSetting(
    "app/secrets/api-key",
    "https://myvault.vault.azure.net/secrets/api-key"
);

SecretReferenceConfigurationSetting created = (SecretReferenceConfigurationSetting)
    configClient.addConfigurationSetting(secretRef);
```

### 6.2 Get Secret Reference
#### ✅ CORRECT: Access Secret URI
```java
SecretReferenceConfigurationSetting ref = (SecretReferenceConfigurationSetting)
    configClient.getConfigurationSetting(secretRef);

System.out.println("Secret URI: " + ref.getSecretId());
```

---

## 7. Read-Only Settings

### 7.1 Set Read-Only
#### ✅ CORRECT: setReadOnly with true
```java
ConfigurationSetting readOnly = configClient.setReadOnly(
    "app/critical/setting", 
    "Production", 
    true
);
```

### 7.2 Clear Read-Only
#### ✅ CORRECT: setReadOnly with false
```java
ConfigurationSetting writable = configClient.setReadOnly(
    "app/critical/setting", 
    "Production", 
    false
);
```

---

## 8. Snapshots

### 8.1 Create Snapshot
#### ✅ CORRECT: beginCreateSnapshot with SyncPoller
```java
import com.azure.data.appconfiguration.models.ConfigurationSnapshot;
import com.azure.data.appconfiguration.models.ConfigurationSettingsFilter;
import com.azure.core.util.polling.SyncPoller;
import com.azure.core.util.polling.PollOperationDetails;

List<ConfigurationSettingsFilter> filters = new ArrayList<>();
filters.add(new ConfigurationSettingsFilter("app/*"));

SyncPoller<PollOperationDetails, ConfigurationSnapshot> poller = configClient.beginCreateSnapshot(
    "release-v1.0",
    new ConfigurationSnapshot(filters),
    Context.NONE
);
poller.setPollInterval(Duration.ofSeconds(10));
poller.waitForCompletion();

ConfigurationSnapshot snapshot = poller.getFinalResult();
```

### 8.2 List Settings in Snapshot
#### ✅ CORRECT: listConfigurationSettingsForSnapshot
```java
PagedIterable<ConfigurationSetting> settings = 
    configClient.listConfigurationSettingsForSnapshot("release-v1.0");

for (ConfigurationSetting setting : settings) {
    System.out.println(setting.getKey() + " = " + setting.getValue());
}
```

### 8.3 Archive and Recover Snapshot
#### ✅ CORRECT: archiveSnapshot and recoverSnapshot
```java
ConfigurationSnapshot archived = configClient.archiveSnapshot("release-v1.0");
ConfigurationSnapshot recovered = configClient.recoverSnapshot("release-v1.0");
```

---

## 9. Async Operations

### 9.1 Async Listing
#### ✅ CORRECT: Reactive Subscription
```java
ConfigurationAsyncClient asyncClient = new ConfigurationClientBuilder()
    .connectionString(connectionString)
    .buildAsyncClient();

asyncClient.listConfigurationSettings(new SettingSelector().setLabelFilter("Production"))
    .subscribe(
        setting -> System.out.println(setting.getKey() + " = " + setting.getValue()),
        error -> System.err.println("Error: " + error.getMessage()),
        () -> System.out.println("Completed")
    );
```

---

## 10. Error Handling

### 10.1 HttpResponseException
#### ✅ CORRECT: Handle 404 and Other Errors
```java
import com.azure.core.exception.HttpResponseException;

try {
    configClient.getConfigurationSetting("nonexistent", null);
} catch (HttpResponseException e) {
    if (e.getResponse().getStatusCode() == 404) {
        System.err.println("Setting not found");
    } else {
        System.err.println("Error: " + e.getMessage());
    }
}
```

#### ❌ INCORRECT: Generic Exception Only
```java
try {
    configClient.getConfigurationSetting("key", null);
} catch (Exception e) {
    // Missing specific HttpResponseException handling
}
```

---

## 11. Environment Configuration

### 11.1 Environment Variables
#### ✅ CORRECT: Reading from Environment
```java
String connectionString = System.getenv("AZURE_APPCONFIG_CONNECTION_STRING");
String endpoint = System.getenv("AZURE_APPCONFIG_ENDPOINT");
```

#### ❌ INCORRECT: Hardcoded Credentials
```java
String connectionString = "Endpoint=https://store.azconfig.io;Id=xxx;Secret=yyy";
```

---

## 12. Best Practices

### 12.1 Labels for Environments
- Use labels to separate configurations by environment (Dev, Staging, Production)

### 12.2 Snapshots for Releases
- Create immutable snapshots for release configurations

### 12.3 Feature Flags
- Use for gradual rollouts and A/B testing
- Configure filters for percentage rollouts

### 12.4 Secret References
- Store sensitive values in Key Vault, not App Configuration
- Use SecretReferenceConfigurationSetting to point to secrets

### 12.5 Optimistic Concurrency
- Use ETags with conditional requests to prevent lost updates

### 12.6 Read-Only Protection
- Lock critical production settings to prevent accidental changes

### 12.7 Authentication
- Prefer Entra ID over connection strings in production