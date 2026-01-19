import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_groq import ChatGroq
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import tempfile
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import aiofiles
import traceback
import logging
from langchain_huggingface import HuggingFaceEndpointEmbeddings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize embeddings with fallback
embeddings = None
HF_TOKEN = os.getenv("HF_TOKEN")


def initialize_embeddings():
    """Initialize embeddings with fallback options"""
    global embeddings
    
    
    try:
        # Try HuggingFace embeddings first
        embeddings = HuggingFaceEndpointEmbeddings(model="sentence-transformers/all-mpnet-base-v2",huggingfacehub_api_token=HF_TOKEN)
        logger.info("Successfully initialized HuggingFace embeddings")
        return embeddings
    except Exception as e:
        logger.warning(f"Failed to initialize HuggingFace embeddings: {str(e)}")
        
    try:
        # Fallback to OpenAI embeddings if available
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings()
        logger.info("Successfully initialized OpenAI embeddings")
        return embeddings
    except Exception as e:
        logger.warning(f"Failed to initialize OpenAI embeddings: {str(e)}")
    
    try:
        # Final fallback to fake embeddings for development
        from langchain_community.embeddings.fake import FakeEmbeddings
        embeddings = FakeEmbeddings(size=384)
        logger.warning("Using fake embeddings - this is for development only")
        return embeddings
    except Exception as e:
        logger.error(f"Failed to initialize any embeddings: {str(e)}")
        embeddings = None
        return None

# Initialize embeddings
try:
    embeddings = initialize_embeddings()
except Exception as e:
    logger.error(f"Critical error initializing embeddings: {str(e)}")
    embeddings = None

# API Keys and Models
Groq_API = os.getenv("GROQ_api_key_Resume") # Updated API key

# Initialize models with error handling
def initialize_models():
    """Initialize LLM models with error handling"""
    try:
        llm = ChatGroq(groq_api_key=Groq_API, model_name="llama-3.1-70b-versatile")  # Updated model name
        llm2 = ChatGroq(groq_api_key=Groq_API, model_name='llama-3.1-8b-instant')
        logger.info("Successfully initialized all LLM models")
        return llm, llm2
    except Exception as e:
        logger.error(f"Error initializing models: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize AI models: {str(e)}")

# Initialize models
llm, llm2 = initialize_models()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    text: str

class TextRequestLang(BaseModel):
    text: str
    lang: str


class Language(BaseModel):
    lang: str

def check_embeddings():
    """Check if embeddings are available and raise error if not"""
    if embeddings is None:
        raise HTTPException(
            status_code=503, 
            detail="Embeddings service is not available. Please install required dependencies: pip install sentence-transformers"
        )

async def process_pdf_file(file, process_func):
    temp_pdf_path = None
    try:
        # Save uploaded file to a temporary file
        async with aiofiles.tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            await temp_pdf.write(await file.read())
            temp_pdf_path = temp_pdf.name

        # Process the PDF
        result = await process_func(temp_pdf_path)
        return result

    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Invalid API Key" in error_msg:
            raise HTTPException(
                status_code=401, 
                detail="Invalid API key. Please check your Groq API key configuration."
            )
        elif "429" in error_msg or "quota" in error_msg.lower():
            raise HTTPException(
                status_code=429, 
                detail="API quota exhausted. Please try again later."
            )
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")
    finally:
        # Remove the temporary file after processing
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            try:
                os.remove(temp_pdf_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file: {cleanup_error}")

@app.get("/")
async def root():
    return {"message": "Server is up. Use the proper endpoints like /health"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        status = {
            "status": "ok",
            "embeddings": "available" if embeddings is not None else "unavailable",
            "models": "initialized"
        }
        
        if embeddings is None:
            status["warning"] = "Embeddings not available - some features may not work"
            
        return status
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.post("/AI_detect_pdf")
async def detect_ai_generated(file: UploadFile = File(...)):
    # Check embeddings availability for RAG operations
    check_embeddings()
    
    async def process_pdf(temp_pdf_path):
        try:
            # Define system prompt for AI detection
            system_prompt = (
                "Analyze the provided text or file to determine whether it is AI-generated. "
                "Provide a detailed assessment with a percentage score indicating the estimated proportion of AI-generated content."
                "Use linguistic patterns, coherence analysis, perplexity, burstiness, and metadata analysis to improve accuracy."
                "Clearly explain the reasoning behind the AI-generated score with supporting evidence from the text."
            )

            # Load the PDF using PyPDFLoader
            loader = PyPDFLoader(temp_pdf_path)
            docs = loader.load()

            # Text splitting for embeddings
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
            splits = text_splitter.split_documents(docs)

            # Create FAISS vectorstore for retrieval
            vectorstore = FAISS.from_documents(splits, embeddings)
            retriever = vectorstore.as_retriever()

            # Prepare QA prompt
            qa_prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{context}\n{input}"),
            ])

            # Create chains
            question_answer_chain = create_stuff_documents_chain(llm2, qa_prompt)
            rag_chain = create_retrieval_chain(retriever, question_answer_chain)

            # Generate response
            response = rag_chain.invoke({"input": 'Detect if the content is AI-generated.'})
            return response["answer"]
        except Exception as e:
            logger.error(f"AI Detection Error: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Process the PDF for AI detection
        ai_detection_result = await process_pdf_file(file, process_pdf)
        return {"result": ai_detection_result}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"AI Detect PDF Error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error detecting AI-generated content in PDF: {str(e)}")

@app.post("/AI_detect_text")
async def detect_text(request: TextRequest):
    """
    Detects whether the provided text input is AI-generated and provides a score.
    """
    system_prompt = (
        f"Analyze the following text: '{request.text}' to determine whether it is AI generated. "
        "Provide a percentage score estimating the AI-generated content. "
        "Explain your reasoning based on linguistic patterns, coherence, perplexity, and metadata analysis."
    )

    try:
        response = llm2.invoke(system_prompt)
        return {"result": response.content}
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Invalid API Key" in error_msg:
            raise HTTPException(status_code=401, detail="Invalid Groq API key. Please check configuration.")
        elif "429" in error_msg:
            raise HTTPException(status_code=429, detail="API rate limit exceeded. Please try again later.")
        raise HTTPException(status_code=500, detail=f"Error detecting AI-generated content: {e}")

@app.post("/grammar-check")
async def grammar_check(request: TextRequest):
    """
    Analyzes and refines the content by performing a comprehensive grammar check.
    """
    system_prompt = (
        f"Perform an advanced grammar and style analysis of the following text: '{request.text }'. "
    "Identify and correct errors related to spelling, punctuation, sentence structure, verb agreement, and word choice."
    "Enhance clarity, coherence, and overall readability while preserving the original meaning."
    f"Ensure the text adheres to the highest linguistic standards for the language."
    "Compare the final output to industry-leading tools like Grammarly, QuillBot and Turnitin."
    "Provide a final score out of 100, along with suggestions for further refinement."

    )

    try:
        response = llm2.invoke(system_prompt)
        return {"result": response.content}
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Invalid API Key" in error_msg:
            raise HTTPException(status_code=401, detail="Invalid Groq API key. Please check configuration.")
        elif "429" in error_msg:
            raise HTTPException(status_code=429, detail="API rate limit exceeded. Please try again later.")
        raise HTTPException(status_code=500, detail=f"Error performing grammar check: {e}")

@app.post("/paraphrase-text")
async def paraphrase_text(request: TextRequestLang):
    """
    Paraphrases the provided text input in the specified language.
    """
    system_prompt = (
        f"Rephrase the following text: '{request.text}' to improve readability, clarity and style. "
        f"Ensure that the revised text is in {request.lang}. "  # Fix: Improved language prompt
        "Maintain the original meaning while refining grammar, sentence flow, and tone. "
        "Give the output in two parts orignal text and paraphrased text."
        "Use precise word choices and avoid unnecessary complexity to ensure an engaging and well-structured output."
    )

    try:
        response = llm2.invoke(system_prompt)
        return {"result": response.content}
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Invalid API Key" in error_msg:
            raise HTTPException(status_code=401, detail="Invalid Groq API key. Please check configuration.")
        elif "429" in error_msg:
            raise HTTPException(status_code=429, detail="API rate limit exceeded. Please try again later.")
        raise HTTPException(status_code=500, detail=f"Error paraphrasing text: {e}")

@app.post("/paraphrase-pdf")
async def paraphrase_pdf(file: UploadFile = File(...)):
    # Check embeddings availability
    check_embeddings()
    
    async def process_pdf(temp_pdf_path):
        try:
            system_prompt = (
                f"Rephrase the following text:  to improve readability, clarity and style in the  language. "
                "Maintain the original meaning while refining grammar, sentence flow, and tone."
                "Use precise word choices and avoid unnecessary complexity to ensure an engaging and well-structured output."
            )

            # Load the PDF using PyPDFLoader
            loader = PyPDFLoader(temp_pdf_path)
            docs = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
            splits = text_splitter.split_documents(docs)

            vectorstore = FAISS.from_documents(splits, embeddings)
            retriever = vectorstore.as_retriever()

            qa_prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{context}\n{input}"),
            ])

            question_answer_chain = create_stuff_documents_chain(llm2, qa_prompt)
            rag_chain = create_retrieval_chain(retriever, question_answer_chain)
            response = rag_chain.invoke({"input": 'paraphrase the text'})
            return response["answer"]
        except Exception as e:
            logger.error(f"PDF Paraphrasing Error: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        paraphrased_text = await process_pdf_file(file, process_pdf)
        return {"result": paraphrased_text}
    except Exception as e:
        logger.error(f"Paraphrase PDF Error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error paraphrasing PDF content: {str(e)}")

@app.post("/detect-plagiarism")
async def detect_plagiarism(file: UploadFile = File(...)):
    """
    Detects plagiarism in an uploaded PDF file and provides a detailed report.
    """
    # Check embeddings availability
    check_embeddings()
    
    async def process_pdf(temp_pdf_path):
        # Load the PDF using PyPDFLoader
        loader = PyPDFLoader(temp_pdf_path)
        docs = loader.load()

        # Split text into chunks for embeddings
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
        splits = text_splitter.split_documents(docs)

        # Create FAISS vectorstore
        vectorstore = FAISS.from_documents(splits, embeddings)
        retriever = vectorstore.as_retriever()

        # Define the system prompt for plagiarism detection
        system_prompt = (
            "Perform a thorough plagiarism analysis on the provided text and generate a detailed report similar to Turnitin or Quillbot Premium."
            "The report should include:\n"
            "1. **Overall Plagiarism Score**: Percentage of detected plagiarism.\n"
            "2. **Section-wise Analysis**: Identify specific parts of the text that match external sources, along with percentage similarity.\n"
            "3. **Source Matching**: List external sources (with URLs) where matching content was found.\n"
            "4. **Highlighted Plagiarized Text**: Display flagged sentences and phrases.\n"
            "5. **Paraphrasing Suggestions**: Provide rewritten versions of plagiarized sections to improve originality.\n"
            "6. **Original Content Summary**: Identify areas that are unique and free from plagiarism.\n"
            "7. **Formatting**: Use code blocks, tables, and structured formatting to enhance readability.\n"
            "8. **Final Report**: Include an overall summary and recommendations for improvement.\n"
            "9. Make the report as long and detailed as possible."
        )

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{context}\n{input}"),
        ])

        # Assume the LLM object is preloaded
        question_answer_chain = create_stuff_documents_chain(llm2, qa_prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        # Input text for detection
        response = rag_chain.invoke({"input": "Detect plagiarism and create a detailed report."})

        # Extract detailed results
        return response["answer"]

    try:
        plagiarism_results = await process_pdf_file(file, process_pdf)
        return {"plagiarism_report": plagiarism_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting plagiarism: {e}")

@app.post("/summarize-text")
async def summarize_text_endpoint(request: TextRequestLang):
    try:
        system_prompt = (
            f"Summarize the following text: '{request.text}' while ensuring enhanced readability, clarity, and conciseness."
            f"generate the summary in the {request.lang} language."
            "Preserve all key points while eliminating redundancy and improving coherence. "
            "Ensure the summary remains engaging and contextually accurate."
        )


        response = llm2.invoke(system_prompt)
        return {"summary": response.content}
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Invalid API Key" in error_msg:
            raise HTTPException(status_code=401, detail="Invalid Groq API key. Please check configuration.")
        elif "429" in error_msg:
            raise HTTPException(status_code=429, detail="API rate limit exceeded. Please try again later.")
        # Log the full error traceback
        logger.error(f"Summarize Text Error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error summarizing text: {str(e)}")

@app.post("/summarize-file")
async def summarize_file(file: UploadFile = File(...),  language: str = "English"):
    # Check embeddings availability
    check_embeddings()
    
    async def process_pdf(temp_pdf_path):
        try:
            # Load the PDF using PyPDFLoader
            loader = PyPDFLoader(temp_pdf_path)
            docs = loader.load()

            # Log document loading
            logger.info(f"PDF Loaded: {temp_pdf_path}, Number of pages: {len(docs)}")

            # Split text for embeddings
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
            splits = text_splitter.split_documents(docs)

            # Create FAISS vectorstore for retrieval
            vectorstore = FAISS.from_documents(splits, embeddings)
            retriever = vectorstore.as_retriever()

            # Define the system prompt for summarization
            system_prompt = (
                f"Summarize the given text to improve readability, coherence, and clarity. "
                f"Ensure the output aligns with the {language}."
                "Maintain the original intent while optimizing the structure for better comprehension and engagement."
            )

            qa_prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{context}\n{input}"),
            ])

            # Assume the LLM object is preloaded
            question_answer_chain = create_stuff_documents_chain(llm2, qa_prompt)
            rag_chain = create_retrieval_chain(retriever, question_answer_chain)

            # Summarize the document
            response = rag_chain.invoke({"input": "Summarize the text."})
            return response["answer"]
        except Exception as e:
            logger.error(f"PDF Summarization Error: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        paraphrased_text = await process_pdf_file(file, process_pdf)
        return {"summary": paraphrased_text}
    except Exception as e:
        logger.error(f"Summarize File Error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error summarizing file content: {str(e)}")

@app.post("/review-file")
async def review_file(file: UploadFile = File(...)):
    # Check embeddings availability
    check_embeddings()
    
    async def process_pdf(temp_pdf_path):
        # Load the PDF using PyPDFLoader
        loader = PyPDFLoader(temp_pdf_path)
        docs = loader.load()

        # Split text for embeddings
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
        splits = text_splitter.split_documents(docs)

        # Create FAISS vectorstore for retrieval
        vectorstore = FAISS.from_documents(splits, embeddings)
        retriever = vectorstore.as_retriever()

        # Define the system prompt for summarization
        system_prompt = (
            "Conduct an in-depth review of the provided research paper and generate a comprehensive evaluation report. "
            "The report should include:\n\n"
            "1. **Abstract Analysis**: Assess the clarity, relevance, and completeness of the abstract.\n"
            "2. **Introduction & Objectives**: Evaluate the introduction's effectiveness in presenting the research problem, objectives, and significance.\n"
            "3. **Literature Review**: Examine the depth, breadth, and credibility of referenced works. Identify gaps or missing sources.\n"
            "4. **Methodology Assessment**: Critique the research design, reproducibility, and clarity of the methodology section.\n"
            "5. **Results & Data Analysis**: Assess the correctness, clarity, and depth of result interpretation.\n"
            "6. **Discussion & Conclusion**: Evaluate how well the discussion connects findings to research objectives and real-world implications.\n"
            "7. **Citations & References**: Verify proper citation format and completeness of sources. Highlight any missing references.\n"
            "8. **Plagiarism Analysis**: Provide:\n"
            "   - Overall plagiarism percentage.\n"
            "   - Sections with detected plagiarism (with matching percentage).\n"
            "   - External sources where similarities were found.\n"
            "   - Highlighted plagiarized phrases with rephrasing suggestions.\n"
            "9. **Suggestions for Improvement**: Offer actionable feedback on clarity, depth, and originality.\n"
            "10. **Strengths & Unique Contributions**: Highlight the paper's originality and strong aspects.\n"
            "11. **Formatting & Presentation**: Assess the paper's grammar, organization, and adherence to academic formatting standards.\n"
            "12. **Overall Summary & Final Score**: Provide a brief summary with a final evaluation score.\n\n"
            "Use code blocks for key highlights (not actual code), structured tables for clarity, and ensure a downloadable review report is available."
        )

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{context}\n{input}"),
        ])

        # Assume the LLM object is preloaded
        question_answer_chain = create_stuff_documents_chain(llm2, qa_prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        # Summarize the document
        response = rag_chain.invoke({"input": "Review the provided research paper and create a detailed report that evaluates its quality, originality, and adherence to academic standards."})
        return response["answer"]

    try:
        paraphrased_text = await process_pdf_file(file, process_pdf)
        return {"summary": paraphrased_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error summarizing file content: {e}")




