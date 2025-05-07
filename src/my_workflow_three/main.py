import asyncio

from my_workflow_three.process import ChatProcess
from my_workflow_three.events import ChatBotEvents

from semantic_kernel import Kernel

async def run_async():
    from semantic_kernel.processes.local_runtime.local_kernel_process import start
    kernel = Kernel()    
    kernel_process = ChatProcess.get_process(kernel)

    await start(
        process=kernel_process,
        kernel=kernel,
        initial_event=ChatBotEvents.StartProcess,
    )

def run():
    """Synchronous wrapper for the async run function that Poetry can use as an entry point"""
    asyncio.run(run_async())

async def run_dapr_async():
    from semantic_kernel.processes.dapr_runtime import start
    kernel = Kernel()    
    kernel_process = ChatProcess.get_process(kernel)

    await start(
        process=kernel_process,
        kernel=kernel,
        initial_event=ChatBotEvents.StartProcess,
    )

def run_dapr():
    """Synchronous wrapper for the async serve function that Poetry can use as an entry point"""
    asyncio.run(run_dapr_async())

if __name__ == "__main__":
    asyncio.run(run())