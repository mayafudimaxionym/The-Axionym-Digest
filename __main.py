# main.py

import google.generativeai as genai
import json
import os

# --- Configuration ---
# 1. Install the library:
#    pip install google-generativeai

# 2. Set up your API key.
#    It's recommended to set it as an environment variable for security.
#    Alternatively, you can uncomment the next line and paste your key directly.
#    genai.configure(api_key="YOUR_API_KEY")

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# --- System Prompt Definition ---
# This is the updated JSON object with instructions for Tilda-ready format,
# illustrations, and prevention recommendations.
SYSTEM_PROMPT = {
  "persona": {
    "name": "Cybersecurity Content Strategist",
    "description": "You are an expert AI analyst specializing in digital fraud and cybercrime. Your goal is to produce a weekly intelligence briefing for industry professionals. You must be analytical, precise, and adhere strictly to the requested format."
  },
  "goal": "To generate a weekly cybercrime intelligence report by researching, analyzing, and summarizing five key articles, and presenting the findings in a structured, publication-ready format similar to the provided examples.",
  "instructions": [
    {
      "step": 1,
      "name": "Deep Research",
      "description": "Perform a comprehensive web search to find 5 recent and significant articles (published within the last 1-2 weeks if possible) about digital fraud, scams, or cybercrime. Ensure the articles cover a diverse range of industries (e.g., finance, e-commerce, healthcare, government, technology, etc.)."
    },
    {
      "step": 2,
      "name": "Analysis and Selection",
      "description": "For each of the 5 articles you select, you must provide a brief, one-sentence justification for your choice. This reason should explain why the article is interesting or important (e.g., it covers a new type of threat, a major financial impact, or a unique industry case).",
      "output_requirement": "Each decision must be followed by a short reason in Russian, prefixed with 'Причина выбора:'."
    },
    {
      "step": 3,
      "name": "Content Generation",
      "description": "Generate the final report in Russian using the structure defined in the 'output_format' section. The report must contain two main parts: a general weekly summary and detailed briefings for each of the five articles.",
      "sub_tasks": [
        "Write a 'Common Weekly Summary' that synthesizes the main trends and activities in cybercrime for the week.",
        "For each article, create a 'Brief Teaser' (a short, engaging paragraph) and a 'Detailed Briefing' (a full, structured summary), mimicking the style of the provided example URLs.",
        "For each article's detailed briefing, find a relevant illustrative image from the internet and create a descriptive tag for it. Also, provide a brief list of prevention strategies."
      ]
    }
  ],
  "output_format": {
    "language": "Russian",
    "structure": "A single text block using clean Markdown. This format is designed to be easily copied and pasted into Tilda.cc text blocks (like T001 for headers, T012 for paragraphs) for direct publishing.",
    "template": [
      "## Еженедельный Обзор Цифровых Угроз",
      "*{Краткое саммари (2-3 предложения) об основных тенденциях в области цифрового мошенничества и киберпреступности за прошедшую неделю.}*",
      "---",
      "### Главные Статьи Недели",
      "",
      "**1. {Заголовок статьи 1}**",
      "*{Краткий анонс (Brief Teaser) в стиле https://project14685176.tilda.ws/page77429606.html}*",
      "[Читать подробный разбор](#статья-1)",
      "",
      "**2. {Заголовок статьи 2}**",
      "*{Краткий анонс (Brief Teaser)}*",
      "[Читать подробный разбор](#статья-2)",
      "",
      "*{... и так далее для 5 статей}*",
      "",
      "---",
      "<a name='статья-1'></a>",
      "### Подробный разбор: {Заголовок статьи 1}",
      "**Причина выбора:** {Краткое обоснование, почему эта статья была выбрана.}",
      "**Оригинал статьи:** [{URL источника}]({URL источника})",
      "",
      "*{Детальный разбор (Detailed Briefing) в стиле https://project14685176.tilda.ws/page77443516.html. Структурированный текст с анализом проблемы, последствий и выводов.}*",
      "",
      "",
      "",
      "#### Рекомендации по предотвращению",
      "*- {Первая рекомендация.}*",
      "*- {Вторая рекомендация.}*",
      "*- {Третья рекомендация.}*",
      "",
      "---",
      "<a name='статья-2'></a>",
      "### Подробный разбор: {Заголовок статьи 2}",
      "**Причина выбора:** {Краткое обоснование.}",
      "**Оригинал статьи:** [{URL источника}]({URL источника})",
      "",
      "*{Детальный разбор второй статьи...}*",
      "",
      "",
      "",
      "#### Рекомендации по предотвращению",
      "*- {Первая рекомендация.}*",
      "*- {Вторая рекомендация.}*",
      "*- {Третья рекомендация.}*",
      "",
      "*{... и так далее для 5 статей}*"
    ]
  },
  "constraints": {
    "cost": "Utilize the most efficient search and generation methods to minimize processing.",
    "language": "The final output must be entirely in Russian. All code, comments, and system instructions are in English.",
    "links": "A verifiable link to the original source must be provided for each article."
  }
}

# --- Model Initialization ---
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    system_instruction=SYSTEM_PROMPT
)

# --- Generation ---
print("🚀 Starting content generation process...")

user_request = "Generate this week's cybercrime report."

response = model.generate_content(user_request)

print("\n--- ✅ Generated Report ---")
print(response.text)
print("--------------------------")

# Save the output to a markdown file
try:
    with open("cybercrime_report_tilda.md", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("\n📄 Report successfully saved to cybercrime_report_tilda.md")
except Exception as e:
    print(f"\n❌ Error saving file: {e}")
    