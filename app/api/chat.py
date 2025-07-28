from fastapi import APIRouter, Request, Depends, HTTPException
from app.auth.firebase import verify_firebase_token
from app.rate_limit.limiter import RateLimiter
from app.core import get_openai_api_key, get_openai_chat_model
import logging
import httpx
import tiktoken
import os

router = APIRouter()

# Accurate token counting using tiktoken
# OpenAI's chat format: each message is a dict with 'role' and 'content'
def count_message_tokens(messages, model):
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = 0
    for m in messages:
        num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        for key, value in m.items():
            num_tokens += len(encoding.encode(str(value)))
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens

async def _chat_ai_proxy(messages, model, user_id):
    # Backend-enforced OpenAI parameters
    max_tokens = 400 # 100 words ≈ 130–140 tokens.
    temperature = 0.7

    if not messages or not isinstance(messages, list):
        raise HTTPException(status_code=400, detail="Missing or invalid messages")
    
    limiter = RateLimiter(user_id)
    tokens = count_message_tokens(messages, model)
    ok, reason = limiter.check(tokens)
    if not ok:
        logging.warning(f"Token check failed: {tokens} tokens in request. Reason: {reason}")
        raise HTTPException(status_code=429, detail=f"{reason} (tokens in request: {tokens})")

    openai_api_key = get_openai_api_key()
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

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
    if response.status_code == 200:
        data = response.json()
        reply = data["choices"][0]["message"]["content"].strip()
        # Use actual prompt_tokens from OpenAI response if available
        usage = data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", tokens)
        limiter.increment(prompt_tokens)
        logging.info(f"User {user_id} proxied chatAI with usage: {usage}")
        return {"reply": reply}
    else:
        logging.error(f"OpenAI error for user {user_id}: {response.text}")
        raise HTTPException(status_code=500, detail=f"OpenAI error: {response.text}")

@router.post("/chatAIProxy")
async def chat_ai_proxy(request: Request, user=Depends(verify_firebase_token)):
    body = await request.json()
    messages = body.get("messages")
    user_id = user['uid']
    
    # Try with default model first
    model = get_openai_chat_model()
    try:
        return await _chat_ai_proxy(messages, model, user_id)
    except Exception as e:
        # If the primary model fails, try with gpt-3.5-turbo
        logging.warning(f"Primary model failed for user {user_id}, falling back to gpt-3.5-turbo. Error: {e}")
        try:
            return await _chat_ai_proxy(messages, "gpt-3.5-turbo", user_id)
        except Exception as fallback_error:
            logging.error(f"Fallback model also failed for user {user_id}: {fallback_error}")
            raise HTTPException(status_code=500, detail="Failed to proxy chat request") 