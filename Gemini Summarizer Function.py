import openai
from dotenv import load_dotenv
import os
import pdfplumber
import re


# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key correctly
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key not found in environment variables.")
openai.api_key = api_key


def summarize_medical_report(report_text):
    try:
        prompt = (
            "Summarize the following medical report in simple terms for a non-medical person:\n\n"
            + report_text
        )
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful medical assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating summary: {e}"


def extract_text_from_pdf(pdf_file):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    except Exception as e:
        return f"Error reading PDF: {e}"


def extract_lab_values(text):
    results = {}
    patterns = {
        "Hemoglobin": r"Hemoglobin\s*[:\-]?\s*(\d+\.?\d*)",
        "WBC": r"WBC\s*[:\-]?\s*(\d+\.?\d*)",
        "Platelets": r"Platelets?\s*[:\-]?\s*(\d+\.?\d*)",
        "RBC": r"RBC\s*[:\-]?\s*(\d+\.?\d*)"
    }
    for name, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            results[name] = match.group(1)
    return results


if __name__ == "__main__":
    pdf_filename = "sample_report.pdf"  # You can change this to take input from user

    if not os.path.exists(pdf_filename):
        print(f"❌ File not found: {pdf_filename}")
    else:
        print("📄 Extracting text from PDF...")
        text = extract_text_from_pdf(pdf_filename)

        if text.startswith("Error"):
            print(text)
        else:
            print("✅ Extracted Text:\n", text[:1000], "...")  # show preview of first 1000 chars

            lab_values = extract_lab_values(text)
            print("\n🧪 Extracted Lab Values:", lab_values)

            print("\n🤖 Generating Summary...")
            summary = summarize_medical_report(text)
            print("\n📝 OpenAi Summary:\n", summary)
