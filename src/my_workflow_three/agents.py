from azure.identity.aio import DefaultAzureCredential
import yaml
import os
from pathlib import Path

from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings

class ChatAgents:
    ai_agent_settings = AzureAIAgentSettings()

    def _load_agent_config(self):
        """Load agent configuration from YAML file."""
        config_path = Path(__file__).parent / "config" / "agents" / "chat_agent.yaml"
        with open(config_path, "r") as file:
            return yaml.safe_load(file)

    async def chat_agent(self) -> AzureAIAgent:
        # Load agent configuration
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
        
        return agent