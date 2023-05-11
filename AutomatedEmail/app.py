from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
import os
from werkzeug.security import check_password_hash, generate_password_hash
from PyPDF2 import PdfReader
# import openai

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Set up OpenAI API credentials
# openai.api_key = os.environ["OPENAI_API_KEY"]

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/uploadResume', methods=['GET', 'POST'])
def uploadResume():
    if request.method == 'POST':
        file = request.files['resume']
        pdf_reader = PdfReader(file)
        text_resume = ''
        for page in pdf_reader.pages:
            text_resume += page.extract_text()
        return render_template('home.html', content = text_resume, prof = '')
    else:
        return render_template('home.html')

@app.route('/uploadProfessorWork', methods=['GET', 'POST'])
def uploadProfessorWork():
    if request.method == 'POST':
        file = request.files['professorWork']
        pdf_reader = PdfReader(file)
        prof_work = ''
        for page in pdf_reader.pages:
            prof_work+= page.extract_text()
        return render_template('home.html', prof = prof_work, content = '')
    else:
        return render_template('home.html')