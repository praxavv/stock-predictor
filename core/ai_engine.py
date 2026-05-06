import requests

def ask_ai(context):

    formatted_context = "\n".join(
        [f"{k}: {v}" for k, v in context.items()]
    )

    prompt = f"""
You are a financial analysis engine.

Rules:
- Do not explain.
- Do not give advice.
- Use ONLY provided data.
- Maximum 25 words.

Output format:
Trend: <Bullish/Bearish/Neutral>
Momentum: <Improving/Worsening/Stable>
Risk: <High/Medium/Low>

Data:
{formatted_context}

Response:
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "tinyllama",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.5,
                    "num_predict": 40,
                    "repeat_penalty": 1.2,
                    "stop": ["\n\n", "Data:", "Rules:"]
                }
            },
            timeout=15
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
