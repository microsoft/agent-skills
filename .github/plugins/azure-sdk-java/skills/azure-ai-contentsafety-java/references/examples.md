# Azure AI Content Safety SDK for Java - Examples

Comprehensive code examples for the Azure AI Content Safety SDK for Java.

## Table of Contents
- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Analyzing Text Content](#analyzing-text-content)
- [Analyzing Image Content](#analyzing-image-content)
- [Handling Analysis Results](#handling-analysis-results)
- [Blocklist Management](#blocklist-management)
- [Async Client Patterns](#async-client-patterns)
- [Error Handling](#error-handling)

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-ai-contentsafety</artifactId>
    <version>1.0.16</version>
</dependency>

<!-- For DefaultAzureCredential authentication -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
    <version>1.14.2</version>
</dependency>
```

## Client Creation

### With API Key Credential

```java
import com.azure.ai.contentsafety.ContentSafetyClient;
import com.azure.ai.contentsafety.ContentSafetyClientBuilder;
import com.azure.ai.contentsafety.BlocklistClient;
import com.azure.ai.contentsafety.BlocklistClientBuilder;
import com.azure.core.credential.KeyCredential;
import com.azure.core.util.Configuration;

String endpoint = Configuration.getGlobalConfiguration().get("CONTENT_SAFETY_ENDPOINT");
String key = Configuration.getGlobalConfiguration().get("CONTENT_SAFETY_KEY");

// Content Safety client
ContentSafetyClient contentSafetyClient = new ContentSafetyClientBuilder()
    .credential(new KeyCredential(key))
    .endpoint(endpoint)
    .buildClient();

// Blocklist client
BlocklistClient blocklistClient = new BlocklistClientBuilder()
    .credential(new KeyCredential(key))
    .endpoint(endpoint)
    .buildClient();
```

### With DefaultAzureCredential (Microsoft Entra ID)

```java
import com.azure.identity.DefaultAzureCredentialBuilder;

// Set environment variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
ContentSafetyClient contentSafetyClient = new ContentSafetyClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint)
    .buildClient();

BlocklistClient blocklistClient = new BlocklistClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint)
    .buildClient();
```

## Analyzing Text Content

```java
import com.azure.ai.contentsafety.ContentSafetyClient;
import com.azure.ai.contentsafety.ContentSafetyClientBuilder;
import com.azure.ai.contentsafety.models.AnalyzeTextOptions;
import com.azure.ai.contentsafety.models.AnalyzeTextResult;
import com.azure.ai.contentsafety.models.TextCategoriesAnalysis;
import com.azure.core.credential.KeyCredential;
import com.azure.core.util.Configuration;

public class AnalyzeText {
    public static void main(String[] args) {
        String endpoint = Configuration.getGlobalConfiguration().get("CONTENT_SAFETY_ENDPOINT");
        String key = Configuration.getGlobalConfiguration().get("CONTENT_SAFETY_KEY");

        ContentSafetyClient contentSafetyClient = new ContentSafetyClientBuilder()
            .credential(new KeyCredential(key))
            .endpoint(endpoint)
            .buildClient();

        // Analyze text
        AnalyzeTextResult response = contentSafetyClient.analyzeText(
            new AnalyzeTextOptions("This is text example")
        );

        // Process results - iterate through harm categories
        for (TextCategoriesAnalysis result : response.getCategoriesAnalysis()) {
            System.out.println(result.getCategory() + " severity: " + result.getSeverity());
        }
    }
}
```

## Analyzing Image Content

```java
import com.azure.ai.contentsafety.ContentSafetyClient;
import com.azure.ai.contentsafety.ContentSafetyClientBuilder;
import com.azure.ai.contentsafety.models.AnalyzeImageOptions;
import com.azure.ai.contentsafety.models.AnalyzeImageResult;
import com.azure.ai.contentsafety.models.ContentSafetyImageData;
import com.azure.ai.contentsafety.models.ImageCategoriesAnalysis;
import com.azure.core.credential.KeyCredential;
import com.azure.core.util.BinaryData;
import com.azure.core.util.Configuration;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

public class AnalyzeImage {
    public static void main(String[] args) throws IOException {
        String endpoint = Configuration.getGlobalConfiguration().get("CONTENT_SAFETY_ENDPOINT");
        String key = Configuration.getGlobalConfiguration().get("CONTENT_SAFETY_KEY");

        ContentSafetyClient contentSafetyClient = new ContentSafetyClientBuilder()
            .credential(new KeyCredential(key))
            .endpoint(endpoint)
            .buildClient();

        // Load image from file
        ContentSafetyImageData image = new ContentSafetyImageData();
        String cwd = System.getProperty("user.dir");
        String source = "/src/samples/resources/image.png";
        image.setContent(BinaryData.fromBytes(Files.readAllBytes(Paths.get(cwd, source))));

        // Analyze image
        AnalyzeImageResult response = contentSafetyClient.analyzeImage(
            new AnalyzeImageOptions(image)
        );

        // Process results - iterate through harm categories
        for (ImageCategoriesAnalysis result : response.getCategoriesAnalysis()) {
            System.out.println(result.getCategory() + " severity: " + result.getSeverity());
        }
    }
}
```

## Handling Analysis Results

### Severity Levels and Content Moderation

```java
import com.azure.ai.contentsafety.ContentSafetyClient;
import com.azure.ai.contentsafety.ContentSafetyClientBuilder;
import com.azure.ai.contentsafety.models.*;
import com.azure.core.credential.KeyCredential;
import com.azure.core.util.Configuration;

public class HandleAnalysisResults {
    
    // Severity thresholds for content moderation decisions
    private static final int SEVERITY_SAFE = 0;
    private static final int SEVERITY_LOW = 2;
    private static final int SEVERITY_MEDIUM = 4;
    private static final int SEVERITY_HIGH = 6;
    
    public static void main(String[] args) {
        String endpoint = Configuration.getGlobalConfiguration().get("CONTENT_SAFETY_ENDPOINT");
        String key = Configuration.getGlobalConfiguration().get("CONTENT_SAFETY_KEY");

        ContentSafetyClient client = new ContentSafetyClientBuilder()
            .credential(new KeyCredential(key))
            .endpoint(endpoint)
            .buildClient();

        String textToAnalyze = "Sample text to analyze for harmful content";
        
        AnalyzeTextResult result = client.analyzeText(new AnalyzeTextOptions(textToAnalyze));
        
        // Process each harm category
        for (TextCategoriesAnalysis categoryResult : result.getCategoriesAnalysis()) {
            TextCategory category = categoryResult.getCategory();
            Integer severity = categoryResult.getSeverity();
            
            System.out.println("Category: " + category);
            System.out.println("Severity: " + severity);
            
            // Make moderation decisions based on severity
            // Categories: HATE, SEXUAL, VIOLENCE, SELF_HARM
            String action = determineModerationAction(severity);
            System.out.println("Recommended Action: " + action);
            System.out.println("---");
        }
        
        // Check if content should be blocked
        boolean shouldBlock = shouldBlockContent(result);
        System.out.println("Block Content: " + shouldBlock);
    }
    
    private static String determineModerationAction(Integer severity) {
        if (severity == null) {
            return "UNKNOWN";
        }
        
        if (severity <= SEVERITY_SAFE) {
            return "ALLOW - Content is safe";
        } else if (severity <= SEVERITY_LOW) {
            return "REVIEW - Low severity, may need human review";
        } else if (severity <= SEVERITY_MEDIUM) {
            return "FLAG - Medium severity, requires attention";
        } else {
            return "BLOCK - High severity, should be blocked";
        }
    }
    
    private static boolean shouldBlockContent(AnalyzeTextResult result) {
        for (TextCategoriesAnalysis categoryResult : result.getCategoriesAnalysis()) {
            Integer severity = categoryResult.getSeverity();
            if (severity != null && severity >= SEVERITY_MEDIUM) {
                return true;
            }
        }
        return false;
    }
}
```

## Blocklist Management

### Create or Update Blocklist

```java
import com.azure.ai.contentsafety.BlocklistClient;
import com.azure.ai.contentsafety.BlocklistClientBuilder;
import com.azure.core.credential.KeyCredential;
import com.azure.core.http.rest.RequestOptions;
import com.azure.core.http.rest.Response;
import com.azure.core.util.BinaryData;
import com.azure.core.util.Configuration;

import java.util.HashMap;
import java.util.Map;

String endpoint = Configuration.getGlobalConfiguration().get("CONTENT_SAFETY_ENDPOINT");
String key = Configuration.getGlobalConfiguration().get("CONTENT_SAFETY_KEY");

BlocklistClient blocklistClient = new BlocklistClientBuilder()
    .credential(new KeyCredential(key))
    .endpoint(endpoint)
    .buildClient();

// Create or update blocklist
String blocklistName = "TestBlocklist";
Map<String, String> description = new HashMap<>();
description.put("description", "Test Blocklist");
BinaryData resource = BinaryData.fromObject(description);
RequestOptions requestOptions = new RequestOptions();

Response<BinaryData> response = blocklistClient
    .createOrUpdateTextBlocklistWithResponse(blocklistName, resource, requestOptions);

if (response.getStatusCode() == 201) {
    System.out.println("Blocklist " + blocklistName + " created.");
} else if (response.getStatusCode() == 200) {
    System.out.println("Blocklist " + blocklistName + " updated.");
}
```

### Add Blocklist Items

```java
import com.azure.ai.contentsafety.models.AddOrUpdateTextBlocklistItemsOptions;
import com.azure.ai.contentsafety.models.AddOrUpdateTextBlocklistItemsResult;
import com.azure.ai.contentsafety.models.TextBlocklistItem;

import java.util.Arrays;
import java.util.List;

String blockItemText1 = "k*ll";
String blockItemText2 = "h*te";
List<TextBlocklistItem> blockItems = Arrays.asList(
    new TextBlocklistItem(blockItemText1).setDescription("Kill word"),
    new TextBlocklistItem(blockItemText2).setDescription("Hate word")
);

AddOrUpdateTextBlocklistItemsResult addedBlockItems = blocklistClient.addOrUpdateBlocklistItems(
    blocklistName,
    new AddOrUpdateTextBlocklistItemsOptions(blockItems)
);

if (addedBlockItems != null && addedBlockItems.getBlocklistItems() != null) {
    System.out.println("BlockItems added:");
    for (TextBlocklistItem addedBlockItem : addedBlockItems.getBlocklistItems()) {
        System.out.println("BlockItemId: " + addedBlockItem.getBlocklistItemId() 
            + ", Text: " + addedBlockItem.getText() 
            + ", Description: " + addedBlockItem.getDescription());
    }
}
```

### Analyze Text with Blocklist

```java
import com.azure.ai.contentsafety.ContentSafetyClient;
import com.azure.ai.contentsafety.models.AnalyzeTextOptions;
import com.azure.ai.contentsafety.models.AnalyzeTextResult;
import com.azure.ai.contentsafety.models.TextBlocklistMatch;

import java.util.Arrays;

// Note: After editing blocklist, wait ~5 minutes for changes to take effect
AnalyzeTextOptions request = new AnalyzeTextOptions("I h*te you and I want to k*ll you");
request.setBlocklistNames(Arrays.asList(blocklistName));
request.setHaltOnBlocklistHit(true);  // Stop analysis on first blocklist match

AnalyzeTextResult analyzeTextResult = contentSafetyClient.analyzeText(request);

// Check for blocklist matches
if (analyzeTextResult.getBlocklistsMatch() != null) {
    System.out.println("Blocklist matches found:");
    for (TextBlocklistMatch match : analyzeTextResult.getBlocklistsMatch()) {
        System.out.println("BlocklistName: " + match.getBlocklistName());
        System.out.println("BlocklistItemId: " + match.getBlocklistItemId());
        System.out.println("BlocklistItemText: " + match.getBlocklistItemText());
    }
}
```

### Remove Blocklist Items

```java
import com.azure.ai.contentsafety.models.RemoveTextBlocklistItemsOptions;

import java.util.Arrays;
import java.util.List;

List<String> blocklistItemIdsToRemove = Arrays.asList(
    "blocklistItemId1",
    "blocklistItemId2"
);

blocklistClient.removeBlocklistItems(
    blocklistName,
    new RemoveTextBlocklistItemsOptions(blocklistItemIdsToRemove)
);

System.out.println("Blocklist items removed.");
```

### List Blocklists and Items

```java
import com.azure.ai.contentsafety.models.TextBlocklist;
import com.azure.ai.contentsafety.models.TextBlocklistItem;
import com.azure.core.http.rest.PagedIterable;

// List all blocklists
PagedIterable<TextBlocklist> blocklists = blocklistClient.listTextBlocklists();
for (TextBlocklist blocklist : blocklists) {
    System.out.println("Blocklist: " + blocklist.getName());
    System.out.println("Description: " + blocklist.getDescription());
}

// List items in a blocklist
PagedIterable<TextBlocklistItem> items = blocklistClient.listTextBlocklistItems(blocklistName);
for (TextBlocklistItem item : items) {
    System.out.println("Item ID: " + item.getBlocklistItemId());
    System.out.println("Text: " + item.getText());
    System.out.println("Description: " + item.getDescription());
}
```

### Delete Blocklist

```java
blocklistClient.deleteTextBlocklist(blocklistName);
System.out.println("Blocklist " + blocklistName + " deleted.");
```

## Async Client Patterns

### Async Content Safety Client

```java
import com.azure.ai.contentsafety.ContentSafetyAsyncClient;
import com.azure.ai.contentsafety.ContentSafetyClientBuilder;
import com.azure.ai.contentsafety.models.AnalyzeTextOptions;
import com.azure.core.credential.KeyCredential;

ContentSafetyAsyncClient asyncClient = new ContentSafetyClientBuilder()
    .credential(new KeyCredential(key))
    .endpoint(endpoint)
    .buildAsyncClient();

// Async text analysis
asyncClient.analyzeText(new AnalyzeTextOptions("Text to analyze"))
    .subscribe(
        result -> {
            result.getCategoriesAnalysis().forEach(category -> {
                System.out.println(category.getCategory() + ": " + category.getSeverity());
            });
        },
        error -> System.err.println("Error: " + error.getMessage()),
        () -> System.out.println("Analysis completed")
    );
```

### Async Blocklist Client

```java
import com.azure.ai.contentsafety.BlocklistAsyncClient;
import com.azure.ai.contentsafety.BlocklistClientBuilder;

BlocklistAsyncClient asyncBlocklistClient = new BlocklistClientBuilder()
    .credential(new KeyCredential(key))
    .endpoint(endpoint)
    .buildAsyncClient();

// Async list blocklists
asyncBlocklistClient.listTextBlocklists()
    .subscribe(
        blocklist -> System.out.println("Found blocklist: " + blocklist.getName()),
        error -> System.err.println("Error: " + error.getMessage())
    );
```

## Error Handling

```java
import com.azure.core.exception.HttpResponseException;
import com.azure.ai.contentsafety.models.AnalyzeTextOptions;

public class ContentSafetyErrorHandling {
    public static void analyzeWithErrorHandling(ContentSafetyClient client, String text) {
        try {
            var result = client.analyzeText(new AnalyzeTextOptions(text));
            // Process result
            result.getCategoriesAnalysis().forEach(category -> {
                System.out.println(category.getCategory() + ": " + category.getSeverity());
            });
        } catch (HttpResponseException e) {
            int statusCode = e.getResponse().getStatusCode();
            System.err.println("HTTP Status: " + statusCode);
            System.err.println("Error: " + e.getMessage());
            
            switch (statusCode) {
                case 400:
                    System.err.println("Bad request - check input parameters");
                    break;
                case 401:
                    System.err.println("Unauthorized - check API key");
                    break;
                case 403:
                    System.err.println("Forbidden - check permissions");
                    break;
                case 404:
                    System.err.println("Resource not found");
                    break;
                case 429:
                    System.err.println("Rate limited - slow down requests");
                    break;
                default:
                    if (statusCode >= 500) {
                        System.err.println("Server error - retry later");
                    }
            }
        } catch (Exception e) {
            System.err.println("Unexpected error: " + e.getMessage());
        }
    }
}
```

### Async Error Handling

```java
asyncClient.analyzeText(new AnalyzeTextOptions(text))
    .subscribe(
        result -> {
            // Process result
        },
        error -> {
            if (error instanceof HttpResponseException) {
                HttpResponseException httpError = (HttpResponseException) error;
                System.err.println("HTTP error: " + httpError.getResponse().getStatusCode());
            } else {
                System.err.println("Error: " + error.getMessage());
            }
        }
    );
```
