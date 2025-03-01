from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from resume_ranking import rank_resumes
from tempfile import NamedTemporaryFile

# Initialize the Flask app
app = Flask(__name__)

# Set the folder to save uploaded files
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# API endpoint to upload resumes and rank them
@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        return jsonify({"message": "File uploaded successfully", "filename": filename}), 200
    
    return jsonify({"error": "File type not allowed"}), 400


# API endpoint to rank resumes based on a job description
@app.route('/rank_resumes', methods=['POST'])
def rank_resumes_api():
    if 'job_description' not in request.json:
        return jsonify({"error": "Job description not provided"}), 400

    job_description = request.json['job_description']
    
    # Rank resumes based on the job description
    ranked_resumes = rank_resumes(app.config['UPLOAD_FOLDER'], job_description)
    
    if ranked_resumes:
        return jsonify({
            "ranked_resumes": [{"resume_name": resume[0], "relevance_score": resume[1]} for resume in ranked_resumes]
        }), 200
    else:
        return jsonify({"error": "No resumes found or processed"}), 404


# API endpoint to check the status of the API
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "API is working"}), 200


# Run the Flask app
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)  # Create upload folder if it doesn't exist
    
    app.run(debug=True, host='0.0.0.0', port=5000)
