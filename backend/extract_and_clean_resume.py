import os
import re
import logging
import pdfplumber
from docx import Document

# Set up logging for error handling
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the path to the resume file (this will be passed dynamically later)
def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF file {pdf_path}: {str(e)}")
        return None

def extract_text_from_docx(docx_path):
    """Extract text from a DOCX file."""
    try:
        doc = Document(docx_path)
        text = ''
        for para in doc.paragraphs:
            text += para.text + '\n'  # Add newline between paragraphs to maintain formatting
        return text
    except Exception as e:
        logging.error(f"Error extracting text from DOCX file {docx_path}: {str(e)}")
        return None

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
        logging.error("Unsupported file format: %s", file_extension)
        raise ValueError("Unsupported file format")

    # Check if text extraction was successful
    if not text:
        logging.error(f"Failed to extract text from the file: {file_path}")
        return None

    # Clean the extracted text (remove extra spaces & line breaks)
    cleaned_text = " ".join(text.split())

    # Define the cleaned file path
    output_file = file_path.replace(".pdf", "_cleaned.txt").replace(".docx", "_cleaned.txt")

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Save the cleaned text to a file
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(cleaned_text)
        logging.info("✅ Resume text cleaned and saved to: %s", output_file)
    except Exception as e:
        logging.error(f"Error saving cleaned text to {output_file}: {str(e)}")

    return cleaned_text

# Function to extract specific sections from the resume text
def extract_section(text, start_keyword, end_keywords):
    """Extract sections like Experience, Skills, Education."""
    pattern = rf"{start_keyword}(.*?)(?={'|'.join(end_keywords)}|\Z)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else "Not Found"

# Example usage of the functions (update this with dynamic file paths)
def process_resume(file_path):
    cleaned_text = extract_and_clean_resume(file_path)
    if not cleaned_text:
        return None

    # Example: Extract specific sections from the cleaned resume text
    experience = extract_section(cleaned_text, "Experience", ["Skills", "Education"])
    skills = extract_section(cleaned_text, "Skills", ["Education"])
    education = extract_section(cleaned_text, "Education", ["Experience", "Skills"])

    # Define the extracted file path
    extracted_file = file_path.replace(".pdf", "_extracted.txt").replace(".docx", "_extracted.txt")

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(extracted_file), exist_ok=True)

    # Save extracted sections to a file
    try:
        with open(extracted_file, "w", encoding="utf-8") as file:
            file.write(f"🔹 Experience:\n{experience}\n\n")
            file.write(f"🔹 Skills:\n{skills}\n\n")
            file.write(f"🔹 Education:\n{education}\n")
        logging.info("✅ Resume sections extracted and saved to: %s", extracted_file)
    except Exception as e:
        logging.error(f"Error saving extracted sections to {extracted_file}: {str(e)}")

    return extracted_file

# Example: Update the file_path dynamically, e.g. via an API or CLI
file_path = os.path.join(os.getcwd(), 'backend', 'uploads', 'sample.pdf')
extracted_file = process_resume(file_path)
if extracted_file:
    print(f"✅ Process completed successfully. Extracted sections saved to: {extracted_file}")
else:
    print("❌ Failed to process the resume.")
