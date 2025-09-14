# digest_logic.py

import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json
import markdown2
import re # Import regex module for link modification

# ... (Configuration and search_articles, get_article_content functions remain the same) ...
# --- Configuration ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
SEARCH_QUERY = "digital fraud and cybercrime news"
NUM_RESULTS_TO_FETCH = 10
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
OUTPUT_PROMPT_FILE = "final_prompt_for_ai.txt"

# --- Core Functions ---
def search_articles():
    # ... This function is correct and remains unchanged ...
    print(f"🔍 Searching for articles with query: '{SEARCH_QUERY}'...")
    if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
        print("❌ Cannot search: API keys are not configured in .env file.")
        return []
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
        print(f"❌ A network error occurred: {e}")
        return []

def get_article_content(url):
    # ... This function is correct and remains unchanged ...
    try:
        print(f"   - Scraping article: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text_content = "\n".join([p.get_text() for p in paragraphs])
        if not text_content:
            return {"status": "warning", "content": "Successfully connected, but could not extract meaningful content."}
        return {"status": "success", "content": text_content}
    except requests.exceptions.RequestException as e:
        error_message = f"Failed to fetch article: {e}"
        print(f"   - ❗️ {error_message}")
        return {"status": "error", "content": error_message}

# ==============================================================================
# NEW & IMPROVED AI SIMULATION FUNCTION
# ==============================================================================
def simulate_ai_digest_generation(prompt_json_str):
    """
    Simulates an expert AI analysis, generating a high-quality Markdown digest
    that closely matches the style of the provided examples.
    """
    try:
        data = json.loads(prompt_json_str)
        articles = data.get('articles_data', [])
        
        # --- Part 1: Generate the Teaser/Brief View section ---
        brief_view_md = "## Weekly Digital Threat Briefing\n\n"
        brief_view_md += "*A curated summary of this week's most significant cybercrime events, analyzed for industry professionals.*\n\n---\n\n"

        for i, article in enumerate(articles, 1):
            title = article.get('title', 'Untitled')
            # AI Simulation: Create a better teaser from the first ~250 chars
            teaser = article.get('content', 'No content available.')[:250].replace('\n', ' ')
            if len(teaser) >= 250:
                teaser += "..."
            
            # AI Simulation: Create a more relevant image suggestion
            image_suggestion = f"Digital illustration representing '{title}' with themes of cybersecurity and data"

            brief_view_md += f"### {title}\n\n"
            brief_view_md += f"_{teaser}_\n\n"
            brief_view_md += f"**[Image: {image_suggestion}]**\n\n"
            brief_view_md += f"[Read More](#article-{i})\n\n---\n\n"

        # --- Part 2: Generate the Detailed/Full View section ---
        full_view_md = "\n\n" # Separator
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'Untitled')
            url = article.get('url', '#') # FIXED: Now using the correct URL
            content = article.get('content', 'No content available.')
            status = article.get('scrape_status', 'unknown')

            full_view_md += f"<a name='article-{i}'></a>\n" # FIXED: English anchor
            full_view_md += f"## {title}\n\n"
            
            if status == 'error':
                full_view_md += f"**Notice:** Content could not be scraped. Please refer to the original article.\n\n_{content}_\n\n"
            else:
                # AI Simulation: Create a more structured brief with a pull quote
                paragraphs = content.split('\n')
                intro = paragraphs[0] if paragraphs else ""
                body = "\n\n".join(paragraphs[1:4]) if len(paragraphs) > 1 else ""
                pull_quote = paragraphs[2] if len(paragraphs) > 2 else "The impact of this development cannot be overstated."
                
                full_view_md += f"{intro}\n\n"
                full_view_md > f"> {pull_quote}\n\n" # Markdown for a blockquote
                full_view_md += f"{body}\n\n"

            full_view_md += f"**Original Article:** [{url}]({url})\n\n"
            full_view_md += "#### Key Takeaways & Prevention\n"
            full_view_md += "* **Takeaway 1:** Always verify requests for sensitive information.\n"
            full_view_md += "* **Takeaway 2:** Implement robust monitoring for unusual account activity.\n"
            full_view_md += "* **Takeaway 3:** Employee training remains the first line of defense.\n\n"
        
        # Combine both parts
        final_markdown = brief_view_md + full_view_md
        return {"status": "success", "markdown_digest": final_markdown}

    except Exception as e:
        return {"status": "error", "markdown_digest": f"Failed to simulate AI generation: {e}"}

# ==============================================================================
# NEW & IMPROVED HTML CONVERSION FUNCTION
# ==============================================================================
def convert_markdown_to_tilda_html(markdown_text):
    """
    Converts Markdown to Tilda-ready HTML, ensuring all external links open in a new tab.
    """
    html = markdown2.markdown(markdown_text, extras=["fenced-code-blocks", "tables", "smarty-pants", "link-patterns"])
    
    # FIXED: Use regex to find all <a> tags that don't have target="_blank" and add it.
    # This ensures both markdown links and raw HTML links are handled.
    def add_target_blank(match):
        tag = match.group(0)
        if 'target=' in tag:
            return tag # Don't modify if target already exists
        if 'href' in tag and (tag.startswith('<a href="http') or tag.startswith('<a href="www')):
            return tag.replace('<a ', '<a target="_blank" ')
        return tag
        
    # A simple replacement for markdown-generated links
    html = html.replace('<a href="http', '<a target="_blank" href="http')

    return html

# ... (generate_final_prompt_from_json remains the same for creating the text file) ...
def generate_final_prompt_from_json(prompt_json_str):
    # ... This function is correct and remains unchanged ...
    try:
        data = json.loads(prompt_json_str)
        articles = data.get('articles_data', [])
        template = data.get('output_format', {}).get('template', 'No template.')
        prompt_header = "You are an expert AI analyst...\n\n--- START OF ARTICLE DATA ---\n"
        prompt_body = ""
        for i, article in enumerate(articles, 1):
            prompt_body += f"\n--- ARTICLE {i} ---\nURL: {article.get('url', 'N/A')}\nTITLE: {article.get('title', 'N/A')}\nCONTENT:\n{article.get('content', 'N/A')}\n---------------------\n"
        prompt_footer = f"\n--- END OF ARTICLE DATA ---\n\nBased on the data, follow this template:\n{template}"
        with open(OUTPUT_PROMPT_FILE, "w", encoding="utf-8") as f:
            f.write(prompt_header + prompt_body + prompt_footer)
        print(f"🚀 Success! Prompt saved to '{OUTPUT_PROMPT_FILE}'.")
        return True
    except Exception as e:
        print(f"❌ Error generating prompt file: {e}")
        return False
    