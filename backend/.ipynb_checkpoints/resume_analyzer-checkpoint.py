import os
import re
from flask import Flask, request, jsonify, url_for
import pdfplumber
from docx import Document
from PIL import Image
import pytesseract
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from backend.db_connection import insert_resume, update_resume_status

app = Flask(__name__)

# Set up upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload folder exists

# Load the lightweight pre-trained BERT model
bert_model = SentenceTransformer("all-MiniLM-L6-v2")

# Function to clean and format extracted text
def clean_text(text):
    text = re.sub(r"\(cid:\d+\)", " ", text)  # Remove artifacts
    text = re.sub(r"\s{2,}", "\n", text).strip()  # Remove excessive spaces
    text = text.replace("○␣", "✅ ")  # Fix bullet points
    text = text.replace("•", "✅ ")
    return text

# Function to extract text from resumes
def extract_text(uploaded_file):
    """
    Extracts text from various resume formats (PDF, DOCX, TXT, PNG, JPG).
    """
    file_extension = uploaded_file.filename.split(".")[-1].lower()

    if file_extension == "pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            text = "\n".join([page.extract_text() or "" for page in pdf.pages])
    
    elif file_extension in ["docx", "doc"]:
        doc = Document(uploaded_file)
        text = "\n".join([para.text for para in doc.paragraphs])
    
    elif file_extension in ["png", "jpg", "jpeg"]:
        image = Image.open(uploaded_file)
        text = pytesseract.image_to_string(image)
    
    elif file_extension == "txt":
        text = uploaded_file.read().decode("utf-8", errors="ignore")
    
    else:
        return "❌ Unsupported file format."

    return clean_text(text)

# Function to calculate similarity score using BERT
def calculate_similarity(resume_text, job_desc_text):
    """
    Uses BERT embeddings to compare resume and job description for a more accurate similarity score.
    """
    if not resume_text.strip() or not job_desc_text.strip():
        return 0.0  # Return 0% similarity if either is empty

    # Generate embeddings (numerical representations)
    resume_embedding = bert_model.encode(resume_text, convert_to_tensor=True)
    job_desc_embedding = bert_model.encode(job_desc_text, convert_to_tensor=True)

    # Convert tensors to NumPy arrays
    resume_embedding = resume_embedding.cpu().numpy().reshape(1, -1)
    job_desc_embedding = job_desc_embedding.cpu().numpy().reshape(1, -1)

    # Compute cosine similarity
    similarity_score = cosine_similarity(resume_embedding, job_desc_embedding)[0][0]

    # Convert score to percentage (0-100)
    return round(similarity_score * 100, 2)

# Health check endpoint
@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "API is running!"}), 200

# Root endpoint to list available routes
@app.route("/", methods=["GET"])
def index():
    routes = {
        "ping": url_for("ping", _external=True),
        "upload": url_for("upload_resume", _external=True),
    }
    return jsonify({"message": "Welcome to the Resume Analyzer API", "routes": routes})

# Endpoint to upload resume, analyze it, and store results in the database
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

    # Extract text from the uploaded resume
    resume_text = extract_text(file)

    # Calculate similarity score using BERT
    ranking_score = calculate_similarity(resume_text, job_description)

    # Store the resume data in the database
    insert_resume(file.filename, file_path, job_description, ranking_score)

    # Update status to "Processed"
    update_resume_status(file_path, "Processed")

    return jsonify({"message": "Resume processed successfully", "ranking_score": ranking_score})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
