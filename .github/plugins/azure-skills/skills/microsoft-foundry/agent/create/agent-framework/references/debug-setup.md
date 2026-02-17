# Agent / Workflow Debugging

Support debugging for agent-framework-based agents or workflows locally in VSCode.

For agent as HTTP server, introduces `agentdev` tool, fully integrated with AI Toolkit Agent Inspector for interactive debugging and testing, supporting:
- agent and workflow execution
- visualize interactions and message flows
- monitor and trace multi-agent orchestration patterns
- troubleshoot complex workflow logic

(This doc applies to Python SDK only)

## Prerequisites

- (REQUIRED) Agent or workflow created using agent-framework SDK
- (REQUIRED) Running in HTTP server mode, i.e., using `azure.ai.agentserver.agentframework` SDK. If not, wrap the agent with `from_agent_framework(agent).run_async()` and install `azure-ai-agentserver-agentframework==1.0.0b10`.

## SDK Installations

Install `debugpy` for debugging support (used by VSCode Python Debugger Extension):

```bash
# install the latest one for better compatibility
pip install debugpy
```

Then, for HTTP server mode, install `agent-dev-cli` pre-release package (which introduces `agentdev` module and command):

```bash
pip install agent-dev-cli --pre
```

More `agentdev` usages:
```bash
# Run script with agentdev instrumentation
agentdev run my_agent.py
# Specify a custom port
agentdev run my_agent.py --port 9000
# Enable verbose output
agentdev run my_agent.py --verbose
# Pass arguments to script
agentdev run my_agent.py -- --server-mode --model ...
```

## Launch Command

The agent/workflow could be launched in either HTTP server mode or CLI mode, depending on the code implementation. To work with VSCode Python Debugger, need to wrap via `debugpy` module.

(Important) By default use the HTTP server mode with `agentdev` for full features. If the agent/workflow code supports CLI mode, could also launch in CLI mode for simpler debugging.

```bash
# HTTP server mode sample launch command
python <entrypoint>.py --server

# Wrapped with debugpy and agentdev
python -m debugpy --listen 127.0.0.1:5679 -m agentdev run <entrypoint>.py --verbose --port 8087 -- --server

# CLI mode sample launch command
python <entrypoint>.py --cli

# Wrapped with debugpy only
python -m debugpy --listen 127.0.0.1:5679 <entrypoint>.py --cli
```

## Example

Example configuration files for VSCode to enable debugging support.

### tasks.json

Run agent with debugging enabled. Note - no need to install dependencies via task (users may have their own python env).

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Validate prerequisites",
      // AI Toolkit built-in task to check port occupancy. Fixed type and command names, fixed args schema, but port numbers list can be customized
      "type": "aitk",
      "command": "debug-check-prerequisites",
      "args": {
        "portOccupancy": [5679, 8087]
      }
    },
    {
      // preferred - run agent as HTTP server
      "label": "Run Agent/Workflow HTTP Server",
      "type": "shell",
      // use `${command:python.interpreterPath}` to point to current user's python env
      "command": "${command:python.interpreterPath} -m debugpy --listen 127.0.0.1:5679 -m agentdev run <your_entrypoint.py> --verbose --port 8087 -- --server",
      "isBackground": true,
      "options": { "cwd": "${workspaceFolder}" },
      "dependsOn": ["Validate prerequisites"],
      // problem matcher to capture server startup
      "problemMatcher": {
        "pattern": [{ "regexp": "^.*$", "file": 0, "location": 1, "message": 2 }],
        "background": {
          "activeOnStart": true,
          "beginsPattern": ".*",
          // the fixed pattern for agent hosting startup
          "endsPattern": "Application startup complete|running on|Started server process"
        }
      }
    },
    {
      // for HTTP server mode - open the inspector after server is up
      "label": "Open Agent Inspector",
      "type": "shell",
      // the fixed command to open the inspector with port specified by arguments
      "command": "echo '${input:openAgentInspector}'",
      "presentation": { "reveal": "never" },
      "dependsOn": ["Run Agent/Workflow HTTP Server"]
    },
    {
      // alternative - run agent in CLI mode
      "label": "Run Agent/Workflow in Terminal",
      "type": "shell",
      // use `${command:python.interpreterPath}` to point to current user's python env
      "command": "${command:python.interpreterPath} -m debugpy --listen 127.0.0.1:5679 <your_entrypoint.py> --cli",
      "isBackground": true,
      "options": { "cwd": "${workspaceFolder}" },
      // problem matcher to capture startup
      "problemMatcher": {
        "pattern": [{ "regexp": "^.*$", "file": 0, "location": 1, "message": 2 }],
        "background": {
          "activeOnStart": true,
          "beginsPattern": ".*",
          // the pattern for startup
          "endsPattern": "Application startup complete|running on|Started server process"
        }
      }
    },
    {
      // util task for gracefully terminating
      "label": "Terminate All Tasks",
      "command": "echo ${input:terminate}",
      "type": "shell",
      "problemMatcher": []
    }
  ],
  "inputs": [
    {
      "id": "openAgentInspector",
      "type": "command",
      "command": "ai-mlstudio.openTestTool",
      // This port should match exactly the "--port" argument of the `agentdev` module
      "args": { "triggeredFrom": "tasks", "port": 8087 }
    },
    {
      "id": "terminate",
      "type": "command",
      "command": "workbench.action.tasks.terminate",
      "args": "terminateAll"
    }
  ]
}
```

### launch.json

Attach debugger to the running agent/workflow.

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      // preferred - debug HTTP server mode
      "name": "Debug Local Agent/Workflow HTTP Server",
      "type": "debugpy",
      "request": "attach",
      "connect": {
        "host": "localhost",
        // the same debugpy port as in tasks.json
        "port": 5679
      },
      // run the tasks before launching debugger
      "preLaunchTask": "Open Agent Inspector",
      "internalConsoleOptions": "neverOpen",
      // terminate all tasks after debugging session ends
      "postDebugTask": "Terminate All Tasks"
    },
    {
      // alternative - debug CLI mode
      "name": "Debug Local Agent/Workflow in Terminal",
      "type": "debugpy",
      "request": "attach",
      "connect": {
        "host": "localhost",
        // the same debugpy port as in tasks.json
        "port": 5679
      },
      // run the tasks before launching debugger
      "preLaunchTask": "Run Agent/Workflow in Terminal",
      "internalConsoleOptions": "neverOpen",
      // terminate all tasks after debugging session ends
      "postDebugTask": "Terminate All Tasks"
    }
  ]
}
```
