import time
import asyncio
import hashlib
import json
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from backend.config import settings
from backend.db.redis_client import redis_client

# Configure Google Generative AI with the API key
genai.configure(api_key=settings.GEMINI_API_KEY)

# Global semaphore — only 1 Gemini call at a time to stay under rate limits
gemini_semaphore = asyncio.Semaphore(1)
INTER_CALL_DELAY = 4  # seconds between calls (stays under 15 RPM)
CACHE_TTL = 3600  # 1 hour

def get_gemini_model(model_name: str = "gemini-2.5-flash", tools=None):
    """
    Returns a configured GenerativeModel instance.
    Defaults to gemini-2.5-flash for reasoning.
    """
    return genai.GenerativeModel(model_name, tools=tools)

class CachedGeminiResponse:
    """Mock Gemini response object that exposes a `.text` property."""
    def __init__(self, text: str):
        self.text = text

def generate_cache_key(contents, **kwargs) -> str:
    """Generates a stable cache key based on the prompt contents and parameters."""
    serialized = ""
    if isinstance(contents, list):
        for item in contents:
            if isinstance(item, dict):
                # If there's binary image data, hash it to keep the key clean and stable via SHA-256
                if "data" in item and isinstance(item["data"], bytes):
                    img_hash = hashlib.sha256(item["data"]).hexdigest()
                    serialized += f"image_data:{img_hash};"
                else:
                    serialized += json.dumps(item, sort_keys=True) + ";"
            else:
                serialized += str(item) + ";"
    else:
        serialized = str(contents)
    
    # Include other settings like generation_config in the hash
    serialized += json.dumps(kwargs, sort_keys=True, default=str)
    return "gemini:" + hashlib.sha256(serialized.encode()).hexdigest()

def gemini_call_with_retry(model_or_chat, contents, max_retries=4, base_delay=15, method="generate_content", **kwargs):
    """Wraps any Gemini call with exponential backoff on ResourceExhausted."""
    for attempt in range(max_retries):
        try:
            func = getattr(model_or_chat, method)
            response = func(contents, **kwargs)
            return response
        except ResourceExhausted as e:
            err_msg = str(e)
            # Fail-fast if it's a daily limit exhaustion (retry won't help for 24 hours)
            if "GenerateRequestsPerDay" in err_msg or "limit: 20" in err_msg or "daily" in err_msg.lower():
                print(f"[Gemini] Daily quota limit hit ({err_msg}). Aborting retry immediately to trigger fallback.")
                raise e
            
            if attempt == max_retries - 1:
                raise  # give up after max retries
            wait = base_delay * (2 ** attempt)  # 15s, 30s, 60s, 120s
            print(f"[Gemini] 429 on attempt {attempt+1} using {method}. Retrying in {wait}s...")
            time.sleep(wait)

async def gemini_call_rate_limited(model_or_chat, contents, method="generate_content", bypass_cache=False, **kwargs):
    """
    Serializes and rate-limits Gemini calls, integrating Redis caching and exponential backoff retries.
    """
    # 1. Check cache first if caching is enabled
    cache_key = None
    if not bypass_cache and method == "generate_content":
        try:
            cache_key = generate_cache_key(contents, **kwargs)
            cached_val = redis_client.get(cache_key)
            if cached_val:
                print(f"[Gemini] Cache hit for key {cache_key} — skipping API call")
                # cached_val might have been double-json encoded or is a direct string
                try:
                    # Let's decode it safely
                    decoded = json.loads(cached_val)
                    if isinstance(decoded, str):
                        return CachedGeminiResponse(decoded)
                    return CachedGeminiResponse(cached_val)
                except Exception:
                    return CachedGeminiResponse(cached_val)
        except Exception as cache_err:
            print(f"[Gemini] Cache lookup error: {cache_err}")

    # 2. Acquire lock, perform rate-limited call in threadpool to avoid blocking event loop
    async with gemini_semaphore:
        print(f"[Gemini] Executing serialized {method} call...")
        response = await asyncio.to_thread(
            gemini_call_with_retry, model_or_chat, contents, method=method, **kwargs
        )
        
        # 3. Cache the result if successful
        if cache_key and response and hasattr(response, "text"):
            try:
                redis_client.setex(cache_key, CACHE_TTL, response.text)
            except Exception as cache_err:
                print(f"[Gemini] Cache save error: {cache_err}")

        # Enforce delay between calls to stay under RPM limits
        await asyncio.sleep(INTER_CALL_DELAY)
        return response
