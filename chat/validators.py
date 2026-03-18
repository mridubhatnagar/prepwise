from pydantic import BaseModel, field_validator


class _MessageData(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def message_must_be_non_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("message must not be empty")
        if len(v) > 2000:
            raise ValueError("message must not exceed 2000 characters")
        return v


class PostMessageRequest(BaseModel):
    data: _MessageData
