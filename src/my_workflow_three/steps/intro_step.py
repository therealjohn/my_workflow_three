
from semantic_kernel.functions import kernel_function
from semantic_kernel.processes.kernel_process.kernel_process_step import KernelProcessStep

class IntroStep(KernelProcessStep):
    @kernel_function
    async def print_intro_message(self):
        print("Welcome to Processes in Semantic Kernel.\n")