# Foundry Multi-Agent Workflow

Multi-agent loop workflow using Foundry project endpoint with `AzureAIClient`. Use this when building workflows with bidirectional edges (loops) and turn-based agent interaction.

> ⚠️ **Warning:** Use Foundry project endpoint, NOT Azure OpenAI endpoint. Use `AzureAIClient` (v2), not legacy `AzureAIAgentClient` (v1).

> 💡 **Tip:** Agent names: alphanumeric + hyphens, start/end alphanumeric, max 63 chars.

## Pattern: Student-Teacher Loop

Two Foundry agents interact in a loop with turn-based control.

```python
from agent_framework import (
    AgentRunEvent, ChatAgent, ChatMessage, Executor, Role,
    WorkflowBuilder, WorkflowContext, WorkflowOutputEvent, handler,
)
from agent_framework.azure import AzureAIClient
from azure.identity.aio import DefaultAzureCredential

ENDPOINT = "<your-foundry-project-endpoint>"
MODEL_DEPLOYMENT_NAME = "<your-foundry-model-deployment>"

class StudentAgentExecutor(Executor):
    agent: ChatAgent

    def __init__(self, agent: ChatAgent, id="student"):
        self.agent = agent
        super().__init__(id=id)

    @handler
    async def handle_teacher_question(
        self, messages: list[ChatMessage], ctx: WorkflowContext[list[ChatMessage]]
    ) -> None:
        response = await self.agent.run(messages)
        messages.extend(response.messages)
        await ctx.send_message(messages)

class TeacherAgentExecutor(Executor):
    turn_count: int = 0
    agent: ChatAgent

    def __init__(self, agent: ChatAgent, id="teacher"):
        self.agent = agent
        super().__init__(id=id)

    @handler
    async def handle_start_message(
        self, message: str, ctx: WorkflowContext[list[ChatMessage]]
    ) -> None:
        messages: list[ChatMessage] = [ChatMessage(Role.USER, text=message)]
        response = await self.agent.run(messages)
        messages.extend(response.messages)
        await ctx.send_message(messages)

    @handler
    async def handle_student_answer(
        self, messages: list[ChatMessage], ctx: WorkflowContext[list[ChatMessage], str]
    ) -> None:
        self.turn_count += 1
        if self.turn_count >= 5:
            await ctx.yield_output("Done!")
            return
        response = await self.agent.run(messages)
        messages.extend(response.messages)
        await ctx.send_message(messages)

async def main():
    async with (
        DefaultAzureCredential() as credential,
        AzureAIClient(
            project_endpoint=ENDPOINT,
            model_deployment_name=MODEL_DEPLOYMENT_NAME,
            credential=credential,
        ).create_agent(
            name="StudentAgent",
            instructions="You are Jamie, a student. Answer questions briefly.",
        ) as student_agent,
        AzureAIClient(
            project_endpoint=ENDPOINT,
            model_deployment_name=MODEL_DEPLOYMENT_NAME,
            credential=credential,
        ).create_agent(
            name="TeacherAgent",
            instructions="You are Dr. Smith. Ask ONE simple question at a time.",
        ) as teacher_agent
    ):
        # Use factories for cleaner state management in production
        workflow = (
            WorkflowBuilder()
            .register_executor(lambda: StudentAgentExecutor(student_agent), name="Student")
            .register_executor(lambda: TeacherAgentExecutor(teacher_agent), name="Teacher")
            .add_edge("Student", "Teacher")
            .add_edge("Teacher", "Student")
            .set_start_executor("Teacher")
            .build()
        )

        async for event in workflow.run_stream("Start the quiz session."):
            if isinstance(event, AgentRunEvent):
                print(f"\n{event.executor_id}: {event.data}")
            elif isinstance(event, WorkflowOutputEvent):
                print(f"\nDone: {event.data}")
                break
```
