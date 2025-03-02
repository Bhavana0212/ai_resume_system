import PyPDF2
import docx
import os
import logging
from PIL import Image
import pytesseract
import json  # Ensure JSON is properly handled

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_resume(file_path, output_path, job_description=None):
    """Parses resumes from different formats (PDF, DOCX, TXT, image files) and extracts relevant data."""
    
    parsed_data = {}
    ranking_score = 0.0  # Default ranking score
    
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file at {file_path} does not exist.")

        if file_path.endswith('.pdf'):
            parsed_data = parse_pdf(file_path)
        elif file_path.endswith('.docx'):
            parsed_data = parse_docx(file_path)
        elif file_path.endswith('.txt'):
            parsed_data = parse_txt(file_path)
        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            parsed_data = parse_image(file_path)
        else:
            raise ValueError("Unsupported file format")
        
        # Calculate ranking score based on the parsed text and job description
        if parsed_data.get("text"):
            ranking_score = calculate_ranking_score(parsed_data["text"], job_description)
        
        # Save parsed data to output path (optional)
        os.makedirs(output_path, exist_ok=True)
        with open(os.path.join(output_path, 'parsed_data.json'), 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=4)
        
        logging.debug(f"Parsed data: {parsed_data}")
        logging.debug(f"Calculated ranking score: {ranking_score}")
        
        return {"ranking_score": ranking_score, "parsed_data": parsed_data}  # Return as dictionary
    
    except Exception as e:
        logging.error(f"Error parsing resume: {e}")
        return {"error": str(e)}

def parse_pdf(file_path):
    """Parses PDF resumes."""
    text = ""
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in range(len(reader.pages)):
                page_text = reader.pages[page].extract_text() or ""
                text += page_text
        text = clean_text(text)
        logging.debug(f"PDF parsing completed with text: {text[:300]}...")
    except Exception as e:
        logging.error(f"Error parsing PDF file: {e}")
    return {"text": text}

def parse_docx(file_path):
    """Parses DOCX resumes."""
    text = ""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip() != ""])
        text = clean_text(text)
        logging.debug(f"DOCX parsing completed with text: {text[:300]}...")
    except Exception as e:
        logging.error(f"Error parsing DOCX file: {e}")
    return {"text": text}

def parse_txt(file_path):
    """Parses TXT resumes."""
    text = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        text = clean_text(text)
        logging.debug(f"TXT parsing completed with text: {text[:300]}...")
    except Exception as e:
        logging.error(f"Error parsing TXT file: {e}")
    return {"text": text}

def parse_image(file_path):
    """Parses image files using OCR."""
    text = ""
    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        text = clean_text(text)
        logging.debug(f"Image parsing completed with text: {text[:300]}...")
    except Exception as e:
        logging.error(f"Error parsing image file: {e}")
    return {"text": text}

def clean_text(text):
    """Cleans unwanted characters from resume text."""
    return text.replace('\xa0', ' ').replace('\x00', '').strip()

def calculate_ranking_score(resume_text, job_description=None):
    """Calculates ranking score based on matching keywords."""
    score = 0.0
    keywords = ['python', 'data science', 'machine learning', 'software engineer', 'C#', 'AI']
    
    for keyword in keywords:
        if keyword.lower() in resume_text.lower():
            score += 1.0
    
    if job_description:
        job_keywords = extract_keywords_from_job_description(job_description)
        for keyword in job_keywords:
            if keyword.lower() in resume_text.lower():
                score += 1.5
    
    logging.debug(f"Calculated ranking score: {score}")
    return score

def extract_keywords_from_job_description(job_description):
    """Extracts keywords from job description."""
    # You can expand this with a more sophisticated keyword extraction algorithm
    return ['python', 'data analysis', 'teamwork', 'communication', 'problem-solving']

if __name__ == "__main__":
    file_path = "data/resume.pdf"  # Example file path
    output_path = "path/to/output"  # Specify the output path where parsed data will be saved
    job_description = "Looking for a software engineer with Python and ML experience."
    
    result = parse_resume(file_path, output_path, job_description)
    
    if "ranking_score" in result:
        logging.info(f"Resume parsing completed successfully with ranking score: {result['ranking_score']}")
    else:
        logging.error("Resume parsing failed.")
