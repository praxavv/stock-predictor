import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai.rag_service import refresh_news, get_ai_summary

def test_rag():
    print("Refreshing market news...")
    try:
        count = refresh_news()
        print(f"Indexed {count} news items.")
    except Exception as e:
        print(f"Failed to refresh news: {e}")
        return

    print("\nGenerating Market Summary...")
    try:
        summary = get_ai_summary()
        print("\n--- AI Market Summary ---")
        print(summary)
        print("-------------------------")
    except Exception as e:
        print(f"Failed to get summary: {e}")

if __name__ == "__main__":
    test_rag()
