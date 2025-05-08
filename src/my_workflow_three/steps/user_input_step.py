from typing import ClassVar, Optional
import os
import json

from semantic_kernel.functions import kernel_function
from semantic_kernel.kernel_pydantic import KernelBaseModel
from semantic_kernel.processes.kernel_process.kernel_process_step import KernelProcessStep
from semantic_kernel.processes.kernel_process.kernel_process_step_state import KernelProcessStepState
from semantic_kernel.processes.kernel_process.kernel_process_step_context import KernelProcessStepContext

from my_workflow_three.events import ChatBotEvents, CommonEvents


class UserInputState(KernelBaseModel):
    user_inputs: list[str] = []
    current_input_index: int = 0
    api_mode: bool = False
    api_inputs: list[str] = []
    api_input_index: int = 0

class UserInputStep(KernelProcessStep[UserInputState]):
    GET_USER_INPUT: ClassVar[str] = "get_user_input"

    def create_default_state(self) -> "UserInputState":
        """Creates the default UserInputState."""
        return UserInputState()

    def populate_user_inputs(self):
        """Method to be overridden by the user to populate with custom user messages."""
        pass

    async def activate(self, state: KernelProcessStepState[UserInputState]):
        """Activates the step and sets the state."""
        state.state = state.state or self.create_default_state()
        self.state = state.state
        self.populate_user_inputs()
        
        # Check if we're in API/container mode by looking for environment variable
        workflow_params = os.environ.get("WORKFLOW_PARAMS", "{}")
        try:
            params = json.loads(workflow_params)
            if isinstance(params, dict) and "inputs" in params and isinstance(params["inputs"], list):
                self.state.api_mode = True
                self.state.api_inputs = params["inputs"]
                print(f"Running in API mode with {len(self.state.api_inputs)} predefined inputs")
        except:
            pass

    @kernel_function(name=GET_USER_INPUT)
    async def get_user_input(self, context: KernelProcessStepContext):
        """Gets the user input."""
        if not self.state:
            raise ValueError("State has not been initialized")

        user_message = None
        
        # Check if we're in API mode with predefined inputs
        if self.state.api_mode and self.state.api_inputs:
            if self.state.api_input_index < len(self.state.api_inputs):
                user_message = self.state.api_inputs[self.state.api_input_index]
                self.state.api_input_index += 1
                print(f"USER: {user_message}")
            else:
                # No more inputs, exit
                print("No more predefined inputs, exiting workflow")
                await context.emit_event(process_event=ChatBotEvents.Exit, data=None)
                return
        else:
            # Try interactive mode, but fall back to a default response if in container
            try:
                user_message = input("USER: ")
            except EOFError:
                # In container/non-interactive environment
                user_message = "Hello"  # Default message
                print(f"USER: {user_message} (default non-interactive response)")

        if user_message and "exit" in user_message:
            await context.emit_event(process_event=ChatBotEvents.Exit, data=None)
            return

        self.state.current_input_index += 1

        # Emit the user input event
        await context.emit_event(process_event=CommonEvents.UserInputReceived, data=user_message)