import pytest
from backend.resume_parser import parse_resume, calculate_ranking_score

# Mock data
sample_resume_text = '''
Tasiana Ukura
tukura@email.com (123) 456-7890 Seattle, WA LinkedIn
WORK EXPERIENCE
Fast - Senior Software Engineer, May 2015 - Present, Seattle, WA
EDUCATION
University of Washington - B.S., Computer Science, August 2004 - May 2008 Seattle, WA
SKILLS
Languages: Python, JavaScript, C++, Java
'''

# Define mock data fixture
@pytest.fixture
def mock_pdf_parsing():
    return sample_resume_text

# Test case for resume parsing
def test_resume_parsing(mock_pdf_parsing):
    # Assuming parse_resume function can work with raw text for testing
    output_path = 'mock_output_path.txt'
    
    # Now pass both arguments
    parsed_resume = parse_resume(mock_pdf_parsing, output_path)
    
    # Adjust assertions based on expected behavior
    assert parsed_resume is not None

# Test case for calculating ranking score
def test_calculate_ranking_score(mock_pdf_parsing):
    # Mock parsed data from the resume
    parsed_data = {
        'text': mock_pdf_parsing
    }
    
    # Pass the text from the parsed data
    ranking_score = calculate_ranking_score(parsed_data['text'])
    
    # Assert the ranking score is as expected (update as needed)
    assert ranking_score >= 0  # Adjust based on your logic

# Test case for ranking score range
def test_ranking_score_range():
    parsed_data = {
        'text': sample_resume_text
    }
    
    # Example ranking score calculation
    ranking_score = calculate_ranking_score(parsed_data['text'])
    
    # Assert that the ranking score is within the expected range (e.g., 0 to 100)
    assert 0 <= ranking_score <= 100

# Parametrized test for different resume formats (PDF, DOCX, TXT)
@pytest.mark.parametrize("file_format, expected_keywords", [
    ("pdf", ['WORK EXPERIENCE', 'EDUCATION', 'SKILLS']),
    ("docx", ['WORK EXPERIENCE', 'EDUCATION', 'SKILLS']),
    ("txt", ['WORK EXPERIENCE', 'EDUCATION', 'SKILLS']),
])
def test_resume_parsing_different_formats(file_format, expected_keywords, mock_pdf_parsing):
    # Mock the output path for testing
    output_path = 'mock_output_path.txt'
    
    # Parse the resume using mock data and output path
    parsed_data = parse_resume(mock_pdf_parsing, output_path)
    
    # Check if the parsed data contains all expected keywords
    assert all(keyword in parsed_data for keyword in expected_keywords)
