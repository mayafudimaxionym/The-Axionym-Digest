# app.py

from flask import Flask, render_template, request, Markup
import markdown
import digest_logic as dl

app = Flask(__name__)

@app.route('/')
def index():
    """Renders the main page."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_prompt():
    """Triggers the article searching and selection process."""
    print("\n--- [SERVER LOG] Received request to generate prompt ---")
    
    # 1. Search for articles
    articles = dl.search_articles()
    if not articles:
        return render_template('index.html', message="Error: Could not find any articles. Check terminal for details.")

    # 2. Interactive selection in the terminal
    print("\n--- [ACTION REQUIRED] Please Select 5 Articles in the Terminal ---")
    for i, article in enumerate(articles):
        print(f"[{i+1}] {article['title']}\n    Snippet: {article['snippet']}\n")
    
    selected_indices = []
    while len(selected_indices) < 5:
        try:
            choice = input(f"Enter the number of your choice ({5 - len(selected_indices)} remaining): ")
            index = int(choice) - 1
            if 0 <= index < len(articles) and index not in selected_indices:
                selected_indices.append(index)
            else:
                print("Invalid number or already selected. Please try again.")
        except (ValueError, IndexError):
            print("Invalid input. Please enter a valid number from the list.")
            
    selected_articles = [articles[i] for i in selected_indices]
    print("\n✅ You have selected 5 articles. Fetching full content...")

    # 3. Scrape content and generate the prompt file
    final_articles_data = []
    for article in selected_articles:
        content = dl.get_article_content(article['url'])
        final_articles_data.append({'title': article['title'], 'url': article['url'], 'content': content})
    
    dl.generate_final_prompt(final_articles_data)
    
    message = f"Success! Prompt file '{dl.OUTPUT_PROMPT_FILE}' has been generated. Please continue to Step 2."
    return render_template('index.html', message=message)


@app.route('/render', methods=['POST'])
def render_digest():
    """Renders the Markdown from the form into HTML."""
    md_text = request.form.get('digest_markdown', '')
    # Convert Markdown to HTML, enabling the 'extra' extension for features like tables
    html_content = markdown.markdown(md_text, extensions=['extra', 'fenced_code'])
    return render_template('index.html', content=Markup(html_content))


if __name__ == '__main__':
    app.run(debug=True, port=5001)
    