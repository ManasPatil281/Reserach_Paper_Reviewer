import React, { useState } from 'react';
import { AlertTriangle } from 'lucide-react';
import FileUpload from '../components/FileUpload';
import MarkdownResult from '../components/MarkdownResult';

export default function AIDetection() {
  const [text, setText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'text' | 'file'>('text');
  
  const API_BASE_URL = 'https://reserach-paper-reviewer.onrender.com/ai-detection';
  
  const handleProcess = async () => {
    setLoading(true);
    try {
      if (activeTab === 'text') {
        const response = await fetch(`${API_BASE_URL}/AI_detect_text`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text }), // Fix: Properly structure the request body
        });
        const data = await response.json();
        setResult(data.result || '');
      } else if (file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE_URL}/AI_detect_pdf`, {
          method: 'POST',
          body: formData,
        });
        const data = await response.json();
        setResult(data.result || '');
      }
    } catch (error) {
      setResult('Error processing request. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <AlertTriangle className="w-16 h-16 text-indigo-600 mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-gray-800">AI Content Detection</h1>
        <p className="text-gray-600 mt-2">Detect AI-generated content with confidence scores</p>
      </div>
      
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex mb-6 space-x-4">
          <button
            onClick={() => setActiveTab('text')}
            className={`flex-1 py-2 px-4 rounded-lg ${
              activeTab === 'text'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Text Input
          </button>
          <button
            onClick={() => setActiveTab('file')}
            className={`flex-1 py-2 px-4 rounded-lg ${
              activeTab === 'file'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            File Upload
          </button>
        </div>
        
        <div className="mb-6">
          {activeTab === 'text' ? (
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter your text here..."
              className="w-full h-40 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          ) : (
            <FileUpload file={file} setFile={setFile} />
          )}
        </div>

        <button
          onClick={handleProcess}
          disabled={loading || (activeTab === 'text' && !text) || (activeTab === 'file' && !file)}
          className={`w-full py-3 rounded-lg ${
            loading
              ? 'bg-gray-300 cursor-not-allowed'
              : 'bg-indigo-600 hover:bg-indigo-700 text-white'
          }`}
        >
          {loading ? 'Processing...' : 'Detect AI Content'}
        </button>

        {result && (
          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-4">Results:</h3>
            <MarkdownResult content={result} />
          </div>
        )}
      </div>
    </div>
  );
}
