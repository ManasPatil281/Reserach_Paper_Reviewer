Abstract—This paper presents Scholarmate, a prototype web
application. We developed a system to explore academic doc-
ument analysis. Our system integrates multiple AI services
including language models and similarity search to provide a
unified interface for document evaluation tasks. The application
uses a React frontend with a FastAPI backend, in corporating
services like Groq’s LLaMA access, Google’s Gemini API, and
FAISS [4] for vector similarity search. We encountered numerous
technical challenges during the development process, including
API rate limiting, context window constraints, and integration
complexity. Our preliminary testing with documents from our
coursework and publicly available papers suggests the approach
has potential, though significant limitations remain. The system
currently handles basic document analysis tasks but requires
substantial refinement for production use. Key technical decisions
include using sentence transformers for text embeddings, imple-
menting async processing for better performance, and deploying
on cloud platforms for scalability. However, we acknowledge that
comprehensive evaluation and real-world testing are needed to
validate the system’s effective ness. This system served primarily
as a learning exercise in modern web development and AI service
integration.
Index Terms—Academic integrity, document analysis, language
models, web application, prototype system, API integration
