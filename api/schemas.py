from pydantic import BaseModel

# --- Request bodies ---

class SuggestRequest(BaseModel):
    case_description: str
    investigation_steps: str


class ImproveRequest(BaseModel):
    customer_message: str
    case_description: str
    investigation_steps: str

# --- Response bodies ---

class SuggestResponse(BaseModel):
    suggestions: str


class ImproveResponse(BaseModel):
    improved_message: str


class CaseRecord(BaseModel):
    id: int
    case_description: str
    investigation_steps: str
    ai_response: str