# digest_logic.py

import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json
import markdown2
import re

# ... (Configuration is unchanged) ...
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
HEADERS = {'User-Agent': 'Mozilla/5.0 ...'} # a long user agent string

# --- Core Functions ---
def search_articles(query, num_to_fetch=10): # MODIFIED: Accepts query and number
    """Searches Google for recent articles."""
    print(f"🔍 Searching for {num_to_fetch} articles with query: '{query}'...")
    if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID: return []
    url = "https://www.googleapis.com/customsearch/v1"
    params = {'key': GOOGLE_API_KEY, 'cx': SEARCH_ENGINE_ID, 'q': query, 'num': num_to_fetch, 'sort': 'date'}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        search_results = response.json()
        if 'items' not in search_results: return []
        return [{'title': item['title'], 'url': item['link'], 'snippet': item.get('snippet', '')} for item in search_results['items']]
    except requests.exceptions.RequestException as e:
        print(f"❌ A network error occurred: {e}")
        return []

# NEW: Function to search for an image
def find_image_url(query):
    """Searches for a single, relevant image URL."""
    print(f"🖼️ Searching for image with query: '{query}'...")
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {'key': GOOGLE_API_KEY, 'cx': SEARCH_ENGINE_ID, 'q': query, 'num': 1, 'searchType': 'image', 'imgSize': 'large'}
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()
        if 'items' in results and len(results['items']) > 0:
            return results['items'][0]['link']
    except Exception as e:
        print(f"   - ❗️ Image search failed: {e}")
    return "https://via.placeholder.com/600x400.png?text=Image+Not+Found" # Fallback

# ... (get_article_content is unchanged) ...
def get_article_content(url):
    try:
        print(f"   - Scraping article: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text_content = "\n".join([p.get_text() for p in paragraphs])
        if not text_content: return {"status": "warning", "content": "Could not extract meaningful content."}
        return {"status": "success", "content": text_content}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "content": f"Failed to fetch article: {e}"}

# ==============================================================================
# COMPLETELY REWRITTEN AI SIMULATION FOR ANALYTICAL NOTE
# ==============================================================================
def simulate_ai_digest_generation(prompt_json_str):
    """
    Simulates an expert AI analysis, generating a high-quality ANALYTICAL NOTE
    in Markdown, including real images and a final source list.
    """
    try:
        data = json.loads(prompt_json_str)
        articles = data.get('articles_data', [])
        output_format = data.get('output_format', {})
        note_title = output_format.get('title', "Weekly Threat Analysis")
        
        # --- Synthesize the intro from all articles ---
        intro_paragraph = "The news is full of headlines about major cyberattacks... But another, equally damaging threat operates quietly in the background: digital fraud. "
        intro_paragraph += f"This week, several key incidents, including {articles[0]['title']} and {articles[1]['title']}, highlight why this issue rarely makes the front page, even as it costs businesses and individuals billions."
        
        # Start building the Markdown
        final_md = f"# {note_title}\n\n"
        final_md += f"![Main illustration for the analytical note]( {find_image_url(note_title)} )\n\n" # Main image
        final_md += f"{intro_paragraph}\n\n"

        # --- Create detailed analysis for each article ---
        for article in articles:
            title = article.get('title', 'Untitled')
            content = article.get('content', 'No content available.')
            
            final_md += f"### {title}\n\n"
            if article['scrape_status'] == 'error':
                final_md += f"_{content}_\n\n"
            else:
                paragraphs = content.split('\n')
                body = "\n\n".join(paragraphs[:2]) if len(paragraphs) > 1 else content
                pull_quote = paragraphs[2] if len(paragraphs) > 2 else "This represents a continuous financial drain on businesses, affecting everything from operational overhead to brand reputation."
                final_md += f"{body}\n\n> {pull_quote}\n\n"
        
        # --- Add a final list of source links ---
        final_md += "---\n\n"
        final_md += "### Source Articles\n\n"
        for article in articles:
            final_md += f"* [{article['title']}]({article['url']})\n"

        return {"status": "success", "markdown_digest": final_md}

    except Exception as e:
        return {"status": "error", "markdown_digest": f"Failed to simulate AI generation: {e}"}

# ... (convert_markdown_to_tilda_html and generate_final_prompt_from_json are unchanged) ...
def convert_markdown_to_tilda_html(markdown_text):
    html = markdown2.markdown(markdown_text, extras=["smarty-pants"])
    soup = BeautifulSoup(html, 'html.parser')
    FONT_FAMILY = "'-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif"
    for tag in soup.find_all(['h1', 'h3', 'p', 'a', 'em', 'strong', 'li']): tag['style'] = f"font-family: {FONT_FAMILY};"
    for h1 in soup.find_all('h1'): h1['style'] += "font-size: 42px; font-weight: 700; color: #111; line-height: 1.2;"
    for h3 in soup.find_all('h3'): h3['style'] += "font-size: 24px; font-weight: 600; color: #111; line-height: 1.3;"
    for p in soup.find_all('p'): p['style'] += "font-size: 18px; color: #333; line-height: 1.6;"
    for img in soup.find_all('img'): img['style'] = "max-width: 100%; height: auto; border-radius: 8px; margin-bottom: 20px;"
    for blockquote in soup.find_all('blockquote'):
        blockquote['style'] = "border-left: 3px solid #333; padding-left: 25px; margin: 20px 0;"
        if p_tag := blockquote.find('p'): p_tag['style'] = f"font-family: {FONT_FAMILY}; font-size: 22px; font-style: italic; color: #111;"
    for a in soup.find_all('a'):
        a['target'] = '_blank'
        a['style'] += "color: #007bff; text-decoration: none;"
    return soup.prettify()

def generate_final_prompt_from_json(prompt_json_str):
    # This function is now less critical but kept for completeness
    try:
        data = json.loads(prompt_json_str)
        # ... rest of the function ...
        return True
    except Exception:
        return False
    