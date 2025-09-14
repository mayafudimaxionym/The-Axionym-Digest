# app.py

from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import digest_logic as dl

app = Flask(__name__)
app.secret_key = 'a_very_secret_key_for_the_axionym_digest'
workflow_state = {}

def get_default_prompts():
    # ... This function is correct and remains unchanged ...
    prompts = {
        "step1": json.dumps({ "task": "find_articles", "query": "latest digital fraud and cybercrime news", "parameters": { "timeframe": "last_7_days", "num_articles": 10, "sort_by": "relevance" } }, indent=2),
        "step2": json.dumps({ "task": "select_best_articles", "selection_count": 5, "criteria": { "prioritize": ["new threats", "major financial impact"], "avoid": ["reposts"] } }, indent=2),
        "step3": json.dumps({ "task": "generate_digest_content", "articles_data": "PLACEHOLDER", "output_format": { "style": "analytical", "template": "## Weekly Digital Threat Briefing...", "include": ["summary", "teaser", "briefing"] } }, indent=2)
    }
    return prompts

def initialize_workflow():
    # ... This function is correct and remains unchanged ...
    global workflow_state
    workflow_state = { "step": 1, "prompts": get_default_prompts(), "results": {} }

@app.route('/')
def index():
    # ... This function is correct and remains unchanged ...
    if 'step' not in workflow_state:
        initialize_workflow()
    debug_state = json.dumps(workflow_state, indent=2, ensure_ascii=False)
    return render_template('index.html', debug_state=debug_state, **workflow_state)

# NEW: Route to save or reset a prompt without running a step
@app.route('/update_prompt', methods=['POST'])
def update_prompt():
    global workflow_state
    data = request.get_json()
    step_key = data.get('step_key') # e.g., 'step1'
    action = data.get('action') # 'save' or 'reset'
    
    if action == 'save':
        new_prompt = data.get('prompt_text')
        workflow_state['prompts'][step_key] = new_prompt
        return jsonify(success=True, message=f"Prompt for {step_key} saved.")
    elif action == 'reset':
        default_prompts = get_default_prompts()
        workflow_state['prompts'][step_key] = default_prompts[step_key]
        return jsonify(success=True, message=f"Prompt for {step_key} reset to default.", new_prompt=default_prompts[step_key])
    
    return jsonify(success=False, message="Invalid action.")

# ... (run_step1, run_step2, run_step3, run_step4 are unchanged from the previous correct version) ...
@app.route('/run_step1', methods=['POST'])
def run_step1():
    # ... This function is correct and remains unchanged ...
    global workflow_state
    prompt_str = request.form.get('prompt_step1')
    try:
        prompt_json = json.loads(prompt_str)
        workflow_state['prompts']['step1'] = prompt_str
    except json.JSONDecodeError:
        return redirect(url_for('index'))
    query = prompt_json.get("query", "cybercrime news")
    dl.SEARCH_QUERY = query
    found_articles = dl.search_articles()
    if not found_articles:
        return redirect(url_for('index'))
    workflow_state['step'] = 2
    workflow_state['results'] = { 'step1': found_articles }
    workflow_state['message'] = f"Step 1 Completed: Found {len(found_articles)} articles."
    workflow_state['message_type'] = "success"
    return redirect(url_for('index'))

@app.route('/run_step2', methods=['POST'])
def run_step2():
    # ... This function is correct and remains unchanged ...
    global workflow_state
    workflow_state['prompts']['step2'] = request.form.get('prompt_step2')
    selected_indices_str = request.form.getlist('selected_articles_indices')
    if len(selected_indices_str) != 5:
        return redirect(url_for('index'))
    all_articles = workflow_state['results']['step1']
    selected_articles = [all_articles[int(i)] for i in selected_indices_str]
    workflow_state['results']['step2'] = selected_articles
    scraped_articles_data, scrape_error_count = [], 0
    for article in selected_articles:
        scrape_result = dl.get_article_content(article['url'])
        scraped_articles_data.append({'title': article['title'], 'url': article['url'], 'scrape_status': scrape_result['status'], 'content': scrape_result['content']})
        if scrape_result['status'] == 'error':
            scrape_error_count += 1
    prompt_step3_template = json.loads(get_default_prompts()['step3'])
    prompt_step3_template['articles_data'] = scraped_articles_data
    workflow_state['prompts']['step3'] = json.dumps(prompt_step3_template, indent=2)
    workflow_state['step'] = 3
    workflow_state['message'] = f"Step 2 Completed. Scraped 5 articles with {scrape_error_count} errors."
    workflow_state['message_type'] = "success" if scrape_error_count == 0 else "error"
    return redirect(url_for('index'))

@app.route('/run_step3', methods=['POST'])
def run_step3():
    # ... This function is correct and remains unchanged ...
    global workflow_state
    user_edited_prompt_str = request.form.get('prompt_step3')
    workflow_state['prompts']['step3'] = user_edited_prompt_str
    ai_result = dl.simulate_ai_digest_generation(user_edited_prompt_str)
    if ai_result['status'] == 'success':
        workflow_state['results']['step4_markdown'] = ai_result['markdown_digest']
        workflow_state['step'] = 4
        workflow_state['message'] = "Step 3 Completed: AI digest simulated."
        workflow_state['message_type'] = "success"
    else:
        workflow_state['message'] = f"Step 3 Failed: {ai_result['markdown_digest']}"
        workflow_state['message_type'] = "error"
    return redirect(url_for('index'))

@app.route('/run_step4', methods=['POST'])
def run_step4():
    # ... This function is correct and remains unchanged ...
    global workflow_state
    final_markdown = request.form.get('final_markdown_digest')
    workflow_state['results']['step4_markdown'] = final_markdown
    tilda_html = dl.convert_markdown_to_tilda_html(final_markdown)
    workflow_state['results']['step4_tilda_html'] = tilda_html
    workflow_state['message'] = "Step 4 Completed: Tilda HTML generated."
    workflow_state['message_type'] = "success"
    return redirect(url_for('index'))


if __name__ == '__main__':
    initialize_workflow()
    app.run(debug=True, port=5001)
    