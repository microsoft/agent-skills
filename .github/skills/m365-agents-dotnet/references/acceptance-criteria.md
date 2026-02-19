# Microsoft 365 Agents SDK Acceptance Criteria (.NET)

**SDK**: `Microsoft.Agents.*` (Hosting.AspNetCore, Builder, Authentication.Msal, CopilotStudio.Client)
**Repository**: https://github.com/microsoft/agents
**NuGet Packages**: https://www.nuget.org/packages?q=Microsoft.Agents
**Purpose**: Skill testing acceptance criteria for validating generated C# code correctness

---

## 1. Correct Using Statements

### 1.1 Core Imports (Hosting)

#### CORRECT
```csharp
using Microsoft.Agents.Builder;
using Microsoft.Agents.Hosting.AspNetCore;
using Microsoft.Agents.Storage;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
```

### 1.2 Core Imports (AgentApplication)

#### CORRECT
```csharp
using Microsoft.Agents.Builder.App;
using Microsoft.Agents.Builder.State;
using Microsoft.Agents.Core.Models;
```

### 1.3 Core Imports (Copilot Studio Client)

#### CORRECT
```csharp
using Microsoft.Agents.CopilotStudio.Client;
using Microsoft.Identity.Client;
```

### 1.4 Anti-Patterns (ERRORS)

#### INCORRECT: Bot Framework namespaces
```csharp
using Microsoft.Bot.Builder;
using Microsoft.Bot.Builder.Integration.AspNet.Core;

var adapter = new BotFrameworkHttpAdapter();
```

---

## 2. Hosting Pipeline

### 2.1 CORRECT: ASP.NET Core registration
```csharp
builder.Services.AddHttpClient();
builder.AddAgentApplicationOptions();
builder.AddAgent<MyAgent>();
builder.Services.AddSingleton<IStorage, MemoryStorage>();

builder.Services.AddControllers();
builder.Services.AddAgentAspNetAuthentication(builder.Configuration);
```

### 2.2 CORRECT: /api/messages endpoint
```csharp
var incomingRoute = app.MapPost("/api/messages",
    async (HttpRequest request, HttpResponse response, IAgentHttpAdapter adapter, IAgent agent, CancellationToken ct) =>
    {
        await adapter.ProcessAsync(request, response, agent, ct);
    });
```

### 2.3 INCORRECT: Bot Framework adapter usage
```csharp
// WRONG - uses Bot Framework adapter instead of IAgentHttpAdapter
var adapter = new BotFrameworkHttpAdapter();
```

---

## 3. AgentApplication Routing

### 3.1 CORRECT: Activity handlers
```csharp
public sealed class MyAgent : AgentApplication
{
    public MyAgent(AgentApplicationOptions options) : base(options)
    {
        OnConversationUpdate(ConversationUpdateEvents.MembersAdded, WelcomeAsync);
        OnActivity(ActivityTypes.Message, OnMessageAsync, rank: RouteRank.Last);
        OnTurnError(OnTurnErrorAsync);
    }
}
```

### 3.2 CORRECT: Turn error handling
```csharp
await turnState.Conversation.DeleteStateAsync(turnContext, ct);

var endOfConversation = Activity.CreateEndOfConversationActivity();
endOfConversation.Code = EndOfConversationCodes.Error;
endOfConversation.Text = exception.Message;
await turnContext.SendActivityAsync(endOfConversation, ct);
```

### 3.3 INCORRECT: Bot Framework activity handler
```csharp
// WRONG - Bot Framework ActivityHandler is not used with Microsoft.Agents SDK
public class MyBot : ActivityHandler { }
```

---

## 4. Token Validation Configuration

### 4.1 CORRECT: appsettings.json section
```json
{
  "TokenValidation": {
    "Enabled": true,
    "Audiences": ["{{ClientId}}"],
    "TenantId": "{{TenantId}}"
  }
}
```

---

## 5. Copilot Studio Client Patterns

### 5.1 CORRECT: CopilotClient with IHttpClientFactory
```csharp
builder.Services.AddHttpClient("mcs").ConfigurePrimaryHttpMessageHandler(() =>
{
    return new AddTokenHandler(settings);
});

builder.Services.AddTransient<CopilotClient>(sp =>
{
    var logger = sp.GetRequiredService<ILoggerFactory>().CreateLogger<CopilotClient>();
    return new CopilotClient(settings, sp.GetRequiredService<IHttpClientFactory>(), logger, "mcs");
});
```

### 5.2 CORRECT: Start conversation and ask question
```csharp
await foreach (var activity in client.StartConversationAsync(emitStartConversationEvent: true))
{
    Console.WriteLine(activity.Type);
}

await foreach (var activity in client.AskQuestionAsync("Hello!", null))
{
    Console.WriteLine(activity.Type);
}
```

### 5.3 INCORRECT: DirectLine usage
```csharp
// WRONG - DirectLine client is not part of Microsoft.Agents SDK
var directLine = new DirectLineClient();
```
