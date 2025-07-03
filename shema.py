from pydantic import BaseModel


class PollData(BaseModel):
    question: str
    choice1: str
    choice2: str
    choice3: str | None
    choice4: str | None
    choice5: str | None
    model_config = {"extra": "forbid"}
