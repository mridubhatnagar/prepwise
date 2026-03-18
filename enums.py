from enum import Enum


class MessageRole(str, Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"


class Scope(str, Enum):
    APP = "app"
    DOCS = "docs"
