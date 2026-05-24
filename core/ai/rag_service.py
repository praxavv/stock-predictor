import os
from typing import List
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from core.ai.news_scraper import get_latest_news
import time

# Configuration
OLLAMA_MODEL = "gemma3:270m"

class RAGService:
    def __init__(self):
        # Balanced num_predict for better quality vs speed
        self.llm = ChatOllama(
            model=OLLAMA_MODEL, 
            temperature=0,
            num_predict=200
        )
        self.news_data = []

    def refresh_news_database(self):
        """Fetch latest news and store it in memory."""
        news_items = get_latest_news()
        self.news_data = []
        for item in news_items:
            # Moderate length: Title + 200 chars of summary
            content = f"[{item['source']}] {item['title']}: {item['summary'][:200]}"
            self.news_data.append(content)
        
        return len(self.news_data)

    def get_market_summary(self, query: str = "Provide a 3-bullet summary of the latest news.") -> str:
        if not self.news_data:
            self.refresh_news_database()
            if not self.news_data:
                return "No news data available."

        # Use all 6 items (3 from each source)
        context_text = "\n".join(self.news_data)

        prompt_template = ChatPromptTemplate.from_template("""
        Context:
        {context}

        Question: {question}
        Answer in exactly 3 bullet points:
        """)

        prompt = prompt_template.format(context=context_text, question=query)
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Error: {str(e)}"

# Singleton instance
rag_service = RAGService()

def refresh_news():
    return rag_service.refresh_news_database()

def get_ai_summary(query: str = "Provide a 3-bullet summary of the latest news."):
    return rag_service.get_market_summary(query)
