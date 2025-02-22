import streamlit as st
from backend.resume_analyzer import process_resume

# Title and description
st.title("AI-Powered Resume Screening & Ranking System")
st.write("Upload a resume and provide a job description to get started")

# Add some space and a section header for better layout
st.markdown("### Step 1: Upload Resume")
uploaded_file = st.file_uploader("Choose a resume", type="pdf")

# Add a section for job description input
st.markdown("### Step 2: Enter Job Description")
job_description = st.text_area("Enter the job description")

# Process the uploaded file when both job description and resume are uploaded
if uploaded_file and job_description:
    st.write(f"Processing {uploaded_file.name}...")

    # Process the resume with the backend logic
    ranked_resumes = process_resume(uploaded_file, job_description)

    # Display the results
    st.write("Ranking of Resumes based on the Job Description:")
    for idx, score in ranked_resumes:
        st.write(f"Resume {idx+1} - Similarity Score: {score:.2f}")
else:
    st.write("Please u
