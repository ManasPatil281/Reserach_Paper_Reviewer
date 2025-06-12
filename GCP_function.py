import os
import functions_framework
from flask import jsonify, Request
import tempfile
import traceback
import logging
import fitz

from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables securely
GROQ_API_KEY = "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"
GOOGLE_API_KEY ="AIzaSyCld0oOHsbSg7pa0WIvfIU-U7eICexYmhE"

# Initialize models and embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

llm3 = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    api_key=GOOGLE_API_KEY
)

def validate_file(file):
    """Validate uploaded file"""
    if not file:
        return False, "No file uploaded"
    if not file.filename.lower().endswith('.pdf'):
        return False, "Only PDF files are allowed"
    return True, None

def process_pdf_text(file_path):
    """Extract text from PDF"""
    try:
        doc = fitz.open(file_path)
        text = " ".join([page.get_text() for page in doc])
        doc.close()
        return text
    except Exception as e:
        logger.error(f"PDF text extraction error: {e}")
        raise

def analyze_document(text, path):
    """Analyze document based on endpoint"""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
    splits = text_splitter.split_text(text)

    vectorstore = FAISS.from_documents(
        [Document(page_content=split) for split in splits],
        embeddings
    )
    retriever = vectorstore.as_retriever()

    # Select system prompt based on endpoint
    prompts = {
        '/AI_detect_pdf': (
            "Analyze the text to determine if it's AI-generated. "
            "Provide a detailed assessment with a percentage score."
        ),
        '/grammar-check': (
            "Analyze the text to determine if it's AI-generated. "
            "Provide a detailed assessment with a percentage score."
        ),

        '/paraphrase-pdf': (
            "Rephrase the text to improve readability and clarity. "
            "Maintain the original meaning."
        ),
        '/detect-plagiarism': (
            "Perform a thorough plagiarism analysis on the provided text and generate a detailed report similar to Turnitin or Quillbot Premium."
            "The report should include:\n"
            "1. **Overall Plagiarism Score**: Percentage of detected plagiarism.\n"
            "2. **Section-wise Analysis**: Identify specific parts of the text that match external sources, along with percentage similarity.\n"
            "3. **Source Matching**: List external sources (with URLs) where matching content was found and only provide valid urls.\n"
            "4. **Highlighted Plagiarized Text**: Display flagged sentences and phrases.\n"
            "5. **Paraphrasing Suggestions**: Provide rewritten versions of plagiarized sections to improve originality.\n"
            "6. **Original Content Summary**: Identify areas that are unique and free from plagiarism.\n"
            "7. **Formatting**: Use tables, and structured formatting to enhance readability.\n"
            "8. **Final Report**: Include an overall summary and recommendations for improvement.\n"
            "9. Make the report as long and detailed as possible."
        ),
        '/summarize-file': (
            "Create a concise summary that preserves key points. "
            "Ensure clarity and engagement."

        ),
        '/review-file': (
            "Conduct an in-depth review of the research paper with a comprehensive evaluation. "
            "Provide a detailed report including: "
            "1. Abstract Analysis: Assess clarity and relevance "
            "2. Methodology Evaluation: Critique research design "
            "3. Results Interpretation: Analyze depth and accuracy "
            "4. Plagiarism Check: Detect potential unoriginal content "
            "5. Overall Score and Recommendations "
        )
    }

    system_prompt = prompts.get(path, "Analyze the document comprehensively.")

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{context}\n{input}")
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm3, qa_prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    response = rag_chain.invoke({"input": "Process this document."})
    return response["answer"]

@functions_framework.http
def text_analysis(request):
    """Main function to handle different text analysis endpoints"""
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    # Handle preflight requests
    if request.method == 'OPTIONS':
        return ('', 204, headers)

    try:
        path = request.path

        # Text-based endpoints
        text_endpoints = ['/AI_detect_text', '/grammar-check', '/paraphrase-text', '/summarize-text']
        if path in text_endpoints:
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({'error': 'No text provided'}), 400, headers
            
            response = llm3.invoke(f"Analyze this text: {data['text']}")
            return jsonify({"result": response.content}), 200, headers

        # File-based endpoints
        file_endpoints = ['/AI_detect_pdf', '/paraphrase-pdf', '/detect-plagiarism', '/summarize-file','review-file']
        if path in file_endpoints:
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'}), 400, headers
            
            file = request.files['file']
            is_valid, error = validate_file(file)
            if not is_valid:
                return jsonify({'error': error}), 400, headers

            # Save temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                file.save(temp_file.name)
                try:
                    text = process_pdf_text(temp_file.name)
                    result = analyze_document(text, path)
                    return jsonify({"result": result}), 200, headers
                finally:
                    os.unlink(temp_file.name)

        return jsonify({'error': 'Invalid endpoint'}), 404, headers

    except Exception as e:
        logger.error(f"Error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500, headers
