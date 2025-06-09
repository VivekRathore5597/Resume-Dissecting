from flask import Flask, render_template, request, jsonify
from PyPDF2 import PdfReader
import google.generativeai as genai
import os
import json

# Set your API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyC9Lz4qHl0rUnOZ1ofODd-bA9txbzhE2Nk"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# App creation
app = Flask(__name__)

# Load model
model = genai.GenerativeModel("models/gemini-2.0-flash-lite")


def resumes_details(resume):
    prompt = f"""
    You are a resume dissecting assistant. Given the following resume text, extract all the important details and return them in a well-structured JSON format.

    The resume text:
    {resume}

    Extract and include the following:
    - Full Name
    - Contact Number
    - Email Address
    - Location
    - Skills
    - Education
    - Certifications
    - Languages
    - Work Experience
    - Recommended Jobs

    Return the response in JSON format.
    """
    response = model.generate_content(prompt).text
    return response


# API end points
@app.route("/")
def index():
    return render_template("index.html")


@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['resume']

    if file.filename == '':
        return jsonify({"error": "No file selected"})

    if file and file.filename.endswith('.pdf'):
        text = ""
        reader = PdfReader(file.stream)
        for page in reader.pages:
            text += page.extract_text()

        # Get resume details from model
        response = resumes_details(text)

        print(response)  # For debug

        # Clean the response by removing the ```json and surrounding text
        response_clean = response.replace("```json", "").replace("```", "").strip()

        # Load the cleaned response into a dictionary
        data = json.loads(response_clean)

        # Extract details from the JSON response
        full_name = data.get("full_name")
        contact_number = data.get("contact_number")
        email_address = data.get("email_address")
        location = data.get("location", "")

        # Skills Extraction
        skills = data.get('skills', [])

        # Education extraction
        education_list = data.get("education", [])
        education_str = " ".join([
            f"{edu.get('degree', '')} from {edu.get('university', '')} (Graduated: {edu.get('graduation_year', '')})"
            for edu in education_list
        ])

        # Work Experience extraction
        work_experience_list = data.get("work_experience", [])
        work_experience_str = "\n".join([
            f"{job.get('title', '')}\nResponsibilities: {', '.join(job.get('description', []))}"
            for job in work_experience_list
        ])

        # Certification Extraction
        certifications = data.get("certifications", [])
        certifications_str = ", ".join([cert.get("name", "") for cert in certifications])

        # Language Extraction
        languages = data.get("languages", [])
        languages_str = ", ".join([lang.get("language", "") for lang in languages])

        # Recommended Job Roles Extraction
        recommended_jobs = data.get("recommended_jobs", [])
        recommended_jobs_str = ", ".join(
            [job.get("title", "") if isinstance(job, dict) else job for job in recommended_jobs])

        # Return all extracted information
        return render_template('index.html',
            full_name=full_name,
            contact_number=contact_number,
            email_address=email_address,
            location=location,
            skills=skills,
            education=education_str,
            work_experience=work_experience_str,
            certifications=certifications_str,
            languages=languages_str,
            recommended_jobs=recommended_jobs_str)




# Start the Flask app
if __name__ == "__main__":
    app.run(debug=True)




