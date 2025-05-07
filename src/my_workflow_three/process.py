
from enum import Enum

from semantic_kernel import Kernel
from semantic_kernel.processes.process_builder import ProcessBuilder
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.processes.kernel_process.kernel_process import KernelProcess

from my_workflow_three.events import CommonEvents, ChatBotEvents
from my_workflow_three.steps.chatbot_response_step import ChatBotResponseStep
from my_workflow_three.steps.intro_step import IntroStep
from my_workflow_three.steps.user_input_step import UserInputStep

class ChatProcess:
    def get_process(kernel: Kernel) -> KernelProcess:
        process = ProcessBuilder(name="ChatBot")

        # Define the steps on the process builder based on their types, not concrete objects
        intro_step = process.add_step(IntroStep)
        user_input_step = process.add_step(UserInputStep)
        response_step = process.add_step(ChatBotResponseStep)

        # Define the input event that starts the process and where to send it
        process.on_input_event(event_id=ChatBotEvents.StartProcess).send_event_to(target=intro_step)

        # Define the event that triggers the next step in the process
        intro_step.on_function_result(function_name=IntroStep.print_intro_message.__name__).send_event_to(
            target=user_input_step
        )

        # Define the event that triggers the process to stop
        user_input_step.on_event(event_id=ChatBotEvents.Exit).stop_process()
        # For the user step, send the user input to the response step
        user_input_step.on_event(event_id=CommonEvents.UserInputReceived).send_event_to(
            target=response_step, parameter_name="user_message"
        )

        # For the response step, send the response back to the user input step
        response_step.on_event(event_id=ChatBotEvents.AssistantResponseGenerated).send_event_to(target=user_input_step)

        return process.build()