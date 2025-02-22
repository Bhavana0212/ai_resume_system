from flask import Flask, request, jsonify
import os
from backend.db_connection import insert_resume, update_resume_status
from backend.resume_analyzer import analyze_resume
import tempfile

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload folder exists

@app.route("/upload", methods=["POST"])
def upload_resume():
    """Endpoint to upload resume, analyze it, and store results in the database."""
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["resume"]
    job_description = request.form.get("job_description", "")

    if not file or not job_description:
        return jsonify({"error": "File and job description are required"}), 400

    # Save the resume temporarily
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Analyze the resume using TF-IDF
    ranking_score = analyze_resume(file_path, job_description)

    # Store the resume data in the database
    insert_resume(file.filename, file_path, job_description, ranking_score)

    # Update status to "Processed"
    update_resume_status(file_path, "Processed")

    return jsonify({"message": "Resume processed successfully", "ranking_score": ranking_score})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
