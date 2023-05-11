from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
import os
from werkzeug.security import check_password_hash, generate_password_hash
import PyPDF2
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
        # Do something with the file, for example save it
        pdf_reader = PyPDF2.PdfFileReader(file)
        page = pdf_reader.getPage(0)
        text_resume = page.extractText()
        return 'File uploaded successfully'
    else:
        return render_template('home.html')

@app.route('/uploadProfessorWork', methods=['GET', 'POST'])
def uploadProfessorWork():
    if request.method == 'POST':
        file = request.files['professorWork']
        pdf_reader = PyPDF2.PdfFileReader(file)
        page = pdf_reader.getPage(0)
        text_professor = page.extractText()
        return 'File uploaded successfully'
    else:
        return render_template('home.html')