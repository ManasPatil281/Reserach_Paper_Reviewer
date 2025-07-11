import React, { useState } from 'react';
import { CheckCircle } from 'lucide-react';
import MarkdownResult from '../components/MarkdownResult'; // Assuming you have a MarkdownResult component.

export default function GrammarCheck() {
  const [text, setText] = useState('');
  const [result, setResult] = useState<string>('');
  const [loading, setLoading] = useState(false);


  const API_BASE_URL = 'https://reserach-paper-reviewer.onrender.com';

  const handleProcess = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/grammar-check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }), // Pass user input
      });
  
      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }
  
      const data = await response.json();
      setResult(data.result || 'No corrections found.');
    } catch (error) {
      setResult('Error processing request. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <CheckCircle className="w-16 h-16 text-indigo-600 mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-gray-800">Grammar Check</h1>
        <p className="text-gray-600 mt-2">Professional grammar and style correction</p>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6">
      

        <div className="mb-6">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter your text here..."
            className="w-full h-40 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>

        <button
          onClick={handleProcess}
          disabled={loading || !text}
          className={`w-full py-3 rounded-lg ${
            loading || !text
              ? 'bg-gray-300 cursor-not-allowed'
              : 'bg-indigo-600 hover:bg-indigo-700 text-white'
          }`}
        >
          {loading ? 'Processing...' : 'Check Grammar'}
        </button>

        {result && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Results:</h3>
            <MarkdownResult content={result} />
          </div>
        )}
      </div>
    </div>
  );
}
