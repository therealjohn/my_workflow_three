import yaml
from typing import ClassVar
from pydantic import Field
from pathlib import Path

from azure.identity.aio import DefaultAzureCredential


from semantic_kernel import Kernel
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import kernel_function
from semantic_kernel.kernel_pydantic import KernelBaseModel
from semantic_kernel.agents import AzureAIAgentThread, AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.processes.kernel_process.kernel_process_step import KernelProcessStep
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.processes.kernel_process.kernel_process_step_state import KernelProcessStepState
from semantic_kernel.processes.kernel_process.kernel_process_step_context import KernelProcessStepContext

from my_workflow_three.events import ChatBotEvents

class ChatBotState(KernelBaseModel):
    """The state object for ChatBotResponseStep."""
    thread: AzureAIAgentThread = None

class ChatBotResponseStep(KernelProcessStep):
    GET_CHAT_RESPONSE: ClassVar[str] = "get_chat_response"

    state: ChatBotState = Field(default_factory=ChatBotState)
    ai_agent_settings: AzureAIAgentSettings = Field(default_factory=AzureAIAgentSettings)

    async def activate(self, state: KernelProcessStepState[ChatBotState]):
        """Activates the step"""
        self.state = state.state or ChatBotState()

    @kernel_function(name=GET_CHAT_RESPONSE)
    async def get_chat_response(self, context: KernelProcessStepContext, user_message: str, kernel: Kernel):
        """Generates a response using AzureAIAgent."""

        agent_config = self._load_agent_config()

        async with (
            DefaultAzureCredential() as creds,
            AzureAIAgent.create_client(credential=creds) as client,
        ):
            
            # 1. Create an agent on the Azure AI agent service
            agent_definition = await client.agents.create_agent(
                model=agent_config["model"]["id"],
                name=agent_config["name"],
                instructions=agent_config["instructions"],
            )

            # 2. Create a Semantic Kernel agent for the Azure AI agent
            agent = AzureAIAgent(
                client=client,
                definition=agent_definition,
            )

            try:
                self.state.thread = self.state.thread or AzureAIAgentThread(client=client)

                response = await agent.get_response(messages=user_message, thread=self.state.thread)
                self.state.thread = response.thread
            except Exception as e:
                print(f"Error while getting response: {e}")
                response = None
            finally:
                await client.agents.delete_agent(agent.id)

        if response is None:
            raise ValueError("Failed to get a response from the Azure AI agent.")

        print(f"ASSISTANT: {response.content}")

        # Emit an event: assistantResponse
        await context.emit_event(process_event=ChatBotEvents.AssistantResponseGenerated, data=response.content)

    def _load_agent_config(self):
        """Load agent configuration from YAML file."""
        # Going up one level from steps directory to find config directory
        config_path = Path(__file__).parent.parent / "config" / "agents" / "chat_agent.yaml"
        with open(config_path, "r") as file:
            return yaml.safe_load(file)