import streamlit as st
import pandas as pd
import os
import pdfplumber
import docx
import pytesseract
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Function to extract text from resumes
def extract_text(file):
    text = ""
    if file.type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
    elif file.type in ["text/plain"]:
        text = file.getvalue().decode("utf-8")
    elif file.type in ["image/png", "image/jpeg"]:
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
    return text

# Function to calculate match score using TF-IDF
def calculate_match_score(resume_text, job_desc_text):
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([resume_text, job_desc_text])
    similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(similarity_score * 100, 2)

# Streamlit UI
st.set_page_config(page_title="AI Resume Screening", layout="wide")

st.title("📄 AI-Powered Resume Screening System")

# Job Description Input
st.subheader("📌 Enter Job Description")
job_desc_text = st.text_area("Paste job description here:", height=150)

# Resume Upload Section
st.subheader("📤 Upload Resumes")
uploaded_files = st.file_uploader(
    "Upload multiple resumes (PDF, DOCX, TXT, PNG, JPG)", 
    type=["pdf", "docx", "txt", "png", "jpg"], 
    accept_multiple_files=True
)

if uploaded_files and job_desc_text:
    candidate_data = []
    
    for file in uploaded_files:
        resume_text = extract_text(file)
        match_score = calculate_match_score(resume_text, job_desc_text)
        candidate_data.append({"Candidate Name": file.name, "Match Score": match_score})

    # Convert to DataFrame
    df = pd.DataFrame(candidate_data)
    
    # Sort by Match Score
    df = df.sort_values(by="Match Score", ascending=False)

    # Display Graph
    st.subheader("📊 Match Score Distribution")
    fig, ax = plt.subplots()
    ax.barh(df["Candidate Name"], df["Match Score"], color="skyblue")
    ax.set_xlabel("Match Score (%)")
    ax.set_title("Resume Match Scores")
    st.pyplot(fig)

    # Display Data Table with Sorting & Filtering
    st.subheader("📋 Candidate Results")
    st.dataframe(df.style.background_gradient(cmap="Blues"))

else:
    st.warning("⚠️ Please enter a job description and upload resumes to proceed.")
