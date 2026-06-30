import google.generativeai as genai
from backend.config import settings

def test():
    print("API Key prefix:", settings.GEMINI_API_KEY[:8] if settings.GEMINI_API_KEY else "None")
    genai.configure(api_key=settings.GEMINI_API_KEY)
    
    # Try multiple models to see which one works
    models_to_try = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.0-flash-exp",
        "gemini-2.5-flash"
    ]
    
    for m_name in models_to_try:
        print(f"\nTrying model: {m_name}...")
        try:
            model = genai.GenerativeModel(m_name)
            res = model.generate_content("Say hello test.")
            print(f"Success with {m_name}: {res.text.strip()}")
            return
        except Exception as e:
            print(f"Failed with {m_name}: {type(e)} - {e}")

if __name__ == "__main__":
    test()
