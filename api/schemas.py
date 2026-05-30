from pydantic import BaseModel


class SuggestRequest(BaseModel):
    case_description: str
    investigation_steps: list[str]  # agora é lista, não texto


class UpdateCaseRequest(BaseModel):
    case_description: str
    investigation_steps: list[str]


class ImproveRequest(BaseModel):
    customer_message: str
    case_description: str
    investigation_steps: str  # para mensagem, texto puro é suficiente


class SuggestResponse(BaseModel):
    suggestions: str


class ImproveResponse(BaseModel):
    improved_message: str


class CaseRecord(BaseModel):
    id: int
    case_description: str
    investigation_steps: list[str]  # lista no retorno também
    ai_response: str
