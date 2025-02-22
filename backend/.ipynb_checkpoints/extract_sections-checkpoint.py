import re

# Load cleaned resume text
with open("cleaned_resume.txt", "r", encoding="utf-8") as file:
    resume_text = file.read()

# Function to extract a specific section
def extract_section(text, start_keyword, end_keywords):
    pattern = rf"{start_keyword}(.*?)(?={'|'.join(end_keywords)}|\Z)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else "Not Found"

# Extract sections
experience = extract_section(resume_text, "Experience", ["Skills", "Education"])
skills = extract_section(resume_text, "Skills", ["Education"])
education = extract_section(resume_text, "Education", ["Experience", "Skills"])

# Save extracted sections
with open("extracted_sections.txt", "w", encoding="utf-8") as file:
    file.write(f"🔹 Experience:\n{experience}\n\n")
    file.write(f"🔹 Skills:\n{skills}\n\n")
    file.write(f"🔹 Education:\n{education}\n")

print("✅ Resume sections extracted and saved to: extracted_sections.txt")
