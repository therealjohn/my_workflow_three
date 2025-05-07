from enum import Enum

class CommonEvents(Enum):
    UserInputReceived = "UserInputReceived"
    AssistantResponseGenerated = "AssistantResponseGenerated"

class ChatBotEvents(Enum):
    StartProcess = "startProcess"
    IntroComplete = "introComplete"
    AssistantResponseGenerated = "assistantResponseGenerated"
    Exit = "exit"