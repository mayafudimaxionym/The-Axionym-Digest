# digest_logic.py

import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json

# --- Configuration ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
SEARCH_QUERY = "digital fraud and cybercrime news"
NUM_RESULTS_TO_FETCH = 10
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
OUTPUT_PROMPT_FILE = "final_prompt_for_ai.txt"

def search_articles():
    """Searches Google for recent articles based on the query."""
    print(f"🔍 Searching for articles with query: '{SEARCH_QUERY}'...")
    url = "https://www.googleapis.com/customsearch/v1"
    params = {'key': GOOGLE_API_KEY, 'cx': SEARCH_ENGINE_ID, 'q': SEARCH_QUERY, 'num': NUM_RESULTS_TO_FETCH, 'sort': 'date'}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        search_results = response.json()
        if 'items' not in search_results:
            print("❌ Error: No articles found. Check API key/search engine ID.")
            return []
        articles = [{'title': item['title'], 'url': item['link'], 'snippet': item.get('snippet', '')} for item in search_results['items']]
        print(f"✅ Found {len(articles)} potential articles.")
        return articles
    except requests.exceptions.RequestException as e:
        print(f"❌ HTTP Request failed: {e}")
        return []

def get_article_content(url):
    """Scrapes the main text content from a given article URL."""
    try:
        print(f"   - Reading article: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text_content = "\n".join([p.get_text() for p in paragraphs])
        return text_content if text_content else "Could not extract content."
    except requests.exceptions.RequestException as e:
        print(f"   - ❗️ Failed to fetch article: {e}")
        return "Failed to fetch article content."

def generate_final_prompt(articles_data):
    """Generates a structured prompt for the AI based on the scraped content."""
    prompt_header = "You are an expert AI analyst... (rest of your detailed prompt)" # Truncated for brevity
    prompt_body = ""
    for i, article in enumerate(articles_data, 1):
        prompt_body += f"\n--- ARTICLE {i} ---\nURL: {article['url']}\nTITLE: {article['title']}\nCONTENT:\n{article['content']}\n"
    prompt_footer = "--- END OF ARTICLE DATA --- (rest of your detailed template)" # Truncated for brevity
    
    final_prompt = prompt_header + prompt_body + prompt_footer
    with open(OUTPUT_PROMPT_FILE, "w", encoding="utf-8") as f:
        f.write(final_prompt)
    print(f"\n🚀 Success! The final prompt has been saved to '{OUTPUT_PROMPT_FILE}'.")
    