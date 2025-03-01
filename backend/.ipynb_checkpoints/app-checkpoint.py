import sys
import os
import logging
from flask import Flask, request, jsonify

# Add the root directory to sys.path for absolute imports
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

@app.route('/')
def home():
    return 'Hello, World!'

# Function to call the backend API to rank resumes
def rank_resumes_from_folder(resumes, job_desc_text):
    url = "https://ai-resume-api.onrender.com/rank_resumes_from_folder"  # Use deployed API URL
    headers = {'Content-Type': 'application/json'}

    # Prepare data to send in the request
    data = {
        'job_description': job_desc_text
    }

    try:
        files = {}
        for i, resume in enumerate(resumes):
            files[f'resumes[{i}]'] = (resume['file'].name, resume['file'], resume['file'].type)

        # Send POST request to the backend
        response = requests.post(url, files=files, data=data, headers=headers)
        
        # Debugging response
        st.write("API Response Code:", response.status_code)
        st.write("API Response Text:", response.text)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Failed to connect to the backend API: {e}")
        return None


# ✅ Upload & Parse Resume API
@app.route('/upload_resume', methods=["POST"])
def upload_resume():
    """Handles resume file upload, parsing, ranking, and insertion into the database."""
    if 'resume' not in request.files:
        logging.error("No file uploaded")
        return jsonify({"error": "No file uploaded"}), 400
   
    resume_file = request.files['resume']
    job_description = request.form.get("job_description", "")

    if resume_file.filename == '':
        logging.error("No selected file")
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save the file
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], resume_file.filename)
        resume_file.save(file_path)
        logging.info(f"File saved at {file_path}")

        # Ensure output directory exists
        output_path = "backend/parsed_resumes"
        os.makedirs(output_path, exist_ok=True)

        # Parse the resume file
        parsed_data = parse_resume(file_path, output_path)
        if not parsed_data:
            logging.error("Failed to parse resume")
            return jsonify({"error": "Failed to parse resume"}), 500

        ranking_score = parsed_data.get("ranking_score", 0.0)

        # Insert parsed resume into the database
        insert_success = insert_resume(
            name=parsed_data.get("name", ""),
            email=parsed_data.get("email", ""),
            phone=parsed_data.get("phone", ""),
            skills=", ".join(parsed_data.get("skills", [])),
            experience=parsed_data.get("experience", ""),
            education=parsed_data.get("education", ""),
            file_path=file_path,
            file_format=resume_file.filename.rsplit(".", 1)[1],
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


# ✅ Rank Resumes from Folder API
@app.route('/rank_resumes_from_folder', methods=['POST'])
def rank_resumes_from_folder():
    """Process and rank all resumes in the uploads folder."""
    logging.info("Rank Resumes API called with job description: %s", request.form.get("job_description"))
    
    try:
        # Fix: Use form-data instead of JSON
        job_description = request.form.get("job_description", "")

        if not job_description:
            logging.error("Job description is required")
            return jsonify({"error": "Job description is required"}), 400

        resume_files = [f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]
        if not resume_files:
            logging.warning("No resumes found in the folder")
            return jsonify({"error": "No resumes found in the folder"}), 404

        ranked_resumes = []
        
        for filename in resume_files:
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            logging.info(f"Processing file: {filename}")

            # Ensure output directory exists
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


# Catch-all route for debugging
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    logging.error(f"Request to non-existent route: {path}")
    return jsonify({"error": f"Route {path} not found"}), 404

# Log all registered routes (useful for debugging route issues)
def log_registered_routes():
    logging.info("Registered routes:")
    for rule in app.url_map.iter_rules():
        logging.info(f"Route: {rule}")

if __name__ == "__main__":
    # Log registered routes manually when the app starts
    log_registered_routes()
    
    # Enable debug mode for better logging
    app.run(debug=True, host="0.0.0.0", port=5000)
