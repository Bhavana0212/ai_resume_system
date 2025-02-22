from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

def calculate_similarity(resume_text, job_description):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
    similarity_score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
    return similarity_score

@app.route('/match_resume', methods=['POST'])
def match_resume():
    data = request.get_json()
    if not data or "resume_text" not in data or "job_description" not in data:
        return jsonify({"error": "Please upload a resume and provide a job description"}), 400
    
    resume_text = data["resume_text"]
    job_description = data["job_description"]
    similarity_score = calculate_similarity(resume_text, job_description)
    return jsonify({"Resume Similarity Score": similarity_score})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
