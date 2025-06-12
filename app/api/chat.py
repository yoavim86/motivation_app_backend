from fastapi import APIRouter, Request, Depends, HTTPException
from app.auth.firebase import verify_firebase_token
from app.rate_limit.limiter import RateLimiter
from app.config import Config
import logging
import httpx

router = APIRouter()

@router.post("/chatAIProxy")
async def chat_ai_proxy(request: Request, user=Depends(verify_firebase_token)):
    body = await request.json()
    messages = body.get("messages")
    # Backend-enforced OpenAI parameters
    model = "gpt-4o-mini"
    max_tokens = 3000
    temperature = 0.7

    if not messages or not isinstance(messages, list):
        raise HTTPException(status_code=400, detail="Missing or invalid messages")
    user_id = user['uid']
    limiter = RateLimiter(user_id)
    tokens = sum(len(m.get('content', '')) for m in messages)
    ok, reason = limiter.check(tokens)
    if not ok:
        raise HTTPException(status_code=429, detail=reason)

    openai_api_key = Config.OPENAI_API_KEY
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
        if response.status_code == 200:
            data = response.json()
            reply = data["choices"][0]["message"]["content"].strip()
            limiter.increment(tokens)
            logging.info(f"User {user_id} proxied chatAI")
            return {"reply": reply}
        else:
            logging.error(f"OpenAI error for user {user_id}: {response.text}")
            raise HTTPException(status_code=500, detail=f"OpenAI error: {response.text}")
    except Exception as e:
        logging.error(f"ChatAI error for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to proxy chat request") 