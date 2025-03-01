import PyPDF2
import docx
import os

def parse_resume(file_path, output_path):
    """Parses resumes from different formats (PDF, DOCX) and extracts relevant data."""
    
    parsed_data = {}
    try:
        if file_path.endswith('.pdf'):
            parsed_data = parse_pdf(file_path)
        elif file_path.endswith('.docx'):
            parsed_data = parse_docx(file_path)
        else:
            raise ValueError("Unsupported file format")
        
        # Save parsed data to output path (optional)
        os.makedirs(output_path, exist_ok=True)
        with open(os.path.join(output_path, 'parsed_data.json'), 'w') as f:
            f.write(str(parsed_data))
        
        return parsed_data
    except Exception as e:
        print(f"Error parsing resume: {e}")
        return None

def parse_pdf(file_path):
    """Parses PDF resumes."""
    text = ""
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
    return {"text": text}

def parse_docx(file_path):
    """Parses DOCX resumes."""
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return {"text": text}
