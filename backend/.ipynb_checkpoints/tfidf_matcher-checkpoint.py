import nltk
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import string

# Download necessary NLTK resources
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

# Initialize the Sentence-BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to clean and preprocess the text
def preprocess_text(text):
    # Convert text to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Tokenize the text into words
    words = nltk.word_tokenize(text)
    
    # Remove stopwords (optional, as Sentence-BERT is good at handling this)
    stopwords = nltk.corpus.stopwords.words('english')
    words = [word for word in words if word not in stopwords]
    
    return ' '.join(words)

# Function to compute similarity between resume and job description
def compute_similarity(resume_text, job_desc_text):
    # Preprocess both resume and job description
    cleaned_resume = preprocess_text(resume_text)
    cleaned_job_desc = preprocess_text(job_desc_text)

    # Get embeddings for both texts using Sentence-BERT
    resume_embedding = model.encode([cleaned_resume])
    job_desc_embedding = model.encode([cleaned_job_desc])

    # Compute cosine similarity between the embeddings
    similarity = cosine_similarity(resume_embedding, job_desc_embedding)
    
    return similarity[0][0] * 100  # Return as percentage

# Example Resume and Job Description (you can replace these with your actual data)
resume_text = """
Experienced software developer with a demonstrated history of working in the software industry. 
Skilled in Python, Java, SQL, and cloud computing. Proficient in backend development and data analysis. 
Strong problem-solving and analytical skills. Worked with AWS, Docker, Kubernetes for cloud deployment and containerization. 
"""

job_desc_text = """
We are looking for a highly skilled software developer with expertise in Python, Java, and SQL. 
The ideal candidate will have experience in backend development and cloud technologies such as AWS, Docker, and Kubernetes. 
Strong analytical and problem-solving skills are a must. Experience with machine learning algorithms is a plus. 
"""

# Compute similarity score
similarity_score = compute_similarity(resume_text, job_desc_text)

# Display the result
if similarity_score > 80:
    print(f"Resume Similarity Score: {similarity_score:.2f}% \n🔵 Strong Match! The candidate is a good fit for the job.")
elif similarity_score > 50:
    print(f"Resume Similarity Score: {similarity_score:.2f}% \n🟡 Medium Match! The candidate has potential for the job.")
else:
    print(f"Resume Similarity Score: {similarity_score:.2f}% \n🔴 Very Low Match! The candidate is not a strong fit for the job.")
