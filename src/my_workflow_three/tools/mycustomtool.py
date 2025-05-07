from typing import Annotated

from semantic_kernel.functions import kernel_function

class MycustomtoolTool:
    """A custom tool as a Semantic Kernel plugin."""

    @kernel_function(description="Provides mycustomtool functionality.")
    def get_mycustomtool(self) -> Annotated[str, "Returns mycustomtool information."]:
        return """
        This is the mycustomtool tool implementation.
        Add your custom logic here.
        """