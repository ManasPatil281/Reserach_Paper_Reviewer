import React, { useState } from 'react';
import { FileSearch, Download } from 'lucide-react';
import FileUpload from '../components/FileUpload';
import { generatePDF } from '../utils/pdfGenerator';
import MarkdownResult from '../components/MarkdownResult';
import { formatResult } from '../utils/formatResult';

export default function PlagiarismCheck() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const API_BASE_URL = 'https://ai-research-paper-backend.onrender.com';

  const handleProcess = async () => {
    if (!file) return;

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(`${API_BASE_URL}/detect-plagiarism`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setResult(data.plagiarism_report || '');
    } catch (error) {
      setResult('Error processing request. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!result) return;
    const doc = generatePDF('Plagiarism Detection Report', result);
    doc.save('plagiarism-report.pdf');
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <FileSearch className="w-16 h-16 text-indigo-600 mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-gray-800">Plagiarism Check</h1>
        <p className="text-gray-600 mt-2">Comprehensive plagiarism detection</p>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="mb-6">
          <FileUpload file={file} setFile={setFile} />
        </div>

        <button
          onClick={handleProcess}
          disabled={loading || !file}
          className={`w-full py-3 rounded-lg ${
            loading || !file
              ? 'bg-gray-300 cursor-not-allowed'
              : 'bg-indigo-600 hover:bg-indigo-700 text-white'
          }`}
        >
          {loading ? 'Processing...' : 'Check Plagiarism'}
        </button>

        {result && (
          <div className="mt-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Plagiarism Report:</h3>
              <button
                onClick={handleDownload}
                className="flex items-center px-4 py-2 text-sm text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors duration-300"
              >
                <Download className="w-4 h-4 mr-2" />
                Download PDF
              </button>
            </div>
            <div className="p-6 bg-white rounded-lg shadow-sm">
              <MarkdownResult content={formatResult(result, 'plagiarism')} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
