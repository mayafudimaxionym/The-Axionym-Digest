# app.py

from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import digest_logic as dl

app = Flask(__name__)
# A secret key is required to use sessions
app.secret_key = 'a_very_secret_key_for_the_axionym_digest_sessions'

# We no longer need a global variable, we will use the session object
# workflow_state = {}

def get_default_prompts():
    # ... This function remains the same ...
    prompts = { "step1": json.dumps({ "task": "find_articles", "query": "latest digital fraud and cybercrime news", "parameters": { "timeframe": "last_7_days", "num_articles": 10, "sort_by": "relevance" } }, indent=2), "step2": json.dumps({ "task": "select_best_articles", "selection_count": 5, "criteria": { "prioritize": ["new threats", "major financial impact"], "avoid": ["reposts"] } }, indent=2), "step3": json.dumps({ "task": "generate_analytical_note", "articles_data": "PLACEHOLDER", "output_format": { "title": "Beyond the Breach: Why Digital Fraud Flies Under the Radar", "style": "analytical_review", "include": ["synthesized_intro", "detailed_analysis_with_quotes", "key_takeaways", "source_links_list"] } }, indent=2) }
    return prompts

def initialize_workflow():
    """Resets the workflow in the user's session."""
    session['workflow'] = { "step": 1, "prompts": get_default_prompts(), "results": {} }
    session.modified = True

@app.route('/')
def index():
    """Displays the main workflow page using session data."""
    if 'workflow' not in session:
        initialize_workflow()
    
    debug_state = json.dumps(session.get('workflow', {}), indent=2, ensure_ascii=False)
    return render_template('index.html', debug_state=debug_state, **session['workflow'])

@app.route('/update_prompt', methods=['POST'])
def update_prompt():
    # ... This function remains the same, but now modifies the session ...
    data = request.get_json()
    step_key, action = data.get('step_key'), data.get('action')
    if action == 'save':
        session['workflow']['prompts'][step_key] = data.get('prompt_text')
        session.modified = True
        return jsonify(success=True, message=f"Prompt for {step_key} saved for this session.")
    elif action == 'reset':
        default_prompts = get_default_prompts()
        session['workflow']['prompts'][step_key] = default_prompts[step_key]
        session.modified = True
        return jsonify(success=True, message=f"Prompt for {step_key} reset.", new_prompt=default_prompts[step_key])
    return jsonify(success=False, message="Invalid action.")


@app.route('/run_step1', methods=['POST'])
def run_step1():
    """Executes Step 1, now respecting the edited prompt."""
    prompt_str = request.form.get('prompt_step1')
    try:
        prompt_json = json.loads(prompt_str)
        session['workflow']['prompts']['step1'] = prompt_str # Save user's edits
    except json.JSONDecodeError:
        return redirect(url_for('index'))

    # FIXED: Actually use the parameters from the edited prompt
    query = prompt_json.get("query", "cybercrime news")
    params = prompt_json.get("parameters", {})
    num_to_fetch = params.get("num_articles", 10) # <-- USING THE EDITED VALUE

    # Pass the number of articles to the search function
    found_articles = dl.search_articles(query, num_to_fetch)
    
    if not found_articles:
        session['workflow']['message'] = f"Step 1 Failed: Could not find any articles for '{query}'."
        session['workflow']['message_type'] = "error"
        return redirect(url_for('index'))

    session['workflow']['step'] = 2
    session['workflow']['results'] = { 'step1': found_articles }
    session['workflow']['message'] = f"Step 1 Completed: Found {len(found_articles)} articles."
    session['workflow']['message_type'] = "success"
    session.modified = True
    return redirect(url_for('index'))

@app.route('/run_step2', methods=['POST'])
def run_step2():
    # ... This function is mostly the same, just using sessions ...
    session['workflow']['prompts']['step2'] = request.form.get('prompt_step2')
    selected_indices_str = request.form.getlist('selected_articles_indices')
    if len(selected_indices_str) != 5: return redirect(url_for('index'))

    all_articles = session['workflow']['results']['step1']
    selected_articles = [all_articles[int(i)] for i in selected_indices_str]
    session['workflow']['results']['step2'] = selected_articles
    
    scraped_articles_data, scrape_error_count = [], 0
    for article in selected_articles:
        scrape_result = dl.get_article_content(article['url'])
        scraped_articles_data.append({'title': article['title'], 'url': article['url'], 'scrape_status': scrape_result['status'], 'content': scrape_result['content']})
        if scrape_result['status'] == 'error': scrape_error_count += 1
        
    prompt_step3_template = json.loads(get_default_prompts()['step3'])
    prompt_step3_template['articles_data'] = scraped_articles_data
    session['workflow']['prompts']['step3'] = json.dumps(prompt_step3_template, indent=2)
    session['workflow']['step'] = 3
    session['workflow']['message'] = f"Step 2 Completed. Scraped 5 articles with {scrape_error_count} errors."
    session['workflow']['message_type'] = "success" if scrape_error_count == 0 else "error"
    session.modified = True
    return redirect(url_for('index'))

@app.route('/run_step3', methods=['POST'])
def run_step3():
    # ... This function is mostly the same, just using sessions ...
    user_edited_prompt_str = request.form.get('prompt_step3')
    session['workflow']['prompts']['step3'] = user_edited_prompt_str
    ai_result = dl.simulate_ai_digest_generation(user_edited_prompt_str)
    if ai_result['status'] == 'success':
        session['workflow']['results']['step4_markdown'] = ai_result['markdown_digest']
        session['workflow']['step'] = 4
        session['workflow']['message'], session['workflow']['message_type'] = "Step 3 Completed: Analytical Note simulated.", "success"
    else:
        session['workflow']['message'], session['workflow']['message_type'] = f"Step 3 Failed: {ai_result['markdown_digest']}", "error"
    session.modified = True
    return redirect(url_for('index'))

@app.route('/run_step4', methods=['POST'])
def run_step4():
    # ... This function is mostly the same, just using sessions ...
    final_markdown = request.form.get('final_markdown_digest')
    session['workflow']['results']['step4_markdown'] = final_markdown
    tilda_html = dl.convert_markdown_to_tilda_html(final_markdown)
    session['workflow']['results']['step4_tilda_html'] = tilda_html
    session['workflow']['message'], session['workflow']['message_type'] = "Step 4 Completed: Tilda HTML generated.", "success"
    session.modified = True
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
    