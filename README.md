# ATS-RESUME
# 📄 ATS Resume & Job Description Matcher

An AI-powered tool designed to help job seekers optimize their resumes. This application uses **Google Gemini AI** to parse resumes, calculate ATS scores, and match candidates against specific Job Descriptions (JD) to provide actionable improvement insights.

## 🚀 Features

* **Resume Analysis:**
    * Supports PDF (`.pdf`) and Word (`.docx`) formats.
    * Extracts key details: Skills, Experience Summary, Education, and Tools.
    * Calculates an estimated **ATS Score (0-100)** based on resume quality.
* **Job Description Matching:**
    * Compares the parsed resume against a user-provided Job Description.
    * Identifies **Matching Skills** and **Missing Skills**.
    * Provides a **Match Percentage** and application status (Yes/No/Maybe).
    * Generates **AI-driven suggestions** to improve the resume for the specific role.
* **Modern UI:** Clean, glassmorphism-inspired interface built with HTML/CSS/JS.

## 🛠️ Tech Stack

* **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
* **Backend:** Python, Flask
* **AI Engine:** Google Gemini API (`google-genai`)
* **File Parsing:** `PyPDF2` (PDFs), `python-docx` (Word docs)

## 📋 Prerequisites

Before running this project, ensure you have:
1.  **Python 3.8+** installed.
2.  A **Google Cloud API Key** (for Gemini AI). You can get one [here](https://aistudio.google.com/).

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/your-username/ats-resume-matcher.git](https://github.com/your-username/ats-resume-matcher.git)
    cd ats-resume-matcher
    ```

2.  **Create a Virtual Environment (Optional but Recommended)**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    Create a file named `requirements.txt` with the following content (or run the command below):
    ```txt
    Flask
    google-genai
    PyPDF2
    python-docx
    ```
    Then install them:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Key**
    * Open `app.py`.
    * Find the line: `GOOGLE_API_KEY = "YOUR_NEW_API_KEY_HERE"`
    * Replace `"YOUR_NEW_API_KEY_HERE"` with your actual Google Gemini API Key.

    > **⚠️ Security Note:** Never commit your actual API key to GitHub. Consider using Environment Variables (`os.getenv`) for production.

## 🏃‍♂️ How to Run

1.  Start the Flask server:
    ```bash
    python app.py
    ```

2.  Open your browser and navigate to:
    ```
    [http://127.0.0.1:5000](http://127.0.0.1:5000)
    ```

## 📖 Usage Guide

1.  **Upload Resume:** Drag and drop your resume (PDF or DOCX) into the upload area.
2.  **View Analysis:** Wait for the AI to extract your skills and calculate your baseline ATS score.
3.  **Match with JD:** Paste a Job Description into the text area and click "Compare Against JD".
4.  **Get Results:** Review the Match Score, Missing Skills, and specific tips on how to tailor your resume.

