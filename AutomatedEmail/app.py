import re
import nltk
from nltk.corpus import stopwords
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from PyPDF2 import PdfReader
from collections import Counter
# import open

#global_var
content_resume = " "
content_prof = " "
keywords_resume = " "
keywords_prof = " "

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

# Function to extract keywords from text using a keyword list
def extract_keywords(text, keyword_list):
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
    words = cleaned_text.split()
    keywords = []

    for i, word in enumerate(words):
        if word in keyword_list:
            # Specify the range of subsequent words to include
            subsequent_words = ' '.join(words[i+1:i+4])  # Include the next 3 words
            keywords.append((word, subsequent_words))

    return keywords

def extract_keywords_by_num(text, num_keywords):
    # Convert the text to lowercase
    cleaned_text = text.lower()
    
    # Remove non-alphanumeric characters
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned_text)
    
    # Split the text into words
    words = cleaned_text.split()
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]
    
    # Find keyword frequencies using Counter
    keyword_frequencies = Counter(words)
    
    # Extract keywords with highest frequencies
    keywords = keyword_frequencies.most_common(num_keywords)
    
    return keywords

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/uploadResume', methods=['GET', 'POST'])
def uploadResume():
    if request.method == 'POST':
        file = request.files['resume']
        pdf_reader = PdfReader(file)
        content_resume = ''
        for page in pdf_reader.pages:
            content_resume += page.extract_text()

        # Predefined keyword list for resume extraction
        keywords = ['skill', 'experience', 'education', 'achievement', 'qualification', 'employ']

        # Extract keywords from the extracted text
        keywords_resume = extract_keywords(content_resume, keywords)

        return render_template('home.html', content=content_resume, keywords_resume=keywords_resume, prof = content_prof, keywords_prof = keywords_prof)
    else:
        return render_template('home.html')
    
def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    num_pages = len(pdf_reader.pages)
    text = ''

    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()

    return text

@app.route('/uploadProfessorWork', methods=['GET', 'POST'])
def uploadProfessorWork():
    if request.method == 'POST':
        file = request.files['professorWork']
        content_prof = extract_text_from_pdf(file)

        # Extract keywords with highest frequencies
        num_keywords = 10  # Number of keywords to extract
        keywords_prof = extract_keywords_by_num(content_prof, num_keywords)

        return render_template('home.html', content=content_resume, keywords_resume=keywords_resume, prof=content_prof, keywords_prof=keywords_prof)
    else:
        return render_template('home.html')