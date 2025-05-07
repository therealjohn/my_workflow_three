from typing import Annotated
from datetime import datetime

from semantic_kernel.functions import kernel_function

class DatePlugin:
    @kernel_function(description="Provides the current date.")
    def get_current_date(self) -> Annotated[str, "Returns the current date."]:
        return datetime.now().strftime("%B %d, %Y")