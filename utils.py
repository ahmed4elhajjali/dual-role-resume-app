import re
import docx2txt
import pdfplumber
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import os
import PyPDF2

def extract_text(resume_path, extension):
    text = ''
    if extension == '.pdf':
        try:
            with pdfplumber.open(resume_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + ' '
        except Exception as e:
            print(f"Error reading PDF: {e}")
            text = ''
    elif extension in ['.doc', '.docx']:
        try:
            text = docx2txt.process(resume_path)
        except Exception as e:
            print(f"Error reading Word file: {e}")
            text = ''
    else:
        print("Unsupported file format for:", resume_path)
        text = ''
    return text

stop_words = set(stopwords.words('english'))


def extract_text(resume_path, extension):
    text = ''
    if extension == '.pdf':
        try:
            with pdfplumber.open(resume_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + ' '
        except:
            text = textract.process(resume_path).decode('utf-8')
    elif extension in ['.doc', '.docx']:
        text = docx2txt.process(resume_path)
    else:
        text = textract.process(resume_path).decode('utf-8')
    return text


def extract_email(text):
    email = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return email[0] if email else None


def extract_mobile_number(text, custom_regex=None):
    if custom_regex:
        phone = re.findall(custom_regex, text)
    else:
        phone = re.findall(r'\+?\d[\d -]{8,12}\d', text)
    return phone[0] if phone else None


def extract_skills(nlp_text, noun_chunks, skills_file=None):
    data = []
    if skills_file:
        with open(skills_file, 'r', encoding='utf-8') as f:
            data = [line.strip().lower() for line in f.readlines()]
    else:
        data = ['python', 'java', 'machine learning', 'communication', 'teamwork', 'c++', 'sql']

    skills = []
    for token in nlp_text:
        if token.text.lower() in data:
            skills.append(token.text)

    for chunk in noun_chunks:
        chunk_text = chunk.text.lower().strip()
        if chunk_text in data:
            skills.append(chunk_text)

    return list(set(skills))


def extract_name(nlp_text, matcher=None):
    for ent in nlp_text.ents:
        if ent.label_ == 'PERSON':
            return ent.text
    return None


def extract_entity_sections_grad(text):
    entities = {}
    lines = [line.strip() for line in text.split('\n') if line.strip() != '']
    for i, line in enumerate(lines):
        if 'experience' in line.lower():
            entities['experience'] = '\n'.join(lines[i+1:])
        elif 'college' in line.lower():
            entities['College Name'] = line
    return entities


def extract_entities_wih_custom_model(nlp_text):
    entities = {}
    for ent in nlp_text.ents:
        label = ent.label_
        text = ent.text
        if label in entities:
            entities[label].append(text)
        else:
            entities[label] = [text]
    return entities


def get_total_experience(experience_text):
    total_exp = 0
    experience_text = experience_text.lower()
    patterns = [
        r'(\d+)\s+years',
        r'(\d+)\s+yrs',
        r'(\d+)\+?\s+years',
        r'(\d+)\s+months',
        r'(\d+)\s+mos',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, experience_text)
        for match in matches:
            num = int(match)
            if 'month' in pattern or 'mos' in pattern:
                total_exp += num / 12
            else:
                total_exp += num
    return total_exp


def get_number_of_pages(file_path):
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            return len(reader.pages)
    except:
        return 1
