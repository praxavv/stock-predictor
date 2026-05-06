import requests

def ask_ai(context):

    formatted_context = "\n".join(
        [f"{k}: {v}" for k, v in context.items()]
    )

    prompt = f"""
    You are a financial market classifier.
    
    Example:
    
    Trend: Bullish
    Momentum: Improving
    Risk: Medium
    
    Now analyze this market data:
    
    {formatted_context}
    
    Answer:
    """

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma:2b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "top_p": 0.9,
                    "num_predict": 60,
                    "repeat_penalty": 1.1,
                }
            },
            timeout=60
        )

        response.raise_for_status()
        result = response.json()

        return result.get("response", "").strip()   

    except requests.exceptions.RequestException:
        return (
            "💤 The AI Analyst is taking a nap right now.\n\n"
            "This assistant runs on Pranav's local machine, "
            "which means the AI only comes alive when his laptop is awake ⚡\n\n"
            "If you need market commentary, please summon Pranav 😄"
        )
