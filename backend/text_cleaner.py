import textract

# Step 1: Define the path to the resume file
file_path = "/Users/asmassisting/Desktop/ai_resume_system/data/sample.pdf"

# Step 2: Extract text from the PDF
text = textract.process(file_path).decode("utf-8")

# Step 3: Clean the text (remove extra spaces & line breaks)
cleaned_text = " ".join(text.split())

# Step 4: Define the output file path
output_file = "/Users/asmassisting/Desktop/ai_resume_system/backend/cleaned_resume.txt"

# Step 5: Save the cleaned text to a file
with open(output_file, "w", encoding="utf-8") as f:
    f.write(cleaned_text)

print("✅ Resume text cleaned and saved to:", output_file)
