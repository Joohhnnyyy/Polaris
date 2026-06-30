import httpx
from backend.config import settings

class RedisRESTClient:
    def __init__(self):
        self.url = settings.UPSTASH_REDIS_REST_URL
        self.token = settings.UPSTASH_REDIS_REST_TOKEN
        self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def get(self, key: str) -> str:
        if not self.url or not self.token:
            return None
        try:
            r = httpx.get(f"{self.url}/get/{key}", headers=self.headers)
            if r.status_code == 200:
                res = r.json()
                return res.get("result")
        except Exception as e:
            print(f"Upstash Redis GET failed: {e}")
        return None

    def setex(self, key: str, seconds: int, value: str):
        if not self.url or not self.token:
            return
        try:
            # Upstash REST SETEX expects: POST /setex/key/seconds/value
            # We can use payload or request format
            r = httpx.post(
                f"{self.url}/setex/{key}/{seconds}", 
                headers=self.headers,
                json=value # store as json value
            )
            if r.status_code != 200:
                print(f"Upstash Redis SETEX failed status: {r.status_code}")
        except Exception as e:
            print(f"Upstash Redis SETEX failed: {e}")

redis_client = RedisRESTClient()
