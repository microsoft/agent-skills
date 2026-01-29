# Browser Authentication Reference

Browser-based authentication for Azure services using the @azure/identity TypeScript SDK.

## Overview

Browser applications require special credential types that handle OAuth redirects and popup windows. This reference covers `InteractiveBrowserCredential`, `BrowserCustomizationOptions`, and SPA authentication patterns.

## Installation

```bash
npm install @azure/identity
```

**Note:** Browser credentials require a bundler (Vite, webpack, etc.) and won't work in Node.js.

## InteractiveBrowserCredential

The primary credential for browser applications.

```typescript
import { InteractiveBrowserCredential } from "@azure/identity";

const credential = new InteractiveBrowserCredential({
  clientId: "<your-app-client-id>",
  tenantId: "<your-tenant-id>",
});

// Use with Azure SDK clients
import { BlobServiceClient } from "@azure/storage-blob";
const blobClient = new BlobServiceClient(
  "https://myaccount.blob.core.windows.net",
  credential
);
```

## App Registration Requirements

Your Azure AD app registration needs:

1. **Platform:** Single-page application (SPA)
2. **Redirect URIs:** 
   - `http://localhost:3000` (development)
   - `https://yourapp.com` (production)
3. **API Permissions:** Configure based on services you're accessing
4. **Implicit grant:** Access tokens (for MSAL.js implicit flow)

## Authentication Modes

### Popup Mode (Default)

```typescript
import { InteractiveBrowserCredential } from "@azure/identity";

const credential = new InteractiveBrowserCredential({
  clientId: "<client-id>",
  tenantId: "<tenant-id>",
  // Popup is default - no loginStyle needed
});

// Triggers popup on first getToken call
const token = await credential.getToken("https://storage.azure.com/.default");
```

### Redirect Mode

```typescript
import { InteractiveBrowserCredential } from "@azure/identity";

const credential = new InteractiveBrowserCredential({
  clientId: "<client-id>",
  tenantId: "<tenant-id>",
  loginStyle: "redirect",
  redirectUri: window.location.origin, // Must match app registration
});

// Redirects to Azure AD, then back to your app
const token = await credential.getToken("https://storage.azure.com/.default");
```

### Handling Redirect Response

```typescript
import { InteractiveBrowserCredential } from "@azure/identity";

// On app load, check for redirect response
const credential = new InteractiveBrowserCredential({
  clientId: "<client-id>",
  tenantId: "<tenant-id>",
  loginStyle: "redirect",
  redirectUri: window.location.origin,
});

// This will handle the response if returning from redirect
try {
  const token = await credential.getToken("https://storage.azure.com/.default");
  console.log("Authenticated successfully");
} catch (error) {
  console.error("Authentication failed:", error);
}
```

## Configuration Options

```typescript
interface InteractiveBrowserCredentialNodeOptions {
  /** Application client ID */
  clientId: string;
  
  /** Azure AD tenant ID */
  tenantId?: string;
  
  /** Redirect URI (must match app registration) */
  redirectUri?: string;
  
  /** Login style: "popup" or "redirect" */
  loginStyle?: "popup" | "redirect";
  
  /** Pre-fill username hint */
  loginHint?: string;
  
  /** Force re-authentication */
  disableAutomaticAuthentication?: boolean;
  
  /** Authority host for sovereign clouds */
  authorityHost?: string;
  
  /** Custom browser customization */
  browserCustomizationOptions?: BrowserCustomizationOptions;
}
```

## Login Hint

Pre-fill the username to skip account selection:

```typescript
const credential = new InteractiveBrowserCredential({
  clientId: "<client-id>",
  tenantId: "<tenant-id>",
  loginHint: "user@example.com", // Pre-fills email
});
```

## Token Caching

The credential automatically caches tokens in browser storage:

```typescript
const credential = new InteractiveBrowserCredential({
  clientId: "<client-id>",
  tenantId: "<tenant-id>",
});

// First call - triggers interactive login
await credential.getToken("https://storage.azure.com/.default");

// Subsequent calls - uses cached token (no prompt)
await credential.getToken("https://storage.azure.com/.default");
```

## Silent Authentication

Attempt silent auth first, fall back to interactive:

```typescript
import { InteractiveBrowserCredential } from "@azure/identity";

const credential = new InteractiveBrowserCredential({
  clientId: "<client-id>",
  tenantId: "<tenant-id>",
  disableAutomaticAuthentication: true, // Don't auto-prompt
});

async function getTokenSilentlyOrInteractive(scope: string): Promise<string> {
  try {
    // Try silent first
    const token = await credential.getToken(scope);
    return token.token;
  } catch (error) {
    // Silent failed - trigger interactive
    const token = await credential.authenticate(scope);
    return token.token;
  }
}
```

## Multi-Tenant Applications

```typescript
const credential = new InteractiveBrowserCredential({
  clientId: "<client-id>",
  tenantId: "common", // Allow any Azure AD tenant
  // Or "organizations" for work/school accounts only
  // Or "consumers" for personal Microsoft accounts only
});
```

## React Integration Example

```typescript
// auth.ts
import { InteractiveBrowserCredential } from "@azure/identity";

let credentialInstance: InteractiveBrowserCredential | null = null;

export function getCredential(): InteractiveBrowserCredential {
  if (!credentialInstance) {
    credentialInstance = new InteractiveBrowserCredential({
      clientId: import.meta.env.VITE_AZURE_CLIENT_ID,
      tenantId: import.meta.env.VITE_AZURE_TENANT_ID,
      redirectUri: window.location.origin,
    });
  }
  return credentialInstance;
}

export async function login(): Promise<void> {
  const credential = getCredential();
  await credential.authenticate(["https://storage.azure.com/.default"]);
}

// App.tsx
import { useState } from "react";
import { BlobServiceClient } from "@azure/storage-blob";
import { getCredential, login } from "./auth";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  const handleLogin = async () => {
    try {
      await login();
      setIsAuthenticated(true);
    } catch (error) {
      console.error("Login failed:", error);
    }
  };
  
  const listBlobs = async () => {
    const credential = getCredential();
    const client = new BlobServiceClient(
      "https://myaccount.blob.core.windows.net",
      credential
    );
    
    for await (const container of client.listContainers()) {
      console.log(container.name);
    }
  };
  
  return (
    <div>
      {!isAuthenticated ? (
        <button onClick={handleLogin}>Login with Azure</button>
      ) : (
        <button onClick={listBlobs}>List Blobs</button>
      )}
    </div>
  );
}
```

## Error Handling

```typescript
import { 
  InteractiveBrowserCredential,
  AuthenticationRequiredError,
  CredentialUnavailableError
} from "@azure/identity";

const credential = new InteractiveBrowserCredential({
  clientId: "<client-id>",
  tenantId: "<tenant-id>",
});

try {
  const token = await credential.getToken("https://storage.azure.com/.default");
} catch (error) {
  if (error instanceof AuthenticationRequiredError) {
    // User needs to authenticate
    console.log("Please sign in");
    await credential.authenticate(["https://storage.azure.com/.default"]);
  } else if (error instanceof CredentialUnavailableError) {
    // Credential not usable in this environment
    console.error("Browser authentication not available");
  } else {
    // Other error (network, consent denied, etc.)
    console.error("Authentication error:", error);
  }
}
```

## Logout

The credential doesn't provide direct logout. Use MSAL.js or redirect to logout URL:

```typescript
function logout() {
  const logoutUrl = new URL(
    `https://login.microsoftonline.com/${tenantId}/oauth2/v2.0/logout`
  );
  logoutUrl.searchParams.set("post_logout_redirect_uri", window.location.origin);
  
  window.location.href = logoutUrl.toString();
}
```

## Sovereign Clouds

```typescript
import { 
  InteractiveBrowserCredential, 
  AzureAuthorityHosts 
} from "@azure/identity";

// Azure Government
const govCredential = new InteractiveBrowserCredential({
  clientId: "<client-id>",
  tenantId: "<tenant-id>",
  authorityHost: AzureAuthorityHosts.AzureGovernment,
});

// Azure China
const chinaCredential = new InteractiveBrowserCredential({
  clientId: "<client-id>",
  tenantId: "<tenant-id>",
  authorityHost: AzureAuthorityHosts.AzureChina,
});
```

## DeviceCodeCredential (Alternative)

For environments without browser capability (CLI tools, IoT):

```typescript
import { DeviceCodeCredential } from "@azure/identity";

const credential = new DeviceCodeCredential({
  clientId: "<client-id>",
  tenantId: "<tenant-id>",
  userPromptCallback: (info) => {
    // Display to user
    console.log(info.message);
    // "To sign in, use a web browser to open the page
    //  https://microsoft.com/devicelogin and enter the code ABC123"
  },
});

const token = await credential.getToken("https://storage.azure.com/.default");
```

## CORS Configuration

Azure services need CORS configured for browser access:

**Azure Storage:**
```typescript
import { BlobServiceClient } from "@azure/storage-blob";

// Configure CORS via Azure Portal or CLI:
// az storage cors add --services b --methods GET,PUT,POST,DELETE,HEAD \
//   --origins "http://localhost:3000" --allowed-headers "*" \
//   --exposed-headers "*" --max-age 3600 --account-name <account>
```

## Best Practices

1. **Use popup for UX** — Better user experience than redirect
2. **Handle redirect on load** — Check for redirect response on app initialization
3. **Cache the credential instance** — Don't create new instances repeatedly
4. **Configure CORS** — Required for browser-to-Azure communication
5. **Use environment variables** — Don't hardcode client IDs
6. **Handle authentication errors** — Provide clear feedback to users
7. **Implement logout** — Clear session and redirect to Azure logout
8. **Test both flows** — Popup may be blocked; redirect is fallback

## Security Considerations

- Never expose client secrets in browser code
- Use SPA platform type in app registration (PKCE)
- Validate tokens server-side for sensitive operations
- Configure appropriate redirect URIs
- Use secure (HTTPS) redirect URIs in production

## See Also

- [Credential Types Reference](./credential-types.md)
- [MSAL.js Documentation](https://learn.microsoft.com/azure/active-directory/develop/msal-js-initializing-client-applications)
- [SPA Authentication](https://learn.microsoft.com/azure/active-directory/develop/scenario-spa-overview)
