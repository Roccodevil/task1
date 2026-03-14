import sys
import os
import re
import ssl
import gc
import shutil
import uuid

# Force Python to add your project root to its path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ['CREWAI_DISABLE_TELEMETRY'] = 'true'
os.environ['OTEL_SDK_DISABLED'] = 'true'

os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
ssl._create_default_https_context = ssl._create_unverified_context

from dotenv import load_dotenv
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from agents.crew_orchestrator import run_explainer_crew

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def format_explanation(text):
    if not text:
        return ""

    text = str(text)

    # Normalize line endings and strip markdown code fences.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"```(?:\w+)?\n?", "", text)
    text = text.replace("```", "")

    blocks = re.split(r"\n\s*\n+", text.strip())
    html_parts = []

    for block in blocks:
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        if not lines:
            continue

        # Markdown separator lines are visual noise for this UI.
        if len(lines) == 1 and re.fullmatch(r"-{2,}", lines[0]):
            continue

        if all(line.startswith("- ") or line.startswith("* ") for line in lines):
            items = [re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line[2:].strip()) for line in lines]
            html_parts.append("<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>")
            continue

        if all(re.match(r"\d+\.\s+", line) for line in lines):
            items = [re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", re.sub(r"\d+\.\s*", "", line)) for line in lines]
            html_parts.append("<ol>" + "".join(f"<li>{item}</li>" for item in items) + "</ol>")
            continue

        paragraph = " ".join(lines)
        paragraph = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", paragraph)
        html_parts.append(f"<p>{paragraph}</p>")

    return "".join(html_parts)


@app.route('/')
def index():
    return render_template('index.html', selected_format='report')


@app.route('/process', methods=['POST'])
def process_document():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    output_format = request.form.get('format')
    user_doubt = request.form.get('doubt', 'Provide a systematic, line-by-line explanation.')

    chroma_root = os.path.join(app.config['UPLOAD_FOLDER'], 'chroma_db')
    os.makedirs(chroma_root, exist_ok=True)
    vector_db_path = os.path.join(chroma_root, str(uuid.uuid4()))

    try:
        explanation_text = run_explainer_crew(filepath, user_doubt, vector_db_path)

        if hasattr(explanation_text, 'raw'):
            explanation_text = explanation_text.raw

        formatted_explanation = format_explanation(str(explanation_text))

        return render_template(
            'index.html',
            explanation=formatted_explanation,
            selected_format=output_format or 'report'
        )
    finally:
        gc.collect()
        if os.path.exists(vector_db_path):
            shutil.rmtree(vector_db_path, ignore_errors=True)


if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
