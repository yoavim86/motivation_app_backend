from fastapi import APIRouter, Request, Depends, HTTPException
from app.auth.firebase import verify_firebase_token
from app.llm.provider import get_llm_provider
from app.rate_limit.limiter import RateLimiter
import logging

router = APIRouter()

@router.post("/chatAIProxy")
async def chat_ai_proxy(request: Request, user=Depends(verify_firebase_token)):
    body = await request.json()
    messages = body.get("messages")
    if not messages or not isinstance(messages, list):
        raise HTTPException(status_code=400, detail="Missing or invalid messages")
    user_id = user['uid']
    limiter = RateLimiter(user_id)
    # Estimate tokens (simple count, for demo)
    tokens = sum(len(m.get('content', '')) for m in messages)
    ok, reason = limiter.check(tokens)
    if not ok:
        raise HTTPException(status_code=429, detail=reason)
    llm = get_llm_provider()
    try:
        response = llm.chat(messages)
        limiter.increment(tokens)
        logging.info(f"User {user_id} proxied chatAI")
        return {"status": "success", "response": response}
    except Exception as e:
        logging.error(f"ChatAI error for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to proxy chat request") 