import sys
import os
import ssl

# Force Python to add your project root to its path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ['CREWAI_DISABLE_TELEMETRY'] = 'true'
os.environ['OTEL_SDK_DISABLED'] = 'true'

os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
ssl._create_default_https_context = ssl._create_unverified_context

import pyttsx3
from dotenv import load_dotenv
from flask import Flask, render_template, request, url_for
from werkzeug.utils import secure_filename

from agents.crew_orchestrator import run_explainer_crew

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['AUDIO_FOLDER'] = 'static/audio'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)


def generate_speech(text, filename="output.mp3"):
	"""CPU-only text-to-speech using pyttsx3"""
	engine = pyttsx3.init()
	filepath = os.path.join(app.config['AUDIO_FOLDER'], filename)
	engine.save_to_file(text, filepath)
	engine.runAndWait()
	return filename


@app.route('/')
def index():
	return render_template('index.html')


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

	explanation_text = run_explainer_crew(filepath, user_doubt)

	audio_filename = None
	if output_format == 'speech':
		audio_filename = generate_speech(explanation_text)

	return render_template('index.html', explanation=explanation_text, audio_file=audio_filename)


if __name__ == '__main__':
	app.run(debug=True, port=5000)
