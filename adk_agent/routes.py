from fastapi import APIRouter, Request, HTTPException
import json as _json
import logging
from .pydantic_models import ADKRequest, DSAResult
from .specialist_agent import handle_dsa_request

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/dsa", response_model=DSAResult)
async def dsa_endpoint(request: Request):
    payload = await request.json()
    src = payload.get("src")
    
    # DEBUG: log what we received
    logger.info(f"[ADK] Received src type: {type(src)}, value: {repr(src)[:200]}")
    
    if src is None:
        raise HTTPException(status_code=400, detail="src property is required and must be a valid JSON object")
    
    if isinstance(src, str):
        logger.info(f"[ADK] src is a string, attempting to parse...")
        try:
            payload["src"] = _json.loads(src)
            logger.info(f"[ADK] Successfully parsed src string")
        except Exception as e:
            logger.error(f"[ADK] Failed to parse src string: {e}")
            raise HTTPException(status_code=400, detail="src property must be a valid json object")
    elif not isinstance(src, dict):
        logger.error(f"[ADK] src is neither dict nor string: {type(src)}")
        raise HTTPException(status_code=400, detail="src property must be a valid json object")

    # Validate shape early
    try:
        ADKRequest(**payload)
    except Exception as e:
        logger.error(f"[ADK] ADKRequest validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    try:
        result = await handle_dsa_request(payload)
    except Exception as e:
        logger.error(f"[ADK] handle_dsa_request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return result
