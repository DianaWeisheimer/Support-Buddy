import logging
from fastapi import APIRouter, HTTPException

from services.ai_service import generate_suggestions, improve_message
from services.database_service import save_case, update_case, get_cases, json_to_steps
from api.schemas import (
    SuggestRequest, SuggestResponse,
    ImproveRequest, ImproveResponse,
    UpdateCaseRequest,
    CaseRecord,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/suggest", response_model=SuggestResponse)
def suggest_next_steps(body: SuggestRequest):
    logger.info("POST /suggest — case: %s", body.case_description[:60])
    try:
        # Junta a lista de steps em texto para mandar pra IA
        steps_text = "\n".join(
            f"{i+1}. {s}" for i, s in enumerate(body.investigation_steps)
        )
        suggestions = generate_suggestions(body.case_description, steps_text)
        save_case(body.case_description, body.investigation_steps, suggestions)
        return SuggestResponse(suggestions=suggestions)
    except Exception as e:
        logger.error("Error in /suggest: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/cases/{case_id}", response_model=SuggestResponse)
def update_case_steps(case_id: int, body: UpdateCaseRequest):
    """Atualiza os steps de um case existente e gera novas sugestões."""
    logger.info("PUT /cases/%d", case_id)
    try:
        steps_text = "\n".join(
            f"{i+1}. {s}" for i, s in enumerate(body.investigation_steps)
        )
        suggestions = generate_suggestions(body.case_description, steps_text)
        update_case(case_id, body.investigation_steps, suggestions)
        return SuggestResponse(suggestions=suggestions)
    except Exception as e:
        logger.error("Error in PUT /cases/%d: %s", case_id, e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/improve", response_model=ImproveResponse)
def improve_customer_message(body: ImproveRequest):
    logger.info("POST /improve")
    try:
        improved = improve_message(
            body.customer_message,
            body.case_description,
            body.investigation_steps,
        )
        return ImproveResponse(improved_message=improved)
    except Exception as e:
        logger.error("Error in /improve: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cases", response_model=list[CaseRecord])
def list_cases():
    logger.info("GET /cases")
    rows = get_cases()
    return [
        CaseRecord(
            id=row[0],
            case_description=row[1],
            investigation_steps=json_to_steps(row[2]),
            ai_response=row[3],
        )
        for row in rows
    ]
