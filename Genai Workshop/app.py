import os
import json
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
import PyPDF2
import docx

app = Flask(__name__)

# --- CONFIGURATION ---
# ⚠️ IMPORTANT: Replace with your NEW API Key. The previous one is compromised.
GOOGLE_API_KEY = "AIzaSyCk9JPpcxMQAj4T1WEbg5mYYRRrW9zuZYQ" 
client = genai.Client(api_key=GOOGLE_API_KEY)

def extract_text(file):
    text = ""
    try:
        if file.filename.lower().endswith('.pdf'):
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted: text += extracted + "\n"
        elif file.filename.lower().endswith('.docx'):
            doc = docx.Document(file)
            for para in doc.paragraphs:
                text += para.text + "\n"
    except Exception as e:
        print(f"Extraction Error: {e}")
    return text

# --- STEP 1: RESUME PROFILE EXTRACTION ---
def parse_resume_profile(resume_text):
    prompt = f"""
    You are an AI Resume Analyzer. Extract the following details from the resume text below.
    Return ONLY a valid JSON object. Do not add markdown formatting.

    Keys required:
    1. "ats_score": <int 0-100> (Estimate the ATS readability score)
    2. "skills": [<list of strings (hard skills)>]
    3. "experience_summary": "<string (max 3 sentences)>"
    4. "education": [<list of strings (degrees/universities)>]
    5. "tools_and_tech": [<list of strings (software/tools)>]
    
    Resume Text:
    {resume_text}
    """
    try:
        # Fixed Model Name to 'gemini-1.5-flash'
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type='application/json')
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Analysis Error: {e}")
        return None

# --- STEP 2: JOB DESCRIPTION MATCHING (FIXED) ---
def match_with_jd(resume_text, jd_text):
    prompt = f"""
    Act as a strict Application Tracking System (ATS). Compare the Resume against the Job Description (JD).
    
    RESUME:
    {resume_text}
    
    JOB DESCRIPTION:
    {jd_text}

    OUTPUT INSTRUCTIONS:
    Return a valid JSON object with the following EXACT structure:
    {{
        "match_percentage": <int between 0 and 100>,
        "can_apply": <string: "Yes", "No", or "Maybe">,
        "matching_skills": [<list of strings: skills present in both>],
        "missing_skills": [<list of strings: skills in JD but missing in Resume>],
        "improvement_suggestions": [<list of strings: specific advice to improve match>]
    }}
    """
    try:
        # Fixed Model Name to 'gemini-1.5-flash'
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type='application/json')
        )
        
        # Parse JSON safely
        result = json.loads(response.text)
        return result
    except Exception as e:
        print(f"Match Error: {e}")
        # Return a fallback JSON so the frontend doesn't crash
        return {
            "match_percentage": 0,
            "can_apply": "Error",
            "matching_skills": [],
            "missing_skills": [],
            "improvement_suggestions": ["Error analyzing match. Please try again."]
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files.get('resume')
    if not file: return jsonify({"error": "No file uploaded"}), 400
    text = extract_text(file)
    analysis = parse_resume_profile(text)
    if analysis:
        return jsonify({"analysis": analysis, "raw_text": text})
    return jsonify({"error": "AI failed to analyze resume"}), 500

@app.route('/match', methods=['POST'])
def match():
    data = request.json
    resume_text = data.get('resume_text')
    jd_text = data.get('jd_text')

    # Validation
    if not resume_text or not jd_text:
        return jsonify({"error": "Missing Resume or Job Description"}), 400

    results = match_with_jd(resume_text, jd_text)
    if results:
        return jsonify(results)
    return jsonify({"error": "AI failed to match Job Description"}), 500

if __name__ == '__main__':
    app.run(debug=True)