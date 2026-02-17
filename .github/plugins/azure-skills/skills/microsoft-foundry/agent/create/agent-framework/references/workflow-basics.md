# Python Workflow Basics

Executors, edges, and the WorkflowBuilder API — the foundation for all workflow patterns.

For more patterns, SEARCH the GitHub repository (github.com/microsoft/agent-framework) to get code snippets like: Agent as Edge, Custom Agent Executor, Workflow as Agent, Reflection, Condition, Switch-Case, Fan-out/Fan-in, Loop, Human in Loop, Concurrent, etc.

## Executor Node Definitions

| Style | When to Use | Example |
|-------|-------------|---------|
| `Executor` subclass + `@handler` | Nodes needing state or lifecycle hooks | `class MyNode(Executor)` |
| `@executor` decorator on function | Simple stateless steps | `@executor(id="my_step")` |
| `AgentExecutor(agent=..., id=...)` | Wrapping an existing agent (not subclassing) | `AgentExecutor(agent=my_agent, id="a1")` |
| Agent directly | Using agent as a node | `client.create_agent(name="...", ...)` (must provide `name`) |

## Handler Signature

```
(input: T, ctx: WorkflowContext[T_Out, T_W_Out]) -> None
```

- `T` = typed input from upstream node
- `ctx.send_message(T_Out)` → forwards to downstream nodes
- `ctx.yield_output(T_W_Out)` → yields workflow output (terminal nodes)
- `WorkflowContext[T_Out]` = shorthand for `WorkflowContext[T_Out, Never]`
- `WorkflowContext` (no params) = `WorkflowContext[Never, Never]`

> ⚠️ **Warning:** Previous node's output type must match next node's input type — check carefully when mixing node styles.

## Code Sample

```python
from typing_extensions import Never
from agent_framework import Executor, WorkflowBuilder, WorkflowContext, executor, handler

class UpperCase(Executor):
    def __init__(self, id: str):
        super().__init__(id=id)

    @handler
    async def to_upper_case(self, text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(text.upper())

@executor(id="reverse_text_executor")
async def reverse_text(text: str, ctx: WorkflowContext[Never, str]) -> None:
    await ctx.yield_output(text[::-1])

async def main():
    upper_case = UpperCase(id="upper_case_executor")
    workflow = WorkflowBuilder().add_edge(upper_case, reverse_text).set_start_executor(upper_case).build()

    # run() for simplicity; run_stream() is preferred for production
    events = await workflow.run("hello world")
    print(events.get_outputs())       # ['DLROW OLLEH']
    print(events.get_final_state())   # WorkflowRunState.IDLE
```
