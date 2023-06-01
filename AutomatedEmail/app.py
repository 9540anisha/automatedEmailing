import os
import re
import nltk
from nltk.corpus import stopwords, wordnet
from flask import Flask, render_template, request
from flask_session import Session
from PyPDF2 import PdfReader
from collections import Counter
from summarize import splitFile, showPaperSummary
import openai
from dotenv import load_dotenv

load_dotenv()

nltk.download('cmudict')
nltk.download('stopwords')
nltk.download('punkt')

#global_var
# content_resume = " "
# content_prof = " "
# keywords_resume = " "
# keywords_prof = " "

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

openai.api_key = os.getenv('OPEN_AI_KEY')

max_tokens = 1000
chunks = []

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
        content_resume = ' '
        for page in pdf_reader.pages:
            content_resume += page.extract_text()

        # Predefined keyword list for resume extraction
        keywords = ['skill', 'experience', 'education', 'achievement', 'qualification', 'employ']

        # Extract keywords from the extracted text
        keywords_resume = extract_keywords(content_resume, keywords)

        return render_template('home.html', content=content_resume, keywords_resume=keywords_resume)
    else:
        return render_template('home.html')
    
def extract_keywords_by_difficulty(text, threshold):
    # Tokenize the text into words
    words = nltk.word_tokenize(text)
    
    # Filter out words less than or equal to two characters
    words = [word for word in words if len(word) > 2 and word.lower() not in stopwords.words('english')]
    
    difficult_words = []
    
    # Check the difficulty level of each word using WordNet
    for word in words:
        synsets = wordnet.synsets(word)
        
        # If no synsets are found, consider the word difficult
        if not synsets:
            difficult_words.append(word)
        else:
            # Get the first synset of the word
            first_synset = synsets[0]
            
            # If the synset has a complexity score above the threshold, consider the word difficult
            if wordnet.synset(first_synset.name()).lexname().split('.')[0] in ['noun', 'verb', 'adjective', 'adverb']:
                if first_synset.pos() == 'n':
                    complexity_score = wordnet.synset(first_synset.name()).max_depth() / 20
                elif first_synset.pos() in ['v', 'a', 'r']:
                    complexity_score = wordnet.synset(first_synset.name()).max_depth() / 10
                else:
                    complexity_score = 0
                
                if complexity_score > threshold:
                    difficult_words.append(word)
    
    return difficult_words
    
def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    num_pages = len(pdf_reader.pages)
    text = ''

    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()

    return text

def get_word_definition(word):
    synsets = wordnet.synsets(word)
    if synsets:
        definition = synsets[0].definition()
        return definition
    else:
        return None

@app.route('/uploadProfessorWork', methods=['GET', 'POST'])
def uploadProfessorWork():
    if request.method == 'POST':
        file = request.files['professorWork']
        pdf_reader = PdfReader(file)
        content_prof = ' '
        for page in pdf_reader.pages:
            content_prof += page.extract_text()
        print(content_prof)
        # Extract keywords from the professor's work based on difficulty
        difficulty_threshold = 0.5  # Adjust the threshold to your preference
        keywords_prof = extract_keywords_by_difficulty(content_prof, difficulty_threshold)
        print(keywords_prof)

        # Get the definition for each keyword and filter out keywords with no definition
        keyword_definitions = {keyword: get_word_definition(keyword) for keyword in keywords_prof}
        keyword_definitions = {k: v for k, v in keyword_definitions.items() if v is not None}
        print(keyword_definitions)

        # Generate the paper summary
        chunks = splitFile(content_prof)
        for i, chunk in enumerate(chunks):
            with open(f'chunk_{i+1}.txt', 'w', encoding='utf-8') as output_file:
                output_file.write(chunk)
            print(chunk + "\n ----------------------------- \n")
        print(showPaperSummary(chunks))

        return render_template('home.html', keywords_prof=keywords_prof, keyword_definitions=keyword_definitions)
    else:
        return render_template('home.html')