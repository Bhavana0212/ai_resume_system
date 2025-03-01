import streamlit as st
import pdfplumber
from docx import Document
from PIL import Image
import pytesseract
import re
from streamlit_option_menu import option_menu
import nltk
import requests
import pandas as pd
from io import BytesIO
nltk.download('stopwords')
from nltk.corpus import stopwords

# Function to clean and format extracted text
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s{2,}", " ", text).strip()
    text = text.replace("\u25cb\u2423", "✅ ")
    text = text.replace("•", "✅ ")

    stop_words = set(stopwords.words('english'))
    words = text.split()
    words = [word for word in words if word not in stop_words]
    text = " ".join(words)
    
    return text

# Function to extract text from resumes
def extract_text(uploaded_file):
    file_extension = uploaded_file.name.split(".")[-1].lower()

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

# Function to call the backend API to rank resumes
def rank_resumes_from_folder(resumes, job_desc_text):
    url = "https://ai-resume-api.onrender.com/rank_resumes_from_folder"  # Use deployed API URL
    headers = {'Content-Type': 'application/json'}

    # Prepare data to send in the request
    data = {
        'job_description': job_desc_text
    }
    
    # Send POST request to the backend
    try:
        files = {}
        for i, resume in enumerate(resumes):
            files[f'resumes[{i}]'] = (resume['file'].name, resume['file'], resume['file'].type)
        
        response = requests.post(url, files=files, data=data, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Failed to connect to the backend API: {e}")
        return None

# Streamlit UI
st.set_page_config(page_title="AI Resume Screening & Ranking", layout="wide")
st.title("📄 AI Resume Screening & Ranking System")

# Sidebar Navigation
with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu", 
        options=["Home", "Upload Resume", "About"], 
        icons=["house", "cloud-upload", "info-circle"], 
        default_index=0
    )

if selected == "Home":
    st.markdown("Welcome to the AI-powered Resume Screening & Ranking System!")
    st.markdown("This system helps you analyze resumes and match them with job descriptions using advanced AI techniques.")

elif selected == "Upload Resume":
    st.markdown("### Upload Resumes and Job Description")
    uploaded_resumes = st.file_uploader("📂 Upload Resume (PDF, DOCX, TXT, PNG, JPG)", 
                                       type=["pdf", "docx", "txt", "png", "jpg", "jpeg"], 
                                       accept_multiple_files=True)
    uploaded_job_desc = st.text_area("📝 Job Description", height=300)

    submit_button = st.button("🔍 Submit")

    if submit_button:
        if uploaded_resumes and uploaded_job_desc:
            st.success("✅ Files uploaded successfully!")

            resumes = []
            for uploaded_file in uploaded_resumes:
                resume_text = extract_text(uploaded_file)

                if resume_text.strip():
                    resumes.append({
                        "file": uploaded_file,
                        "text": resume_text
                    })
                else:
                    resumes.append({
                        "file": uploaded_file,
                        "text": "❌ No text detected"
                    })

            ranked_resumes = rank_resumes_from_folder(resumes, uploaded_job_desc)
            
            if ranked_resumes:
                resumes_data = ranked_resumes.get('ranked_resumes', [])
                df = pd.DataFrame(resumes_data)

                df["Ranking Score"] = df["Ranking Score"].astype(float) * 100  
                df["Ranking Score"] = df["Ranking Score"].map("{:.2f}%".format)

                df = df.sort_values(by="Ranking Score", ascending=False)

                st.markdown("""
                    <style>
                        .table-container {
                            display: flex;
                            justify-content: center;
                            margin-top: 30px;
                        }
                        .table {
                            border: 1px solid #ddd;
                            width: 80%;
                            margin: 0 auto;
                            padding: 10px;
                            text-align: center;
                        }
                        .table th {
                            background-color: #f4f4f4;
                            color: #333;
                            padding: 10px;
                        }
                        .table td {
                            padding: 10px;
                            border-bottom: 1px solid #ddd;
                        }
                        .table th, .table td {
                            text-align: center;
                            font-size: 16px;
                        }
                        .table tr:nth-child(even) {
                            background-color: #f9f9f9;
                        }
                    </style>
                """, unsafe_allow_html=True)

                st.markdown('<div class="table-container">', unsafe_allow_html=True)
                st.dataframe(df.style.set_table_attributes('class="table"'))
                st.markdown('</div>', unsafe_allow_html=True)

                for resume in resumes:
                    with st.expander(f"📄 {resume['file'].name} - Extracted Text"):
                        st.text_area("Extracted Text:", resume["text"], height=200)

        else:
            st.error("⚠️ Please upload resumes and provide a job description.")

elif selected == "About":
    st.markdown("### About this project")
    st.markdown("""
        This is an AI-based Resume Screening and Ranking system designed to help HR professionals 
        and hiring managers streamline their recruitment process. The tool analyzes resumes, extracts 
        key information, and matches them with job descriptions to provide an accuracy score.
    """)
