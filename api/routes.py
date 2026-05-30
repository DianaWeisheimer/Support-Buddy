import logging
from fastapi import APIRouter, HTTPException

from services.ai_service import generate_suggestions, improve_message
from services.database_service import save_case, get_cases
from api.schemas import (SuggestRequest, SuggestResponse, ImproveRequest, ImproveResponse, CaseRecord)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/suggest", response_model=SuggestResponse)
def suggest_next_steps(body: SuggestRequest):
    """
    Recebe descrição do case e passos investigados,
    retorna sugestões de próximos passos geradas por IA.
    """
    logger.info("POST /suggest — case: %s", body.case_description[:60])
    try:
        suggestions = generate_suggestions(
            body.case_description,
            body.investigation_steps,
        )
        save_case(body.case_description, body.investigation_steps, suggestions)
        return SuggestResponse(suggestions=suggestions)
    except Exception as e:
        logger.error("Error in /suggest: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/improve", response_model=ImproveResponse)
def improve_customer_message(body: ImproveRequest):
    """
    Recebe rascunho de mensagem + contexto do case,
    retorna versão melhorada pela IA.
    """
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
    """
    Retorna todos os cases salvos no banco de dados.
    """
    logger.info("GET /cases")
    rows = get_cases()
    return [
        CaseRecord(
            id=row[0],
            case_description=row[1],
            investigation_steps=row[2],
            ai_response=row[3],
        )
        for row in rows
    ]