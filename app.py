from flask import Flask, render_template, request
import os
import PyPDF2
import google.generativeai as genai

app = Flask(__name__)

# Configure Google API and Gemini API keys
os.environ['GEMINI_API_KEY'] = "AIzaSyDxK7CxvKYGt62fL3XsLJDR6oB-cXdX35I"
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

def generate_gemini_content(prompt):
    # Generate content using the Gemini AI model
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

def extract_text_from_pdf(file):
    # Function to extract text from a PDF file
    text = ''
    try:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        text = f"Failed to extract text due to: {str(e)}"
    return text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/symptoms', methods=['POST'])
def symptoms():
    symptoms = request.form['symptoms']
    response = generate_gemini_content(f"A user reports the following symptoms: {symptoms}. What general advice should be given?")
    return render_template('index.html', symptoms_result=response)

@app.route('/conditions', methods=['POST'])
def conditions():
    conditions = request.form['conditions']
    response = generate_gemini_content(f"A user has these health conditions: {conditions}. How should this affect their care for the symptoms mentioned earlier?")
    return render_template('index.html', conditions_result=response)

@app.route('/labreport', methods=['POST'])
def labreport():
    lab_report = request.files['lab_report']
    if lab_report:
        lab_report_text = extract_text_from_pdf(lab_report)
        if lab_report_text:
            prompt = "Based on the extracted text from the user's lab report, provide insights and suggestions for the following:\n\n"
            prompt += "1. Analyze glucose levels and other relevant parameters to predict the likelihood of diabetes an tell the user if he has diabeties or not.\n\n"
            prompt += "2. Evaluate cholesterol levels, blood pressure, and other indicators to assess the risk of heart disease.On a scale of very low risk to very high risk give rating of colestrol levels\n\n"
            prompt += "3. Examine liver function tests and other markers to determine the possibility of liver disease. rate the health of liver from on a scale 1 to 5\n\n"
            prompt += "4. Assess the overall balance of blood components, including red blood cells, white blood cells, and platelets. mention the deficeinet components and give better supplements for their enhancement\n\n"
            prompt += "5. If the provided text doeant fulfil any of the above criterias, then just analyse it extract insights and predictions from that\n\n"
            prompt += f"Extracted text from the lab report: {lab_report_text[:1000000]}.\n\nWhat insights can be drawn?"
            
            response = generate_gemini_content(prompt)
            return render_template('index.html', labreport_result=response)
        else:
            return render_template('index.html', labreport_result="Unable to extract text from the lab report or file is empty.")
    else:
        return render_template('index.html', labreport_result="No lab report provided.")

if __name__ == "__main__":
    app.run(debug=True)
