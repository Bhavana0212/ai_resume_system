import streamlit as st
import requests
import json

# Flask API URL
FLASK_API_URL = "http://127.0.0.1:5000/match_resume"

st.title("AI Resume Screening & Ranking System")

# Text inputs for job description and resume text
job_description = st.text_area("Enter Job Description:")
resume_text = st.text_area("Enter Resume Text:")

if st.button("Match Resume"):
    if job_description and resume_text:
        # Prepare JSON payload
        payload = {"resume_text": resume_text, "job_description": job_description}
        headers = {"Content-Type": "application/json"}

        # Send request to Flask API
        response = requests.post(FLASK_API_URL, data=json.dumps(payload), headers=headers)

        # Display result
        if response.status_code == 200:
            similarity_score = response.json().get("Resume Similarity Score", "Error")
            st.success(f"Resume Similarity Score: {similarity_score:.2f}")
        else:
            st.error(f"Error: {response.text}")
    else:
        st.warning("Please enter both resume text and job description.")
