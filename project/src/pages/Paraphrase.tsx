import React, { useState } from 'react';
import { Type } from 'lucide-react';
import FileUpload from '../components/FileUpload';
import ProcessingOptions from '../components/ProcessingOptions';
import MarkdownResult from '../components/MarkdownResult';
import { formatResult } from '../utils/formatResult';

export default function Paraphrase() {
  const [text, setText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'text' | 'file'>('text');
  const [language, setLanguage] = useState('English');

  const API_BASE_URL = 'https://us-central1-scholar-mate-449005.cloudfunctions.net/ai-detection';

  const handleProcess = async () => {
    setLoading(true);
    try {
      if (activeTab === 'text') {
        const response = await fetch(`${API_BASE_URL}/paraphrase-text`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            text, 
            lang: language // Fix: Use correct parameter name matching backend
          }),
        });
        const data = await response.json();
        setResult(data.result || '');
      }else if (file) {
        const formData = new FormData();
        formData.append('lang', language);
        formData.append('file', file);
         // Ensure language is correctly appended
      
        const response = await fetch(`${API_BASE_URL}/paraphrase-pdf`, {
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
        <Type className="w-16 h-16 text-indigo-600 mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-gray-800">Paraphrase</h1>
        <p className="text-gray-600 mt-2">Rewrite content while maintaining meaning</p>
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

        <ProcessingOptions
          language={language}
          setLanguage={setLanguage}
        />

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
          {loading ? 'Processing...' : 'Paraphrase'}
        </button>

        {result && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Results:</h3>
            <MarkdownResult content={formatResult(result, 'paraphrase')} />
          </div>
        )}
      </div>
    </div>
  );
}
