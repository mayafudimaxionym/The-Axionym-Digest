# digest_logic.py

import os
import requests
from bs4 import BeautifulSoup # We will now use BeautifulSoup for styling
from dotenv import load_dotenv
import json
import markdown2
import re

# ... (Configuration section is unchanged) ...
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
SEARCH_QUERY = "digital fraud and cybercrime news"
NUM_RESULTS_TO_FETCH = 10
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
OUTPUT_PROMPT_FILE = "final_prompt_for_ai.txt"

# ... (search_articles and get_article_content functions are unchanged) ...
def search_articles():
    print(f"🔍 Searching for articles with query: '{SEARCH_QUERY}'...")
    if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID: return []
    url = "https://www.googleapis.com/customsearch/v1"
    params = {'key': GOOGLE_API_KEY, 'cx': SEARCH_ENGINE_ID, 'q': SEARCH_QUERY, 'num': NUM_RESULTS_TO_FETCH, 'sort': 'date'}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        search_results = response.json()
        if 'items' not in search_results: return []
        return [{'title': item['title'], 'url': item['link'], 'snippet': item.get('snippet', '')} for item in search_results['items']]
    except requests.exceptions.RequestException as e:
        print(f"❌ A network error occurred: {e}")
        return []

def get_article_content(url):
    try:
        print(f"   - Scraping article: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text_content = "\n".join([p.get_text() for p in paragraphs])
        if not text_content:
            return {"status": "warning", "content": "Could not extract meaningful content."}
        return {"status": "success", "content": text_content}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "content": f"Failed to fetch article: {e}"}

# ... (simulate_ai_digest_generation is also unchanged, it produces structured Markdown) ...
def simulate_ai_digest_generation(prompt_json_str):
    try:
        data = json.loads(prompt_json_str)
        articles = data.get('articles_data', [])
        brief_view_md = "## Weekly Digital Threat Briefing\n\n*A curated summary of this week's most significant cybercrime events, analyzed for industry professionals.*\n\n---\n\n"
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'Untitled')
            teaser = article.get('content', 'No content available.')[:250].replace('\n', ' ')
            if len(teaser) >= 250: teaser += "..."
            image_suggestion = f"Digital illustration representing '{title}' with themes of cybersecurity and data"
            brief_view_md += f"### {title}\n\n"
            brief_view_md += f"![{image_suggestion}](https://via.placeholder.com/300x200.png?text=Illustrative+Image)\n\n" # Placeholder for an actual image
            brief_view_md += f"_{teaser}_\n\n"
            brief_view_md += f"[Read More](#article-{i})\n\n---\n\n"
        full_view_md = "\n\n"
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'Untitled')
            url = article.get('url', '#')
            content = article.get('content', 'No content available.')
            status = article.get('scrape_status', 'unknown')
            full_view_md += f"<a name='article-{i}'></a>\n## {title}\n\n"
            if status == 'error':
                full_view_md += f"**Notice:** Content could not be scraped.\n\n_{content}_\n\n"
            else:
                paragraphs = content.split('\n')
                intro = paragraphs[0] if paragraphs else ""
                body = "\n\n".join(paragraphs[1:4]) if len(paragraphs) > 1 else ""
                pull_quote = paragraphs[2] if len(paragraphs) > 2 else "The impact of this development cannot be overstated."
                full_view_md += f"{intro}\n\n> {pull_quote}\n\n{body}\n\n"
            full_view_md += f"**Original Article:** [{url}]({url})\n\n"
            full_view_md += "#### Key Takeaways & Prevention\n* **Takeaway 1**\n* **Takeaway 2**\n* **Takeaway 3**\n\n"
        return {"status": "success", "markdown_digest": brief_view_md + full_view_md}
    except Exception as e:
        return {"status": "error", "markdown_digest": f"Failed to simulate AI generation: {e}"}

# ==============================================================================
# COMPLETELY REWRITTEN HTML CONVERSION FUNCTION
# ==============================================================================
def convert_markdown_to_tilda_html(markdown_text):
    """
    Converts Markdown to beautifully styled HTML with inline CSS,
    mimicking the axionym.com example, ready for Tilda.
    """
    # 1. Convert base Markdown to HTML
    base_html = markdown2.markdown(markdown_text, extras=["smarty-pants"])

    # 2. Parse the HTML with BeautifulSoup to manipulate and style it
    soup = BeautifulSoup(base_html, 'html.parser')

    # 3. Define the styles based on the example
    # Using a professional, clean sans-serif font stack
    FONT_FAMILY = "'-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif"
    
    # 4. Apply styles to all elements
    for tag in soup.find_all(['h2', 'h3', 'p', 'a', 'em', 'strong', 'li']):
        tag['style'] = f"font-family: {FONT_FAMILY};"

    for h2 in soup.find_all('h2'):
        h2['style'] += "font-size: 32px; font-weight: 600; color: #111111; line-height: 1.2; margin-bottom: 20px;"

    for h3 in soup.find_all('h3'):
        h3['style'] += "font-size: 24px; font-weight: 600; color: #111111; line-height: 1.3; margin-bottom: 15px;"
        
    for p in soup.find_all('p'):
        p['style'] += "font-size: 18px; color: #333333; line-height: 1.6;"

    for strong in soup.find_all('strong'):
        strong['style'] += "font-weight: 600; color: #000000;"

    for li in soup.find_all('li'):
        li['style'] += "font-size: 18px; color: #333333; line-height: 1.6; margin-bottom: 10px;"

    for blockquote in soup.find_all('blockquote'):
        # This creates the distinctive pull-quote style
        blockquote['style'] = "border-left: 3px solid #333333; padding-left: 25px; margin-left: 0; margin-right: 0;"
        quote_p = blockquote.find('p')
        if quote_p:
            quote_p['style'] = f"font-family: {FONT_FAMILY}; font-size: 22px; font-style: italic; color: #111111; line-height: 1.5;"
    
    for a in soup.find_all('a'):
        a['target'] = '_blank' # Open all links in a new tab
        a['style'] += "color: #007bff; text-decoration: none;"
        # Style "Read More" links as buttons
        if a.get_text() == "Read More":
            a['style'] = f"font-family: {FONT_FAMILY}; display: inline-block; padding: 10px 25px; border: 1px solid #333; border-radius: 30px; color: #111; font-size: 16px; font-weight: 500; text-decoration: none;"

    # The entire content can be wrapped in a div for consistent styling in Tilda
    wrapper = soup.new_tag('div')
    wrapper['style'] = "max-width: 800px; margin: 0 auto;"
    
    # Prettify() returns a nicely formatted string
    return soup.prettify()

# ... (generate_final_prompt_from_json is unchanged) ...
def generate_final_prompt_from_json(prompt_json_str):
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
    