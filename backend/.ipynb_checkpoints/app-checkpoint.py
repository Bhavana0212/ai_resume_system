import sys
print(sys.executable)
import os
import logging
from flask import Flask, request, jsonify

# Add the root directory to the sys.path for absolute imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import necessary modules from backend folder
from backend.db_connection import (
    insert_resume, update_ranking_score, update_resume,
    delete_resume, get_top_resumes, get_all_resumes,
    get_resume_by_id, get_resume_by_email
)

from backend.extract_and_clean_resume import extract_and_clean_resume, extract_section

# Absolute import for resume_parser
try:
    from backend.resume_parser import parse_resume
except ImportError as e:
    logging.error(f"Failed to import backend.resume_parser: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)

# Uploads folder configuration
UPLOAD_FOLDER = "backend/uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "png", "jpg", "jpeg"}

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    """Check if the file has a valid extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ Upload & Parse Resume API
@app.route("/upload_resume", methods=["POST"])
def upload_resume():
    """Handles resume file upload, parsing, ranking, and insertion into the database."""
    if "file" not in request.files:
        logging.error("No file uploaded")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    job_description = request.form.get("job_description", "")

    if file.filename == "":
        logging.error("No selected file")
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        try:
            file.save(file_path)
            logging.info(f"File saved at {file_path}")

            # Handle missing output path correctly
            output_path = "backend/parsed_resumes"
            os.makedirs(output_path, exist_ok=True)

            parsed_data = parse_resume(file_path, output_path)
            
            if not parsed_data:
                logging.error("Failed to parse resume")
                return jsonify({"error": "Failed to parse resume"}), 500

            ranking_score = parsed_data.get("ranking_score", 0.0)

            insert_success = insert_resume(
                name=parsed_data.get("name", ""),
                email=parsed_data.get("email", ""),
                phone=parsed_data.get("phone", ""),
                skills=", ".join(parsed_data.get("skills", [])),
                experience=parsed_data.get("experience", ""),
                education=parsed_data.get("education", ""),
                file_path=file_path,
                file_format=file.filename.rsplit(".", 1)[1],
                job_description=job_description,
                ranking_score=ranking_score
            )

            if insert_success:
                logging.info("Resume uploaded and processed successfully!")
                return jsonify({"message": "Resume uploaded and processed successfully!", "ranking_score": ranking_score}), 201
            else:
                logging.error("Failed to insert resume into the database")
                return jsonify({"error": "Failed to insert resume into the database"}), 500

        except Exception as e:
            logging.exception("Exception in upload_resume API")
            return jsonify({"error": str(e)}), 500
    else:
        logging.error("Invalid file format")
        return jsonify({"error": "Invalid file format"}), 400

# ✅ Rank Resumes from Folder API
@app.route('/rank_resumes_from_folder', methods=['POST'])
def rank_resumes_from_folder():
    """Process and rank all resumes in the uploads folder."""
    try:
        job_description = request.json.get("job_description", "")

        if not job_description:
            return jsonify({"error": "Job description is required"}), 400

        resume_files = [f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]
        if not resume_files:
            return jsonify({"error": "No resumes found in the folder"}), 404

        ranked_resumes = []
        
        for filename in resume_files:
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            logging.info(f"Processing file: {filename}")

            # Handle missing output path correctly
            output_path = "backend/parsed_resumes"
            os.makedirs(output_path, exist_ok=True)

            parsed_data = parse_resume(file_path, output_path)
            if parsed_data:
                logging.info(f"Parsed data for {filename}: {parsed_data}")
                ranking_score = parsed_data.get("ranking_score", 0.0)
                ranked_resumes.append({
                    "filename": filename,
                    "ranking_score": ranking_score,
                    "parsed_data": parsed_data
                })
            else:
                logging.warning(f"Failed to parse file: {filename}")

        if ranked_resumes:
            ranked_resumes.sort(key=lambda x: x["ranking_score"], reverse=True)
            return jsonify({"ranked_resumes": ranked_resumes}), 200
        else:
            return jsonify({"error": "No valid resumes parsed"}), 404

    except Exception as e:
        logging.exception("Exception in rank_resumes_from_folder API")
        return jsonify({"error": str(e)}), 500

# ✅ API Health Check
@app.route("/ping", methods=["GET"])
def health_check():
    """Check if the API is running."""
    return jsonify({"message": "API is running successfully!"}), 200

if __name__ == "__main__":
    # Enable debug mode for better logging
    app.run(debug=True, host="0.0.0.0", port=5000)
