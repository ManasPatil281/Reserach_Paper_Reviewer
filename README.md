# ScholarMate 🎓 - Research Paper Reviewer

**Advanced text processing and Paper reviewer powered by cutting-edge AI technology**

ScholarMate is a comprehensive web application that provides AI-powered text analysis tools for academic and research purposes. It offers plagiarism detection, grammar checking, text paraphrasing, summarization, AI content detection, and comprehensive paper reviewing capabilities.

## ✨ Features

- **🤖 AI Content Detection**: Detect AI-generated content with confidence scores
- **✍️ Grammar Check**: Professional grammar and style correction
- **🔄 Paraphrasing**: Rewrite content while maintaining meaning
- **🛑 Plagiarism Detection**: Comprehensive plagiarism detection with source matching
- **📌 Text Summarization**: Create concise summaries of long texts
- **📄 Paper Reviewer**: Get comprehensive academic paper reviews with detailed analysis

## 🚀 Technology Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **React Router** for navigation
- **React Markdown** for displaying formatted results
- **jsPDF** for PDF generation

### Backend
- **FastAPI** (Python) for API server
- **LangChain** for AI agent orchestration
- **Groq API** for fast LLM inference
- **Google Gemini** for advanced language processing
- **HuggingFace** embeddings for semantic search
- **Scholarly** for Google Scholar integration
- **ArXiv API** for research paper search

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- **Node.js** (v18 or higher)
- **Python** (v3.8 or higher)
- **npm** or **yarn** package manager
- **pip** for Python package management

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Reserach_Paper_Reviewer/project
```

### 2. Frontend Setup
```bash
# Install frontend dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 3. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install fastapi uvicorn langchain langchain-groq langchain-google-genai langchain-huggingface langchain-community langchain-text-splitters faiss-cpu python-dotenv aiofiles PyPDF2 requests scholarly python-multipart

# Create environment file (optional)
touch .env
```

### 4. Environment Variables
Create a `.env` file in the backend directory:
```env
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

**Note**: The application has default API keys configured for demonstration purposes, but it's recommended to use your own keys for production.

### 5. Start the Backend Server
```bash
# From the backend directory
python main.py
```

The backend API will be available at `http://127.0.0.5:8005`

## 🎯 Usage Guide

### Text Processing
1. **Navigate** to any feature page (AI Detection, Grammar Check, etc.)
2. **Choose input method**: Text input or file upload
3. **Enter your content** or upload a PDF file
4. **Select language** (if applicable)
5. **Click process** and wait for results
6. **Download PDF reports** where available

### API Endpoints

#### AI Content Detection
- `POST /AI_detect_text` - Detect AI content in text
- `POST /AI_detect_pdf` - Detect AI content in PDF files

#### Grammar & Style
- `POST /grammar-check` - Check grammar and style

#### Text Paraphrasing
- `POST /paraphrase-text` - Paraphrase text input
- `POST /paraphrase-pdf` - Paraphrase PDF content

#### Plagiarism Detection
- `POST /detect-plagiarism` - Detect plagiarism in PDF files

#### Text Summarization
- `POST /summarize-text` - Summarize text input
- `POST /summarize-file` - Summarize PDF files

#### Paper Review
- `POST /review-file` - Comprehensive paper review

#### Health Check
- `GET /health` - Check API server status

## 📚 API Documentation

### Request Examples

#### Text Analysis
```javascript
// AI Detection
const response = await fetch('http://127.0.0.5:8005/AI_detect_text', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: "Your text here" })
});

// Grammar Check
const response = await fetch('http://127.0.0.5:8005/grammar-check', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: "Your text here" })
});
```

#### File Upload
```javascript
// PDF Analysis
const formData = new FormData();
formData.append('file', pdfFile);

const response = await fetch('http://127.0.0.5:8005/review-file', {
  method: 'POST',
  body: formData
});
```

## 🔧 Configuration

### Supported Languages
- English (default)
- Spanish
- French
- German
- Italian
- Portuguese
- And more...

### File Support
- **PDF files** (.pdf) up to 10MB
- **Text input** up to 50,000 characters

## 🚨 Troubleshooting

### Common Issues

1. **Backend not starting**
   - Check if all Python dependencies are installed
   - Verify API keys are configured correctly
   - Ensure port 8005 is not in use

2. **Frontend connection issues**
   - Verify backend is running on `http://127.0.0.5:8005`
   - Check CORS settings in backend
   - Clear browser cache

3. **API errors**
   - Check server logs for detailed error messages
   - Verify file formats and sizes
   - Ensure API keys have sufficient quota

4. **Model errors**
   - Update to latest Groq model versions
   - Check model availability in your region
   - Try alternative model configurations

### Performance Tips
- Use smaller file sizes for faster processing
- Process large documents in chunks
- Consider using text input for simple operations

## 📁 Project Structure

```
project/
├── src/                    # Frontend source code
│   ├── components/         # React components
│   ├── pages/             # Page components
│   ├── utils/             # Utility functions
│   └── App.tsx            # Main application
├── backend/               # Backend API server
│   └── main.py           # FastAPI application
├── public/               # Static assets
├── package.json          # Frontend dependencies
└── README.md            # Project documentation
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Team

**Project Made By:**
- **Manas Patil**
- **Ayush Attarde** 
- **Soham Kamathi**
- **Gaurav Kuthwal**
- **Ashutoshkumar Tripathi**


## 📞 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the troubleshooting section

---
