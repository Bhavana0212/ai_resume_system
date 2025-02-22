from flask import Flask, request, jsonify
import os
import PyPDF2
import docx
import textract
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Function to extract text from resumes
def extract_text_from_resume(file_path):
    text = ""
    file_ext = os.path.splitext(file_path)[1].lower()

    try:
        if file_ext == ".pdf":
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"

        elif file_ext == ".docx":
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"

        elif file_ext in [".txt"]:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

        elif file_ext in [".jpg", ".jpeg", ".png"]:
            text = textract.process(file_path).decode("utf-8")

    except Exception as e:
        return f"Error extracting text: {str(e)}"

    return text.strip()

# Function to calculate similarity between resume and job description
def calculate_similarity(resume_text, job_description):
    try:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([job_description, resume_text])
        similarity_score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0] * 100
        return round(similarity_score, 2)
    except Exception as e:
        return f"Error in similarity calculation: {str(e)}"

# API Endpoint: Upload Resume and Analyze
@app.route("/analyze_resume", methods=["POST"])
def analyze_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No resume file uploaded"}), 400

    resume_file = request.files["resume"]
    job_description = request.form.get("job_description")

    if not job_description:
        return jsonify({"error": "Job description is required"}), 400

    file_path = os.path.join("uploads", resume_file.filename)
    resume_file.save(file_path)

    resume_text = extract_text_from_resume(file_path)
    if "Error" in resume_text:
        return jsonify({"error": resume_text}), 400

    similarity_score = calculate_similarity(resume_text, job_description)

    return jsonify({
        "filename": resume_file.filename,
        "message": "Resume analyzed successfully!",
        "similarity_score": similarity_score
    })

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)  # Create upload folder if not exists
    app.run(debug=True)
