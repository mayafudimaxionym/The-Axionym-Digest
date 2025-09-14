# The Axionym Digest

This project generates a weekly cybercrime intelligence report using the Gemini API. The report is formatted in Markdown for easy publishing on Tilda.cc.

## How it Works

The `main.py` script uses the Gemini API to generate a weekly report on digital fraud and cybercrime. The script is guided by a detailed system prompt.

The system prompt instructs the AI to:
1.  Research and select 5 recent articles on cybercrime.
2.  Analyze and justify the selection of each article.
3.  Generate a report in Russian, including a weekly summary, article teasers, and detailed briefings.
4.  The output is a single Markdown file (`cybercrime_report_tilda.md`) ready for use with Tilda.cc.

## How to Use

1.  **Install dependencies:**
    ```bash
    pip install google-generativeai
    ```

2.  **Set up your API key:**
    Set the `GEMINI_API_KEY` environment variable to your Gemini API key.

3.  **Run the script:**
    ```bash
    python main.py
    ```

4.  **Output:**
    The generated report will be saved as `cybercrime_report_tilda.md`.

## Configuration

The behavior of the AI is controlled by the system prompt within `main.py`. You can modify this to change the persona, goals, instructions, and output format of the generated report.
