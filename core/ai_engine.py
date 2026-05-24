import requests

# Use the same model as RAG for consistency and speed
OLLAMA_MODEL = "gemma3:270m"

def ask_ai(context):
    """
    Generate a concise financial report using a small model.
    The prompt is heavily structured to aid small models (like gemma3:270m).
    """
    
    ticker = context.get('ticker', 'Unknown')
    news = context.get('news_summary', 'No major news.')
    
    prompt = f"""[INST] You are a professional financial analyst. Provide a brief, high-signal report.

MARKET CONTEXT:
{news}

STOCK ANALYSIS FOR {ticker}:
- Price: ${context.get('latest_price')}
- Indicator: RSI is {context.get('rsi')}, MA50 is {context.get('ma50')}
- Prediction: {context.get('signal')} ({context.get('confidence')*100:.1f}% confidence)

TASK:
Combine market context and stock data into a 2-sentence summary. 
Be direct. No fluff. Focus on trend and sentiment. [/INST]"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 100,
                    "top_p": 0.9,
                }
            },
            timeout=30
        )

        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()   

    except Exception as e:
        return f"AI Service Error: {str(e)}"
