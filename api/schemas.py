from pydantic import BaseModel


class SuggestRequest(BaseModel):
    case_description: str
    investigation_steps: list[str]  # now a list, not text


class UpdateCaseRequest(BaseModel):
    case_description: str
    investigation_steps: list[str]


class ImproveRequest(BaseModel):
    customer_message: str
    tone: str
    case_description: str
    investigation_steps: str  # plain text is enough for the message


class SuggestResponse(BaseModel):
    suggestions: str


class ImproveResponse(BaseModel):
    improved_message: str


class CaseRecord(BaseModel):
    id: int
    case_description: str
    investigation_steps: list[str]  # list in the response as well
    ai_response: str
