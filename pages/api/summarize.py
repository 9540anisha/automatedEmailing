import openai
import os
import re
import splitText
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
max_tokens = 1000
chunks = []

def readTextFile(paperFilePath):
    with open(paperFilePath, encoding='utf-8') as file:
        text = file.read()
        # print(re.findall(r'\w+', text).__len__())       # number of tokens
        # print("raw text: \n -----------------\n" + text + "--------------------------\n")
        return text

def splitFile(textFile):
    return splitText.split_file(textFile, max_tokens)

def showPaperSummary(chunks):
    output = ""
    skips = 0
    openai.api_key = OPENAI_API_KEY
    for i, chunk in enumerate(chunks):
        prompt = f"Summarize the following research paper:\n{chunk}"
        response = openai.Completion.create(engine="text-davinci-002",prompt=prompt,temperature=0.5,
            max_tokens=100,
            n=1,
            stop=None
        )
        if(i == 0):
            output += "Paper Summary: \n" + response["choices"][0]["text"] + "\nKey Points: \n"
            # print("Paper Summary: \n")
            # print(response["choices"][0]["text"])
            # print("Key Points:")
        else:
            tempString = f"#{i - skips}:" + response["choices"][0]["text"] + "\n \n"
            if(tempString.count("et al.") > 2):
                skips += 1
                continue
            output += tempString
    return output

'''Example implementation'''
# chunks = splitFile(readTextFile(paperFilePath = r'C:\Users\User\openai-quickstart-node\pages\api\paper.txt'))
# print(showPaperSummary(chunks))
