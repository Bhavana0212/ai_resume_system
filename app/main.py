import streamlit as st
import requests
import os

# Streamlit Page Configuration
st.set_page_config(page_title="AI Resume Screening", layout="wide")

# Custom Styling
st.markdown("""
    <style>
        .main { background-color: #f5f5f5; }
        .title { text-align: center; font-size: 36px; font-weight: bold; color: #1f77b4; }
        .subtitle { text-align: center; font-size: 18px; color: #555; }
        .upload-box { border: 2px dashed #1f77b4; padding: 20px; border-radius: 10px; background-color: white; }
        .navbar { background-color: #1f77b4; padding: 10px; color: white; text-align: center; font-size: 20px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Navbar
st.markdown('<div class="navbar">AI Resume Screening & Ranking System</div>', unsafe_allow_html=True)

# Title and Description
st.markdown('<p class="title">AI-Powered Resume Screening</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Upload your resume and job description to get an AI-based ranking</p>', unsafe_allow_html=True)

# File Upload Section
st.markdown('<div class="upload-box">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload a Resume", type=["pdf", "docx", "txt", "jpg", "png", "jpeg"])
st.markdown('</div>', unsafe_allow_html=True)

# Job Description Input
job_description = st.text_area("Enter Job Description", height=150)

# Submit Button
if st.button("Submit for Analysis"):
    if uploaded_file is not None and job_description.strip() != "":
        # Save the file locally
        file_path = os.path.join("uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Send to Backend for Processing
        response = requests.post("http://localhost:5000/process_resume", json={
            "file_path": file_path,
            "file_format": uploaded_file.type,
            "job_description": job_description
        })

        if response.status_code == 200:
            st.success("Resume has been uploaded and processed successfully!")
        else:
            st.error("Error processing the resume.")
    else:
        st.warning("Please upload a resume and enter a job description.")
