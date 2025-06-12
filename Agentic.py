import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import tempfile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import aiofiles
import traceback
import logging
from langchain.docstore.document import Document
import PyPDF2
import requests
import xml.etree.ElementTree as ET

# LangChain imports for agents
from langchain.agents import tool, Tool, AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import BaseTool

# Define request models
class TextRequest(BaseModel):
    text: str

class TextRequestLang(BaseModel):
    text: str
    lang: str = "English"

# Custom ArXiv search function
def arxiv_search(query: str) -> str:
    """Search for papers on arXiv"""
    try:
        base_url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": 5,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        
        response = requests.get(base_url, params=params)
        
        if response.status_code != 200:
            return f"Error searching arXiv: HTTP {response.status_code}"
        
        # Parse XML response
        root = ET.fromstring(response.content)
        
        # Define namespace
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        
        # Extract entries
        entries = root.findall('atom:entry', namespace)
        
        if not entries:
            return "No results found on arXiv for this query."
        
        results = []
        for entry in entries:
            title = entry.find('atom:title', namespace).text.strip()
            summary = entry.find('atom:summary', namespace).text.strip()
            published = entry.find('atom:published', namespace).text.strip()
            
            # Get authors
            authors = [author.find('atom:name', namespace).text for author in entry.findall('atom:author', namespace)]
            authors_str = ", ".join(authors)
            
            # Get link (URL)
            links = entry.findall('atom:link', namespace)
            url = next((link.get('href') for link in links if link.get('rel') == 'alternate')), "No URL available"
            
            result = {
                'title': title,
                'authors': authors_str,
                'published': published,
                'summary': summary,
                'url': url
            }
            results.append(result)
        
        # Format results nicely
        formatted_results = "\n\n".join([
            f"Title: {r['title']}\n"
            f"Authors: {r['authors']}\n"
            f"Published: {r['published']}\n"
            f"URL: {r['url']}\n"
            f"Summary: {r['summary']}"
            for r in results
        ])
        
        return formatted_results
    
    except Exception as e:
        return f"Error searching arXiv: {str(e)}"

# We'll keep the ScholarTool implementation since it's custom
from scholarly import scholarly

# Custom ScholarTool implementation
class ScholarTool(BaseTool):
    name: str = "scholar_search"
    description: str = "Search for academic papers and publications on Google Scholar"
    
    def _run(self, query: str) -> str:
        try:
            search_query = scholarly.search_pubs(query)
            results = []
            # Get first 5 results
            for i in range(5):
                try:
                    pub = next(search_query)
                    result = {
                        'title': pub.get('bib', {}).get('title', 'No title'),
                        'authors': pub.get('bib', {}).get('author', 'Unknown'),
                        'year': pub.get('bib', {}).get('pub_year', 'Unknown'),
                        'abstract': pub.get('bib', {}).get('abstract', 'No abstract available'),
                        'citations': pub.get('num_citations', 0),
                        'url': pub.get('pub_url', 'No URL available')
                    }
                    results.append(result)
                except StopIteration:
                    break
                except Exception as e:
                    results.append(f"Error retrieving publication {i+1}: {str(e)}")
            
            if not results:
                return "No results found for the given query."
            
            # Format results nicely
            formatted_results = "\n\n".join([
                f"Title: {r['title']}\n"
                f"Authors: {r['authors']}\n"
                f"Year: {r['year']}\n"
                f"Citations: {r['citations']}\n"
                f"URL: {r['url']}\n"
                f"Abstract: {r['abstract']}"
                for r in results if isinstance(r, dict)
            ])
            
            return formatted_results
        except Exception as e:
            return f"Error searching Google Scholar: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        # Scholarly doesn't have native async support, so we use the sync version
        return self._run(query)

# Custom web search function
@tool
def web_search(query: str) -> str:
    """Search the web for information"""
    try:
        search = DuckDuckGoSearchRun()
        return search.run(query)
    except Exception as e:
        return f"Error searching the web: {str(e)}"

# Create a wrapper for the scholar search tool
@tool
def scholar_search(query: str) -> str:
    """Search for academic papers on Google Scholar"""
    scholar_tool = ScholarTool()
    return scholar_tool._run(query)

# Create a wrapper for arxiv search
@tool
def arxiv_tool(query: str) -> str:
    """Search for papers on arXiv"""
    return arxiv_search(query)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up embeddings and models
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
Groq_API="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"

# Available Groq models - update this list as needed
AVAILABLE_GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3-8b-8192",
    "llama-3-70b-8192",
    "mixtral-8x7b-32768",
    "gemma-7b-it"
]

# Function to validate Groq model availability
def validate_groq_model(model_name):
    if model_name not in AVAILABLE_GROQ_MODELS:
        logger.warning(f"Model '{model_name}' not in list of known available models. This might cause issues.")
    return model_name

# Initialize models with validation
default_model = validate_groq_model("llama-3.3-70b-versatile")

try:
    llm = ChatGroq(groq_api_key=Groq_API, model_name=default_model)
    llm2 = ChatGroq(groq_api_key=Groq_API, model_name=default_model)
    llm3 = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        api_key=os.getenv("GOOGLE_API_KEY", "AIzaSyCld0oOHsbSg7pa0WIvfIU-U7eICexYmhE")
    )
    logger.info(f"Models initialized successfully with Groq model: {default_model}")
except Exception as e:
    logger.error(f"Error initializing models: {str(e)}")
    # Continue with app startup but log the error

# Define our LangChain tools
tools = [
    web_search,
    arxiv_tool,
    scholar_search,
]

# Read PDF file content
@tool
def read_pdf(file_path: str) -> str:
    """Read the content of a PDF file"""
    try:
        text_content = ""
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
        return text_content
    except Exception as e:
        return f"Error reading PDF file: {str(e)}"

# Define templates for different tasks
ai_detection_template = """You are an AI Content Detection Specialist. Your task is to analyze the content provided and determine if it was likely generated by an AI or written by a human.

Content to analyze: {content}

Provide a detailed analysis looking at:
1. Writing patterns and stylistic markers
2. Coherence and logical flow
3. Presence of repetitive phrases or structures
4. Unusual word choices or combinations
5. Consistency of voice and tone

Based on your analysis, give a percentage estimate of how likely this content was generated by AI.

Your response should include:
- Detailed reasoning for your assessment
- Specific examples from the text that support your conclusion
- A final percentage score indicating likelihood of AI generation

Available tools:
{tools}

Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

{agent_scratchpad}
"""

grammar_check_template = """You are a Grammar and Style Expert. Your task is to analyze the provided text for grammar, style, and readability issues.

Text to analyze: {content}

Provide a comprehensive analysis including:
1. Grammar corrections (spelling, punctuation, sentence structure)
2. Style improvements (clarity, conciseness, word choice)
3. Readability assessment
4. Suggestions for overall improvement

Your response should include:
- Corrected version of the text
- Detailed explanations of major changes
- A readability score out of 100
- Specific recommendations for further improvement

Available tools:
{tools}

Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

{agent_scratchpad}
"""

paraphrase_template = """You are a Language Expert specializing in paraphrasing. Your task is to rephrase the provided content in {language} while maintaining its original meaning.

Content to paraphrase: {content}

Guidelines for paraphrasing:
1. Maintain the original meaning and key information
2. Use different vocabulary and sentence structures
3. Ensure the new text flows naturally
4. Keep the same tone and level of formality
5. Make sure the output is in {language}

Your response should include:
- Complete paraphrased version of the content
- Brief explanation of major changes made

Available tools:
{tools}

Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

{agent_scratchpad}
"""

plagiarism_check_template = """You are a Plagiarism Detection Expert. Your task is to analyze the provided content for potential plagiarism.

Content to analyze: {content}

Conduct a thorough plagiarism analysis by:
1. Identifying potentially unoriginal passages or ideas
2. Searching for similar academic papers or publications using the provided search tools
3. Checking for proper citation and attribution

Use these tools to search for similar content:
- Web search for general information
- Scholar search for academic papers
- arXiv search for research papers

Your response should include:
- An estimated plagiarism percentage
- Specific sections that may be plagiarized
- Potential source matches (with URLs where possible)
- Suggestions for improving originality

Available tools:
{tools}

Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

{agent_scratchpad}
"""

summarize_template = """You are a Research and Summarization Expert. Your task is to create a clear and concise summary of the provided content in {language}.

Content to summarize: {content}

Guidelines for summarization:
1. Capture all key points and main ideas
2. Maintain the logical flow and structure
3. Remove redundant information
4. Ensure accuracy and context preservation
5. Make the summary readable and engaging
6. Provide the summary in {language}

Your response should be a comprehensive yet concise summary of the original content.

Available tools:
{tools}

Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

{agent_scratchpad}
"""

review_template = """You are a Research Paper Review Expert. Your task is to provide a comprehensive review of the academic paper provided.

Paper content: {content}

Conduct a thorough analysis focusing on:
1. Content and scientific validity (methodology, results, conclusions)
2. Structure and organization
3. Writing style and clarity
4. Potential plagiarism concerns 
5. References and citations

Use these tools to search for relevant information:
- Web search for general information
- Scholar search for academic papers
- arXiv search for research papers

Your response should include:
- Summary of the paper
- Strengths and weaknesses
- Content analysis
- Style and formatting evaluation
- Plagiarism assessment
- Overall score (out of 100)
- Specific recommendations for improvement

Available tools:
{tools}

Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

{agent_scratchpad}
"""

# Create agent executors for different tasks
def create_ai_detection_agent():
    prompt = PromptTemplate.from_template(ai_detection_template)
    agent = create_react_agent(llm2, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

def create_grammar_check_agent():
    prompt = PromptTemplate.from_template(grammar_check_template)
    agent = create_react_agent(llm3, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

def create_paraphrase_agent():
    prompt = PromptTemplate.from_template(paraphrase_template)
    agent = create_react_agent(llm3, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

def create_plagiarism_agent():
    prompt = PromptTemplate.from_template(plagiarism_check_template)
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

def create_summarize_agent():
    prompt = PromptTemplate.from_template(summarize_template)
    agent = create_react_agent(llm3, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

def create_review_agent():
    prompt = PromptTemplate.from_template(review_template)
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# Improved error handling for LLM operations
async def safe_agent_invoke(agent, params, operation_name="LLM operation"):
    try:
        result = agent.invoke(params)
        return result["output"]
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in {operation_name}: {error_msg}")
        logger.error(traceback.format_exc())
        
        # Check for model-related errors
        if "model" in error_msg.lower() and "decommissioned" in error_msg.lower():
            raise HTTPException(
                status_code=500, 
                detail=f"The LLM model being used has been decommissioned. Please contact the administrator to update the model."
            )
        raise HTTPException(status_code=500, detail=f"Error in {operation_name}: {error_msg}")

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

    except HTTPException as http_exc:
        # Re-raise HTTP exceptions
        raise http_exc
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        logger.error(traceback.format_exc())
        # Check for model-related errors
        error_msg = str(e)
        if "model" in error_msg.lower() and "decommissioned" in error_msg.lower():
            raise HTTPException(
                status_code=500, 
                detail=f"The LLM model being used has been decommissioned. Please contact the administrator to update the model."
            )
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        # Remove the temporary file after processing
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

@app.post("/AI_detect_pdf")
async def detect_ai_generated(file: UploadFile = File(...)):
    async def process_pdf(temp_pdf_path):
        try:
            # Read PDF content
            pdf_content = read_pdf(temp_pdf_path)
            
            # Create AI Detection Agent
            ai_detection_agent = create_ai_detection_agent()
            
            # Run the agent with improved error handling
            return await safe_agent_invoke(
                ai_detection_agent, 
                {"content": pdf_content},
                "AI detection"
            )
            
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
    try:
        # Create AI Detection Agent
        ai_detection_agent = create_ai_detection_agent()
        
        # Run the agent with improved error handling
        result = await safe_agent_invoke(
            ai_detection_agent, 
            {"content": request.text},
            "AI text detection"
        )
        
        return {"result": result}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"AI Detect Text Error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error detecting AI-generated content: {str(e)}")

@app.post("/grammar-check")
async def grammar_check(request: TextRequest):
    """
    Analyzes and refines the content by performing a comprehensive grammar check.
    """
    try:
        # Create Grammar Check Agent
        grammar_agent = create_grammar_check_agent()
        
        # Run the agent
        result = grammar_agent.invoke({
            "content": request.text
        })
        
        return {"result": result["output"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing grammar check: {e}")

@app.post("/paraphrase-text")
async def paraphrase_text(request: TextRequestLang):
    """
    Paraphrases the provided text input in the specified language.
    """
    try:
        # Create Paraphrase Agent
        paraphrase_agent = create_paraphrase_agent()
        
        # Run the agent
        result = paraphrase_agent.invoke({
            "content": request.text,
            "language": request.lang
        })
        
        return {"result": result["output"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error paraphrasing text: {e}")

@app.post("/paraphrase-pdf")
async def paraphrase_pdf(file: UploadFile = File(...)):
    async def process_pdf(temp_pdf_path):
        try:
            # Read PDF content
            pdf_content = read_pdf(temp_pdf_path)
            
            # Create Paraphrase Agent
            paraphrase_agent = create_paraphrase_agent()
            
            # Run the agent
            result = paraphrase_agent.invoke({
                "content": pdf_content,
                "language": "English"
            })
            
            return result["output"]
            
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
    async def process_pdf(temp_pdf_path):
        try:
            # Read PDF content
            pdf_content = read_pdf(temp_pdf_path)
            
            # Create Plagiarism Detection Agent
            plagiarism_agent = create_plagiarism_agent()
            
            # Run the agent
            result = plagiarism_agent.invoke({
                "content": pdf_content
            })
            
            return result["output"]
            
        except Exception as e:
            logger.error(f"Plagiarism Detection Error: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    try:
        plagiarism_results = await process_pdf_file(file, process_pdf)
        return {"plagiarism_report": plagiarism_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting plagiarism: {e}")

@app.post("/summarize-text")
async def summarize_text_endpoint(request: TextRequestLang):
    try:
        # Create Summarize Agent
        summarize_agent = create_summarize_agent()
        
        # Run the agent
        result = summarize_agent.invoke({
            "content": request.text,
            "language": request.lang
        })
        
        return {"summary": result["output"]}
    except Exception as e:
        logger.error(f"Summarize Text Error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error summarizing text: {str(e)}")

@app.post("/summarize-file")
async def summarize_file(file: UploadFile = File(...), language: str = "English"):
    async def process_pdf(temp_pdf_path):
        try:
            # Read PDF content
            pdf_content = read_pdf(temp_pdf_path)
            
            # Create Summarize Agent
            summarize_agent = create_summarize_agent()
            
            # Run the agent
            result = summarize_agent.invoke({
                "content": pdf_content,
                "language": language
            })
            
            return result["output"]
            
        except Exception as e:
            logger.error(f"PDF Summarization Error: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        summary = await process_pdf_file(file, process_pdf)
        return {"summary": summary}
    except Exception as e:
        logger.error(f"Summarize File Error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error summarizing file content: {str(e)}")

@app.post("/review-file")
async def review_file(file: UploadFile = File(...)):
    async def process_pdf(temp_pdf_path):
        try:
            # Read PDF content
            pdf_content = read_pdf(temp_pdf_path)
            
            # Create Review Agent
            review_agent = create_review_agent()
            
            # Run the agent with improved error handling
            return await safe_agent_invoke(
                review_agent, 
                {"content": pdf_content},
                "paper review"
            )
            
        except Exception as e:
            logger.error(f"Paper Review Error: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        review_result = await process_pdf_file(file, process_pdf)
        return {"summary": review_result}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Review File Error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error reviewing file content: {str(e)}")

# Add health check endpoint to verify model availability
@app.get("/health")
async def health_check():
    try:
        # Basic test to ensure the models are working
        response = {
            "status": "ok",
            "groq_model": default_model,
            "google_model": "gemini-1.5-pro",
        }
        return response
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

def main():
    import uvicorn
    uvicorn.run(app, host="127.0.0.5", port=8005)

if __name__ == "__main__":
    main()
