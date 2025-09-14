# app.py

from flask import Flask, render_template, request
from markupsafe import Markup # Correct import for Markup
import markdown
import digest_logic as dl

app = Flask(__name__)

# A global variable to temporarily store the found articles.
# In a real-world application, using user sessions would be better,
# but for a local-only tool, this is acceptable.
found_articles = []

@app.route('/')
def index():
    """Renders the main page."""
    return render_template('index.html')

@app.route('/search-articles', methods=['POST'])
def search_articles_route():
    """
    Searches for articles and displays them on the same page for selection.
    """
    global found_articles
    print("\n--- [SERVER LOG] Received request to search for articles ---")
    
    found_articles = dl.search_articles()
    
    if not found_articles:
        return render_template('index.html', message="Error: Could not find any articles. Check terminal logs.")

    # Pass the found articles to the template for rendering the selection form
    return render_template('index.html', articles_to_select=found_articles)

@app.route('/generate-prompt', methods=['POST'])
def generate_prompt_route():
    """
    Processes the user's selection, scrapes the content, and generates the prompt file.
    """
    global found_articles
    print("\n--- [SERVER LOG] Received request to generate prompt from selection ---")

    # Get the indices of the selected checkboxes from the form
    selected_indices = request.form.getlist('selected_articles')
    
    if len(selected_indices) != 5:
        message = f"Error: Please select exactly 5 articles. You selected {len(selected_indices)}."
        # Pass the original list back so the user can correct their selection
        return render_template('index.html', articles_to_select=found_articles, message=message)

    # Build the list of selected articles from the form data
    selected_articles_data = []
    for index_str in selected_indices:
        index = int(index_str)
        # Get the article data from the hidden form fields
        title = request.form.get(f'article_title_{index}')
        url = request.form.get(f'article_url_{index}')
        selected_articles_data.append({'title': title, 'url': url})
        
    print(f"✅ User selected {len(selected_articles_data)} articles. Fetching content...")

    # Scrape content for the selected articles and generate the final prompt file
    final_articles_data = []
    for article in selected_articles_data:
        content = dl.get_article_content(article['url'])
        final_articles_data.append({'title': article['title'], 'url': article['url'], 'content': content})
    
    dl.generate_final_prompt(final_articles_data)
    
    message = f"Success! The prompt file '{dl.OUTPUT_PROMPT_FILE}' has been generated. You can now proceed to Step 3."
    # Clear the global variable and return to the main page with a success message
    found_articles = [] 
    return render_template('index.html', message=message)


@app.route('/render', methods=['POST'])
def render_digest():
    """Renders the Markdown from the form textarea into HTML."""
    md_text = request.form.get('digest_markdown', '')
    # Convert Markdown to HTML, enabling the 'extra' extension for features like tables
    html_content = markdown.markdown(md_text, extensions=['extra', 'fenced_code'])
    return render_template('index.html', content=Markup(html_content))


if __name__ == '__main__':
    app.run(debug=True, port=5001)
    