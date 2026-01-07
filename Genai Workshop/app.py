import os
import json
import re
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
import PyPDF2
import docx

app = Flask(__name__)

# --- CONFIGURATION ---
# ⚠️ SECURITY NOTE: Never commit your actual API key to GitHub/public repos.
# Use an environment variable for production.
GOOGLE_API_KEY = "YOUR_API_KEY_HERE"  # <--- PASTE YOUR NEW KEY HERE
client = genai.Client(api_key=GOOGLE_API_KEY)

# --- HELPER: CLEAN JSON ---
def clean_json_text(text):
    """Removes markdown code blocks if the AI adds them."""
    text = text.strip()
    # Remove ```json and ``` if present
    if text.startswith("```"):
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text

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
    1. "ats_score": <int 0-100> (General resume quality score)
    2. "skills": [<list of strings (hard skills)>]
    3. "experience_summary": "<string (max 3 sentences)>"
    4. "education": [<list of strings (degrees/universities)>]
    5. "tools_and_tech": [<list of strings (software/tools)>]
    
    Resume Text:
    {resume_text}
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type='application/json')
        )
        cleaned_text = clean_json_text(response.text)
        return json.loads(cleaned_text)
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
    Return a valid JSON object with the following EXACT structure. 
    Ensure "ats_score" is a number between 0 and 100 representing the match percentage.
    
    {{
        "ats_score": <int>,
        "match_percentage": <int>, 
        "can_apply": <string: "Yes", "No", or "Maybe">,
        "matching_skills": [<list of strings: skills present in both>],
        "missing_skills": [<list of strings: skills in JD but missing in Resume>],
        "improvement_suggestions": [<list of strings: specific advice to improve match>]
    }}
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type='application/json')
        )
        
        # Clean and Parse JSON
        cleaned_text = clean_json_text(response.text)
        result = json.loads(cleaned_text)
        return result

    except Exception as e:
        print(f"Match Error: {e}")
        # Return a structure that tells the user something went wrong but keeps the app alive
        return {
            "ats_score": 0,
            "match_percentage": 0,
            "can_apply": "Error",
            "matching_skills": [],
            "missing_skills": ["Error analyzing match"],
            "improvement_suggestions": [f"System Error: {str(e)}"]
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
    return jsonify({"error": "AI failed to analyze resume. Please try again."}), 500

@app.route('/match', methods=['POST'])
def match():
    data = request.json
    resume_text = data.get('resume_text')
    jd_text = data.get('jd_text')

    if not resume_text or not jd_text:
        return jsonify({"error": "Missing Resume or Job Description"}), 400

    results = match_with_jd(resume_text, jd_text)
    
    # If results exist (even if it's the error object), return success so frontend can display it
    if results:
        return jsonify(results)
        
    return jsonify({"error": "AI failed to match Job Description"}), 500

if __name__ == '__main__':
    app.run(debug=True)
