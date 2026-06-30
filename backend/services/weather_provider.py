import httpx
from backend.models.models import WeatherSnapshot

class WeatherProvider:
    async def get_weather(self, lat: float, lng: float) -> WeatherSnapshot:
        raise NotImplementedError

class MockWeatherProvider(WeatherProvider):
    async def get_weather(self, lat: float, lng: float) -> WeatherSnapshot:
        return WeatherSnapshot(
            weather_condition="Overcast with Light Rain",
            rain_accumulation_mm=4.5,
            temperature_c=28.5,
            source="MockWeatherProvider"
        )

class OpenWeatherProvider(WeatherProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_weather(self, lat: float, lng: float) -> WeatherSnapshot:
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={self.api_key}&units=metric"
            async with httpx.AsyncClient() as client:
                res = await client.get(url, timeout=3.0)
                if res.status_code == 200:
                    data = res.json()
                    condition = data["weather"][0]["description"].title()
                    temp = data["main"]["temp"]
                    rain = data.get("rain", {}).get("1h", 0.0)
                    return WeatherSnapshot(
                        weather_condition=condition,
                        rain_accumulation_mm=float(rain),
                        temperature_c=float(temp),
                        source="OpenWeatherProvider API"
                    )
        except Exception as e:
            print(f"OpenWeather API query failed: {e}. Falling back to seasonal defaults.")
        
        # Safe default fallback if query fails (monsoon/summer default)
        return WeatherSnapshot(
            weather_condition="Scattered Clouds",
            rain_accumulation_mm=0.0,
            temperature_c=31.0,
            source="OpenWeatherProvider Fallback"
        )
