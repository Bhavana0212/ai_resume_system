import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text.strip()

def analyze_resume(resume_path, job_description):
    """Compute the similarity score between a resume and a job description using TF-IDF."""
    resume_text = extract_text_from_pdf(resume_path)
    
    if not resume_text:
        return 0  # Return 0 if the resume text extraction fails

    documents = [resume_text, job_description]  # List containing resume and job description
    vectorizer = TfidfVectorizer()  # Initialize TF-IDF Vectorizer
    tfidf_matrix = vectorizer.fit_transform(documents)  # Convert text to TF-IDF matrix

    # Compute cosine similarity between the resume and the job description
    similarity_score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

    return round(similarity_score * 100, 2)  # Convert to percentage
