
from typing import ClassVar

from semantic_kernel.functions import kernel_function
from semantic_kernel.kernel_pydantic import KernelBaseModel
from semantic_kernel.processes.kernel_process.kernel_process_step import KernelProcessStep
from semantic_kernel.processes.kernel_process.kernel_process_step_state import KernelProcessStepState
from semantic_kernel.processes.kernel_process.kernel_process_step_context import KernelProcessStepContext

from my_workflow_three.events import ChatBotEvents, CommonEvents


class UserInputState(KernelBaseModel):
    user_inputs: list[str] = []
    current_input_index: int = 0

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

    @kernel_function(name=GET_USER_INPUT)
    async def get_user_input(self, context: KernelProcessStepContext):
        """Gets the user input."""
        if not self.state:
            raise ValueError("State has not been initialized")

        user_message = input("USER: ")

        # print(f"USER: {user_message}")

        if "exit" in user_message:
            await context.emit_event(process_event=ChatBotEvents.Exit, data=None)
            return

        self.state.current_input_index += 1

        # Emit the user input event
        await context.emit_event(process_event=CommonEvents.UserInputReceived, data=user_message)