---
name: playwright-ts
description: Run Playwright tests at scale using Microsoft Playwright Testing service. Use when scaling browser tests across cloud-hosted browsers, integrating with CI/CD pipelines, or publishing test results to the Playwright Portal.
---

# Azure Playwright Testing SDK for TypeScript

Run Playwright tests at scale with cloud-hosted browsers and centralized reporting.

> **Deprecation Notice:** `@azure/microsoft-playwright-testing` will be deprecated March 8, 2026. Migrate to `@azure/playwright`. See [migration guide](https://aka.ms/mpt/migration-guidance).

## Installation

```bash
# Recommended: Auto-generates config
npm init @azure/microsoft-playwright-testing@latest

# Manual installation
npm install @azure/microsoft-playwright-testing --save-dev
npm install @playwright/test@^1.47 --save-dev
```

## Environment Variables

```bash
PLAYWRIGHT_SERVICE_URL=wss://eastus.api.playwright.microsoft.com/accounts/{workspace-id}/browsers
```

## Authentication

### Microsoft Entra ID (Recommended)

```bash
# Sign in with Azure CLI
az login
```

```typescript
// playwright.service.config.ts
import { defineConfig } from "@playwright/test";
import { getServiceConfig, ServiceOS } from "@azure/microsoft-playwright-testing";
import config from "./playwright.config";

export default defineConfig(
  config,
  getServiceConfig(config, {
    os: ServiceOS.LINUX,
    // serviceAuthType defaults to ENTRA_ID
  }),
  {
    reporter: [["list"], ["@azure/microsoft-playwright-testing/reporter"]],
  }
);
```

### Custom Credential

```typescript
import { ManagedIdentityCredential } from "@azure/identity";
import { getServiceConfig } from "@azure/microsoft-playwright-testing";

export default defineConfig(
  config,
  getServiceConfig(config, {
    credential: new ManagedIdentityCredential(),
  })
);
```

## Core Workflow

### Service Configuration

```typescript
// playwright.service.config.ts
import { defineConfig } from "@playwright/test";
import { getServiceConfig, ServiceOS } from "@azure/microsoft-playwright-testing";
import config from "./playwright.config";

export default defineConfig(
  config,
  getServiceConfig(config, {
    os: ServiceOS.LINUX,
    timeout: 30000,
    exposeNetwork: "<loopback>",
    useCloudHostedBrowsers: true,
  }),
  {
    reporter: [
      ["list"],
      ["@azure/microsoft-playwright-testing/reporter", {
        enableGitHubSummary: true,
        enableResultPublish: true,
      }],
    ],
  }
);
```

### Run Tests

```bash
npx playwright test --config=playwright.service.config.ts --workers=20
```

### Reporting Only (Local Browsers)

```typescript
export default defineConfig(
  config,
  getServiceConfig(config, {
    useCloudHostedBrowsers: false, // Run locally, publish to portal
  }),
  {
    reporter: [["@azure/microsoft-playwright-testing/reporter"]],
  }
);
```

### Manual Browser Connection

```typescript
import playwright, { test, expect, BrowserType } from "@playwright/test";
import { getConnectOptions } from "@azure/microsoft-playwright-testing";

test("manual connection", async ({ browserName }) => {
  const { wsEndpoint, options } = await getConnectOptions();
  const browser = await (playwright[browserName] as BrowserType).connect(wsEndpoint, options);
  const context = await browser.newContext();
  const page = await context.newPage();

  await page.goto("https://example.com");
  await expect(page).toHaveTitle(/Example/);

  await browser.close();
});
```

## Configuration Options

```typescript
type PlaywrightServiceAdditionalOptions = {
  serviceAuthType?: "ENTRA_ID" | "ACCESS_TOKEN";  // Default: ENTRA_ID
  os?: "linux" | "windows";                        // Default: linux
  runId?: string;                                  // Default: ISO datetime
  runName?: string;                                // Default: guid
  timeout?: number;                                // Default: 30000ms
  slowMo?: number;                                 // Default: 0
  exposeNetwork?: string;                          // Default: <loopback>
  useCloudHostedBrowsers?: boolean;                // Default: true
  credential?: TokenCredential;                    // Default: DefaultAzureCredential
};
```

## CI/CD Integration

### GitHub Actions

```yaml
name: playwright-ts
on: [push, pull_request]

permissions:
  id-token: write
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - run: npm ci
      
      - name: Run Tests
        env:
          PLAYWRIGHT_SERVICE_URL: ${{ secrets.PLAYWRIGHT_SERVICE_URL }}
        run: npx playwright test -c playwright.service.config.ts --workers=20
```

### Azure Pipelines

```yaml
- task: AzureCLI@2
  displayName: Run Playwright Tests
  env:
    PLAYWRIGHT_SERVICE_URL: $(PLAYWRIGHT_SERVICE_URL)
  inputs:
    azureSubscription: My_Service_Connection
    scriptType: pscore
    inlineScript: |
      npx playwright test -c playwright.service.config.ts --workers=20
    addSpnToEnvironment: true
```

## Key Types

```typescript
import {
  getServiceConfig,
  getConnectOptions,
  ServiceOS,
  ServiceAuth,
  ServiceEnvironmentVariable,
} from "@azure/microsoft-playwright-testing";

import type {
  OsType,
  AuthenticationType,
  BrowserConnectOptions,
  ReporterConfiguration,
  PlaywrightServiceAdditionalOptions,
} from "@azure/microsoft-playwright-testing";
```

## Best Practices

1. **Use Entra ID auth** - More secure than access tokens
2. **Enable artifacts** - Set `trace: "on-first-retry"`, `video: "retain-on-failure"` in config
3. **Scale workers** - Use `--workers=20` or higher for parallel execution
4. **Region selection** - Choose region closest to your test targets
5. **Results retention** - Test results retained for 90 days in portal
