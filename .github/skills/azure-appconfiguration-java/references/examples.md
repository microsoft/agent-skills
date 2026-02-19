# Azure App Configuration Java SDK - Examples

Comprehensive code examples for the Azure App Configuration SDK for Java.

## Table of Contents

- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Configuration Settings CRUD](#configuration-settings-crud)
- [List and Filter Settings](#list-and-filter-settings)
- [Feature Flags](#feature-flags)
- [Secret References](#secret-references)
- [Read-Only Settings](#read-only-settings)
- [Snapshots](#snapshots)
- [Labels](#labels)
- [Async Operations](#async-operations)
- [Error Handling](#error-handling)
- [Complete Application Example](#complete-application-example)

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-data-appconfiguration</artifactId>
    <version>1.8.0</version>
</dependency>

<!-- For DefaultAzureCredential -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
    <version>1.14.2</version>
</dependency>
```

Or use Azure SDK BOM:

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.azure</groupId>
            <artifactId>azure-sdk-bom</artifactId>
            <version>1.2.28</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <dependency>
        <groupId>com.azure</groupId>
        <artifactId>azure-data-appconfiguration</artifactId>
    </dependency>
</dependencies>
```

## Client Creation

### With Connection String

```java
import com.azure.data.appconfiguration.ConfigurationClient;
import com.azure.data.appconfiguration.ConfigurationClientBuilder;

String connectionString = System.getenv("AZURE_APPCONFIG_CONNECTION_STRING");

ConfigurationClient client = new ConfigurationClientBuilder()
    .connectionString(connectionString)
    .buildClient();
```

### With Entra ID (Recommended)

```java
import com.azure.identity.DefaultAzureCredentialBuilder;

String endpoint = System.getenv("AZURE_APPCONFIG_ENDPOINT");

ConfigurationClient client = new ConfigurationClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint)
    .buildClient();
```

### Async Client

```java
import com.azure.data.appconfiguration.ConfigurationAsyncClient;

ConfigurationAsyncClient asyncClient = new ConfigurationClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint)
    .buildAsyncClient();
```

## Configuration Settings CRUD

### Create Setting (Add)

Creates only if setting doesn't exist:

```java
import com.azure.data.appconfiguration.models.ConfigurationSetting;

// Add with key, label, and value
ConfigurationSetting setting = client.addConfigurationSetting(
    "app/database/connection",    // key
    "Production",                  // label (can be null)
    "Server=prod.db.com;Database=myapp"  // value
);

System.out.println("Setting created:");
System.out.println("  Key: " + setting.getKey());
System.out.println("  Label: " + setting.getLabel());
System.out.println("  Value: " + setting.getValue());
System.out.println("  ETag: " + setting.getETag());
```

### Create or Update Setting (Set)

Creates or overwrites:

```java
ConfigurationSetting setting = client.setConfigurationSetting(
    "app/cache/enabled",
    "Production",
    "true"
);

System.out.println("Setting set: " + setting.getKey() + " = " + setting.getValue());
```

### Create with ConfigurationSetting Object

```java
ConfigurationSetting newSetting = new ConfigurationSetting()
    .setKey("app/feature/timeout")
    .setLabel("Production")
    .setValue("30000")
    .setContentType("application/json");

ConfigurationSetting created = client.addConfigurationSetting(newSetting);
```

### Get Setting

```java
ConfigurationSetting setting = client.getConfigurationSetting(
    "app/database/connection",
    "Production"
);

System.out.println("=== Setting Details ===");
System.out.println("Key: " + setting.getKey());
System.out.println("Label: " + setting.getLabel());
System.out.println("Value: " + setting.getValue());
System.out.println("Content-Type: " + setting.getContentType());
System.out.println("Last Modified: " + setting.getLastModified());
System.out.println("ETag: " + setting.getETag());
System.out.println("Read-Only: " + setting.isReadOnly());
```

### Conditional Get (If Changed)

Only fetch if modified since last retrieval:

```java
import com.azure.core.http.rest.Response;
import com.azure.core.util.Context;

// First, get the setting with its ETag
ConfigurationSetting setting = client.getConfigurationSetting("app/cache/enabled", "Production");

// Later, check if it changed
Response<ConfigurationSetting> response = client.getConfigurationSettingWithResponse(
    setting,      // Setting with ETag
    null,         // Accept datetime
    true,         // ifChanged - only fetch if modified
    Context.NONE
);

if (response.getStatusCode() == 304) {
    System.out.println("Setting not modified since last fetch");
} else {
    ConfigurationSetting updated = response.getValue();
    System.out.println("Setting was modified: " + updated.getValue());
}
```

### Update Setting

```java
// Simple update
ConfigurationSetting updated = client.setConfigurationSetting(
    "app/cache/enabled",
    "Production",
    "false"
);

System.out.println("Updated value: " + updated.getValue());
```

### Conditional Update (If Unchanged)

Only update if no concurrent modifications:

```java
// Get current setting with ETag
ConfigurationSetting current = client.getConfigurationSetting("app/timeout", "Production");

// Modify the value
current.setValue("60000");

// Update only if ETag matches (optimistic concurrency)
Response<ConfigurationSetting> response = client.setConfigurationSettingWithResponse(
    current,     // Setting with current ETag
    true,        // ifUnchanged - only update if ETag matches
    Context.NONE
);

if (response.getStatusCode() == 200) {
    System.out.println("Update successful");
} else {
    System.out.println("Conflict - setting was modified by another process");
}
```

### Delete Setting

```java
ConfigurationSetting deleted = client.deleteConfigurationSetting(
    "app/cache/enabled",
    "Production"
);

if (deleted != null) {
    System.out.println("Deleted setting: " + deleted.getKey());
}
```

### Conditional Delete

```java
Response<ConfigurationSetting> response = client.deleteConfigurationSettingWithResponse(
    setting,     // Setting with ETag
    true,        // ifUnchanged
    Context.NONE
);

if (response.getStatusCode() == 200) {
    System.out.println("Setting deleted");
}
```

## List and Filter Settings

### List All Settings

```java
import com.azure.data.appconfiguration.models.SettingSelector;
import com.azure.core.http.rest.PagedIterable;

PagedIterable<ConfigurationSetting> settings = client.listConfigurationSettings(
    new SettingSelector()
);

System.out.println("=== All Settings ===");
for (ConfigurationSetting s : settings) {
    System.out.printf("%s [%s] = %s%n", s.getKey(), s.getLabel(), s.getValue());
}
```

### List by Key Pattern

```java
SettingSelector selector = new SettingSelector()
    .setKeyFilter("app/*");  // Wildcard pattern

PagedIterable<ConfigurationSetting> settings = client.listConfigurationSettings(selector);

for (ConfigurationSetting s : settings) {
    System.out.println(s.getKey() + " = " + s.getValue());
}
```

### List by Label

```java
SettingSelector selector = new SettingSelector()
    .setKeyFilter("*")
    .setLabelFilter("Production");

PagedIterable<ConfigurationSetting> settings = client.listConfigurationSettings(selector);
```

### List by Multiple Keys

```java
SettingSelector selector = new SettingSelector()
    .setKeyFilter("app/database/*,app/cache/*");  // Comma-separated patterns

PagedIterable<ConfigurationSetting> settings = client.listConfigurationSettings(selector);
```

### List Null Labels Only

```java
SettingSelector selector = new SettingSelector()
    .setKeyFilter("*")
    .setLabelFilter("\0");  // Null label filter

PagedIterable<ConfigurationSetting> settings = client.listConfigurationSettings(selector);
```

### Select Specific Fields

```java
import com.azure.data.appconfiguration.models.SettingFields;
import java.util.EnumSet;

SettingSelector selector = new SettingSelector()
    .setKeyFilter("*")
    .setFields(EnumSet.of(SettingFields.KEY, SettingFields.VALUE, SettingFields.LAST_MODIFIED));

PagedIterable<ConfigurationSetting> settings = client.listConfigurationSettings(selector);
```

### List Revisions

View history of changes:

```java
SettingSelector selector = new SettingSelector()
    .setKeyFilter("app/database/connection");

PagedIterable<ConfigurationSetting> revisions = client.listRevisions(selector);

System.out.println("=== Setting Revisions ===");
for (ConfigurationSetting revision : revisions) {
    System.out.printf("Value: %s, Modified: %s%n",
        revision.getValue(),
        revision.getLastModified());
}
```

## Feature Flags

### Create Feature Flag

```java
import com.azure.data.appconfiguration.models.FeatureFlagConfigurationSetting;
import com.azure.data.appconfiguration.models.FeatureFlagFilter;
import java.util.Arrays;

// Simple feature flag
FeatureFlagConfigurationSetting simpleFlag = new FeatureFlagConfigurationSetting("dark-mode", true)
    .setDescription("Enable dark mode theme");

client.addConfigurationSetting(simpleFlag);

// Feature flag with percentage filter
FeatureFlagFilter percentageFilter = new FeatureFlagFilter("Microsoft.Percentage")
    .addParameter("Value", 50);  // 50% rollout

FeatureFlagConfigurationSetting betaFlag = new FeatureFlagConfigurationSetting("beta-feature", true)
    .setDescription("Beta feature with gradual rollout")
    .setClientFilters(Arrays.asList(percentageFilter));

FeatureFlagConfigurationSetting created = (FeatureFlagConfigurationSetting)
    client.addConfigurationSetting(betaFlag);

System.out.println("Feature flag created: " + created.getFeatureId());
```

### Create Feature Flag with Targeting Filter

```java
import java.util.HashMap;
import java.util.Map;

Map<String, Object> targetingParams = new HashMap<>();
targetingParams.put("Audience", Map.of(
    "Users", Arrays.asList("user1@example.com", "user2@example.com"),
    "Groups", Arrays.asList(
        Map.of("Name", "beta-testers", "RolloutPercentage", 100),
        Map.of("Name", "employees", "RolloutPercentage", 50)
    ),
    "DefaultRolloutPercentage", 10
));

FeatureFlagFilter targetingFilter = new FeatureFlagFilter("Microsoft.Targeting")
    .setParameters(targetingParams);

FeatureFlagConfigurationSetting targetedFlag = new FeatureFlagConfigurationSetting("new-dashboard", true)
    .setDescription("New dashboard with targeted rollout")
    .setClientFilters(Arrays.asList(targetingFilter));

client.addConfigurationSetting(targetedFlag);
```

### Get Feature Flag

```java
FeatureFlagConfigurationSetting flag = (FeatureFlagConfigurationSetting)
    client.getConfigurationSetting(
        ".appconfig.featureflag/beta-feature",  // Key format for feature flags
        null
    );

System.out.println("=== Feature Flag ===");
System.out.println("Feature ID: " + flag.getFeatureId());
System.out.println("Enabled: " + flag.isEnabled());
System.out.println("Description: " + flag.getDescription());
System.out.println("Filters: " + flag.getClientFilters());
```

### Update Feature Flag

```java
FeatureFlagConfigurationSetting flag = (FeatureFlagConfigurationSetting)
    client.getConfigurationSetting(".appconfig.featureflag/beta-feature", null);

// Disable the feature
flag.setEnabled(false);

FeatureFlagConfigurationSetting updated = (FeatureFlagConfigurationSetting)
    client.setConfigurationSetting(flag);

System.out.println("Feature flag updated. Enabled: " + updated.isEnabled());
```

### List Feature Flags

```java
SettingSelector selector = new SettingSelector()
    .setKeyFilter(".appconfig.featureflag/*");

PagedIterable<ConfigurationSetting> flags = client.listConfigurationSettings(selector);

System.out.println("=== Feature Flags ===");
for (ConfigurationSetting setting : flags) {
    if (setting instanceof FeatureFlagConfigurationSetting) {
        FeatureFlagConfigurationSetting flag = (FeatureFlagConfigurationSetting) setting;
        System.out.printf("%s: %s%n", flag.getFeatureId(), flag.isEnabled() ? "ON" : "OFF");
    }
}
```

## Secret References

### Create Secret Reference

```java
import com.azure.data.appconfiguration.models.SecretReferenceConfigurationSetting;

SecretReferenceConfigurationSetting secretRef = new SecretReferenceConfigurationSetting(
    "app/secrets/api-key",                                    // Key
    "https://myvault.vault.azure.net/secrets/api-key"        // Key Vault secret URI
);

SecretReferenceConfigurationSetting created = (SecretReferenceConfigurationSetting)
    client.addConfigurationSetting(secretRef);

System.out.println("Secret reference created: " + created.getKey());
System.out.println("Points to: " + created.getSecretId());
```

### Get Secret Reference

```java
SecretReferenceConfigurationSetting ref = (SecretReferenceConfigurationSetting)
    client.getConfigurationSetting("app/secrets/api-key", null);

System.out.println("Secret URI: " + ref.getSecretId());

// To get the actual secret value, use Key Vault SDK
// SecretClient kvClient = new SecretClientBuilder()...
// KeyVaultSecret secret = kvClient.getSecret("api-key");
```

### Update Secret Reference

```java
SecretReferenceConfigurationSetting ref = (SecretReferenceConfigurationSetting)
    client.getConfigurationSetting("app/secrets/api-key", null);

// Point to a different secret version
ref.setSecretId("https://myvault.vault.azure.net/secrets/api-key/abc123");

client.setConfigurationSetting(ref);
```

## Read-Only Settings

### Set Read-Only

```java
ConfigurationSetting readOnly = client.setReadOnly(
    "app/critical/setting",
    "Production",
    true  // isReadOnly
);

System.out.println("Setting is now read-only: " + readOnly.isReadOnly());
```

### Clear Read-Only

```java
ConfigurationSetting writable = client.setReadOnly(
    "app/critical/setting",
    "Production",
    false  // make writable
);

System.out.println("Setting is writable: " + !writable.isReadOnly());
```

## Snapshots

### Create Snapshot

```java
import com.azure.data.appconfiguration.models.ConfigurationSnapshot;
import com.azure.data.appconfiguration.models.ConfigurationSettingsFilter;
import com.azure.core.util.polling.SyncPoller;
import com.azure.core.util.polling.PollOperationDetails;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

List<ConfigurationSettingsFilter> filters = new ArrayList<>();
filters.add(new ConfigurationSettingsFilter("app/*"));  // Include all app/* keys

SyncPoller<PollOperationDetails, ConfigurationSnapshot> poller = client.beginCreateSnapshot(
    "release-v1.0",
    new ConfigurationSnapshot(filters),
    Context.NONE
);

poller.setPollInterval(Duration.ofSeconds(10));
poller.waitForCompletion();

ConfigurationSnapshot snapshot = poller.getFinalResult();

System.out.println("=== Snapshot Created ===");
System.out.println("Name: " + snapshot.getName());
System.out.println("Status: " + snapshot.getStatus());
System.out.println("Item Count: " + snapshot.getItemCount());
System.out.println("Size: " + snapshot.getSizeInBytes() + " bytes");
System.out.println("Created: " + snapshot.getCreatedAt());
```

### Get Snapshot

```java
ConfigurationSnapshot snapshot = client.getSnapshot("release-v1.0");

System.out.println("Snapshot: " + snapshot.getName());
System.out.println("Status: " + snapshot.getStatus());
System.out.println("Items: " + snapshot.getItemCount());
System.out.println("Retention: " + snapshot.getRetentionPeriod());
```

### List Settings in Snapshot

```java
PagedIterable<ConfigurationSetting> settings = 
    client.listConfigurationSettingsForSnapshot("release-v1.0");

System.out.println("=== Settings in Snapshot ===");
for (ConfigurationSetting setting : settings) {
    System.out.printf("%s = %s%n", setting.getKey(), setting.getValue());
}
```

### Archive Snapshot

```java
ConfigurationSnapshot archived = client.archiveSnapshot("release-v1.0");
System.out.println("Status: " + archived.getStatus());  // archived
```

### Recover Snapshot

```java
ConfigurationSnapshot recovered = client.recoverSnapshot("release-v1.0");
System.out.println("Status: " + recovered.getStatus());  // ready
```

### List All Snapshots

```java
import com.azure.data.appconfiguration.models.SnapshotSelector;

SnapshotSelector selector = new SnapshotSelector()
    .setNameFilter("release-*");

PagedIterable<ConfigurationSnapshot> snapshots = client.listSnapshots(selector);

System.out.println("=== Snapshots ===");
for (ConfigurationSnapshot snap : snapshots) {
    System.out.printf("%s - %s (%d items)%n",
        snap.getName(),
        snap.getStatus(),
        snap.getItemCount());
}
```

## Labels

### List Labels

```java
import com.azure.data.appconfiguration.models.SettingLabelSelector;

PagedIterable<SettingLabel> labels = client.listLabels(
    new SettingLabelSelector().setNameFilter("*")
);

System.out.println("=== Labels ===");
for (SettingLabel label : labels) {
    System.out.println("Label: " + (label.getName() == null ? "(null)" : label.getName()));
}
```

## Async Operations

### Async List with Reactive Streams

```java
ConfigurationAsyncClient asyncClient = new ConfigurationClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint)
    .buildAsyncClient();

asyncClient.listConfigurationSettings(new SettingSelector().setLabelFilter("Production"))
    .subscribe(
        setting -> System.out.println(setting.getKey() + " = " + setting.getValue()),
        error -> System.err.println("Error: " + error.getMessage()),
        () -> System.out.println("Completed listing")
    );

// Keep application running for async operations
Thread.sleep(5000);
```

### Async Get and Set

```java
asyncClient.getConfigurationSetting("app/timeout", "Production")
    .flatMap(setting -> {
        setting.setValue("45000");
        return asyncClient.setConfigurationSetting(setting);
    })
    .subscribe(
        updated -> System.out.println("Updated: " + updated.getValue()),
        error -> System.err.println("Error: " + error.getMessage())
    );
```

## Error Handling

```java
import com.azure.core.exception.HttpResponseException;
import com.azure.core.exception.ResourceNotFoundException;

try {
    ConfigurationSetting setting = client.getConfigurationSetting("nonexistent", null);
} catch (ResourceNotFoundException e) {
    System.err.println("Setting not found");
} catch (HttpResponseException e) {
    int statusCode = e.getResponse().getStatusCode();
    
    switch (statusCode) {
        case 401:
            System.err.println("Unauthorized - check credentials");
            break;
        case 403:
            System.err.println("Forbidden - check permissions");
            break;
        case 409:
            System.err.println("Conflict - setting already exists or ETag mismatch");
            break;
        case 412:
            System.err.println("Precondition failed - setting was modified");
            break;
        case 429:
            System.err.println("Rate limited - retry with backoff");
            break;
        default:
            System.err.println("Error: " + e.getMessage());
    }
}
```

## Complete Application Example

```java
import com.azure.data.appconfiguration.ConfigurationClient;
import com.azure.data.appconfiguration.ConfigurationClientBuilder;
import com.azure.data.appconfiguration.models.*;
import com.azure.core.http.rest.PagedIterable;
import com.azure.identity.DefaultAzureCredentialBuilder;

import java.util.*;

public class AppConfigurationManager {
    
    private final ConfigurationClient client;
    private final String environment;
    
    public AppConfigurationManager(String environment) {
        this.client = new ConfigurationClientBuilder()
            .endpoint(System.getenv("AZURE_APPCONFIG_ENDPOINT"))
            .credential(new DefaultAzureCredentialBuilder().build())
            .buildClient();
        this.environment = environment;
    }
    
    public String getSetting(String key) {
        try {
            ConfigurationSetting setting = client.getConfigurationSetting(key, environment);
            return setting.getValue();
        } catch (Exception e) {
            // Try without label
            try {
                ConfigurationSetting setting = client.getConfigurationSetting(key, null);
                return setting.getValue();
            } catch (Exception ex) {
                return null;
            }
        }
    }
    
    public void setSetting(String key, String value) {
        client.setConfigurationSetting(key, environment, value);
    }
    
    public boolean isFeatureEnabled(String featureId) {
        try {
            String key = ".appconfig.featureflag/" + featureId;
            ConfigurationSetting setting = client.getConfigurationSetting(key, environment);
            
            if (setting instanceof FeatureFlagConfigurationSetting) {
                return ((FeatureFlagConfigurationSetting) setting).isEnabled();
            }
            
            // Try without label
            setting = client.getConfigurationSetting(key, null);
            if (setting instanceof FeatureFlagConfigurationSetting) {
                return ((FeatureFlagConfigurationSetting) setting).isEnabled();
            }
        } catch (Exception e) {
            // Feature flag doesn't exist - default to disabled
        }
        return false;
    }
    
    public void setFeatureEnabled(String featureId, boolean enabled) {
        String key = ".appconfig.featureflag/" + featureId;
        
        try {
            FeatureFlagConfigurationSetting flag = (FeatureFlagConfigurationSetting)
                client.getConfigurationSetting(key, environment);
            flag.setEnabled(enabled);
            client.setConfigurationSetting(flag);
        } catch (Exception e) {
            // Create new feature flag
            FeatureFlagConfigurationSetting newFlag = new FeatureFlagConfigurationSetting(featureId, enabled);
            newFlag.setLabel(environment);
            client.addConfigurationSetting(newFlag);
        }
    }
    
    public Map<String, String> getAllSettings(String prefix) {
        Map<String, String> result = new HashMap<>();
        
        SettingSelector selector = new SettingSelector()
            .setKeyFilter(prefix + "*")
            .setLabelFilter(environment);
        
        PagedIterable<ConfigurationSetting> settings = client.listConfigurationSettings(selector);
        
        for (ConfigurationSetting setting : settings) {
            if (!(setting instanceof FeatureFlagConfigurationSetting) 
                && !(setting instanceof SecretReferenceConfigurationSetting)) {
                result.put(setting.getKey(), setting.getValue());
            }
        }
        
        return result;
    }
    
    public void createSnapshot(String snapshotName, String keyPrefix) {
        List<ConfigurationSettingsFilter> filters = new ArrayList<>();
        filters.add(new ConfigurationSettingsFilter(keyPrefix + "*")
            .setLabel(environment));
        
        var poller = client.beginCreateSnapshot(snapshotName, new ConfigurationSnapshot(filters), null);
        poller.waitForCompletion();
        
        ConfigurationSnapshot snapshot = poller.getFinalResult();
        System.out.printf("Snapshot '%s' created with %d items%n", 
            snapshot.getName(), snapshot.getItemCount());
    }
    
    public static void main(String[] args) {
        AppConfigurationManager config = new AppConfigurationManager("Production");
        
        // Set some configuration
        config.setSetting("app/database/timeout", "30000");
        config.setSetting("app/cache/ttl", "3600");
        
        // Get configuration
        String timeout = config.getSetting("app/database/timeout");
        System.out.println("Database timeout: " + timeout);
        
        // Feature flags
        config.setFeatureEnabled("dark-mode", true);
        
        if (config.isFeatureEnabled("dark-mode")) {
            System.out.println("Dark mode is enabled");
        }
        
        // Get all app settings
        Map<String, String> appSettings = config.getAllSettings("app/");
        System.out.println("\n=== All App Settings ===");
        appSettings.forEach((key, value) -> 
            System.out.printf("%s = %s%n", key, value));
        
        // Create a snapshot for release
        config.createSnapshot("release-" + System.currentTimeMillis(), "app/");
    }
}
```

## Environment Variables

```bash
AZURE_APPCONFIG_CONNECTION_STRING=Endpoint=https://<store>.azconfig.io;Id=<id>;Secret=<secret>
AZURE_APPCONFIG_ENDPOINT=https://<store>.azconfig.io

# For DefaultAzureCredential
AZURE_CLIENT_ID=<service-principal-client-id>
AZURE_CLIENT_SECRET=<service-principal-secret>
AZURE_TENANT_ID=<tenant-id>
```

## Best Practices

1. **Use labels** — Separate configurations by environment (Dev, Staging, Production)
2. **Use snapshots** — Create immutable snapshots for releases
3. **Feature flags** — Use for gradual rollouts and A/B testing
4. **Secret references** — Store sensitive values in Key Vault, not App Configuration
5. **Conditional requests** — Use ETags for optimistic concurrency
6. **Read-only protection** — Lock critical production settings
7. **Use Entra ID** — Preferred over connection strings for security
8. **Async client** — Use for high-throughput scenarios
