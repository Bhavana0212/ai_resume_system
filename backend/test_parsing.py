import logging
from backend.resume_parser import parse_resume

# Set up logging to capture debug information
logging.basicConfig(level=logging.DEBUG)

# Test the parsing function
if __name__ == "__main__":
    # Replace these with actual paths to your test files
    file_path_pdf = "data/resume.pdf"  # Update with your PDF file path
    file_path_docx = "data/resume.docx"  # Update with your DOCX file path
    output_path = "path/to/output"  # Update with your output directory
    job_description = "We are looking for a software engineer with experience in Python and machine learning."

    # Test parsing PDF
    try:
        ranking_score_pdf, parsed_data_pdf = parse_resume(file_path_pdf, output_path, job_description)
        if ranking_score_pdf is not None:
            logging.info(f"PDF Resume parsing completed with ranking score: {ranking_score_pdf}")
        else:
            logging.error("PDF Resume parsing failed.")
    except Exception as e:
        logging.error(f"Error parsing PDF resume: {e}")

    # Test parsing DOCX
    try:
        ranking_score_docx, parsed_data_docx = parse_resume(file_path_docx, output_path, job_description)
        if ranking_score_docx is not None:
            logging.info(f"DOCX Resume parsing completed with ranking score: {ranking_score_docx}")
        else:
            logging.error("DOCX Resume parsing failed.")
    except Exception as e:
        logging.error(f"Error parsing DOCX resume: {e}")

    # Log the parsed data for DOCX to inspect
    logging.debug(f"Parsed DOCX Resume: {parsed_data_docx}")

    # Additional logging to inspect the parsed text from both formats
    logging.debug(f"Parsed PDF Resume: {parsed_data_pdf}")
