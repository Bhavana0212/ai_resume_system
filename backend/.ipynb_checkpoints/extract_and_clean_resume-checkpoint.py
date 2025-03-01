import os
import re
import pdfplumber
from docx import Document

# Define the path to the resume file (this will be passed dynamically later)
def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(docx_path):
    """Extract text from a DOCX file."""
    doc = Document(docx_path)
    text = ''
    for para in doc.paragraphs:
        text += para.text
    return text

# Function to clean and extract sections from the resume
def extract_and_clean_resume(file_path):
    """Process and clean the resume, extracting text and sections."""
    file_extension = file_path.split('.')[-1].lower()

    # Extract text based on file type
    if file_extension == "pdf":
        text = extract_text_from_pdf(file_path)
    elif file_extension == "docx":
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format")

    # Clean the extracted text (remove extra spaces & line breaks)
    cleaned_text = " ".join(text.split())

    # Save the cleaned text to a file
    output_file = file_path.replace(".pdf", "_cleaned.txt").replace(".docx", "_cleaned.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    print("✅ Resume text cleaned and saved to:", output_file)
    return cleaned_text

# Function to extract specific sections from the resume text
def extract_section(text, start_keyword, end_keywords):
    """Extract sections like Experience, Skills, Education."""
    pattern = rf"{start_keyword}(.*?)(?={'|'.join(end_keywords)}|\Z)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else "Not Found"

# Example usage of the functions (update this with dynamic file paths)
# Replace 'path_to_file' with actual file path when calling the function
file_path = "/Users/asmassisting/Desktop/ai_resume_system/data/sample.pdf"  # Change this path
cleaned_text = extract_and_clean_resume(file_path)

# Example: Extract specific sections from the cleaned resume text
experience = extract_section(cleaned_text, "Experience", ["Skills", "Education"])
skills = extract_section(cleaned_text, "Skills", ["Education"])
education = extract_section(cleaned_text, "Education", ["Experience", "Skills"])

# Save extracted sections
extracted_file = file_path.replace(".pdf", "_extracted.txt").replace(".docx", "_extracted.txt")
with open(extracted_file, "w", encoding="utf-8") as file:
    file.write(f"🔹 Experience:\n{experience}\n\n")
    file.write(f"🔹 Skills:\n{skills}\n\n")
    file.write(f"🔹 Education:\n{education}\n")

print("✅ Resume sections extracted and saved to:", extracted_file)
