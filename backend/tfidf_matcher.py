from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(resume_text, job_description):
    """
    Calculate the TF-IDF cosine similarity between the resume text and job description.

    Args:
        resume_text (str): Extracted text from the resume.
        job_description (str): Job description text.

    Returns:
        float: Similarity score between 0 and 1.
    """
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
    
    similarity_score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
    return similarity_score

if __name__ == "__main__":
    # Example usage for testing
    resume_text = """Experienced Software Engineer skilled in Python, SQL, and cloud computing.
                      Worked on optimizing backend performance and data pipelines."""
    
    job_description = """Looking for a Software Engineer with experience in Python, SQL,
                         and cloud technologies to optimize backend performance."""

    score = calculate_similarity(resume_text, job_description)
    print(f"Resume Similarity Score: {round(score, 2)}")
