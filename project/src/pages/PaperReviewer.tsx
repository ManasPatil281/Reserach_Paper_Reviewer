import React, { useState } from 'react';
import { ScrollText, CheckCircle2, AlertCircle, Download } from 'lucide-react';
import FileUpload from '../components/FileUpload';
import MarkdownResult from '../components/MarkdownResult'; // Import MarkdownResult component
import { generatePDF } from '../utils/pdfGenerator';
import { formatResult } from '../utils/formatResult'; // Ensure formatting for markdown

export default function PaperReviewer() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const API_BASE_URL = 'https://reserach-paper-reviewer.onrender.com';

  const handleProcess = async () => {
    if (!file) return;

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/review-file`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setResult(data.summary || '');
    } catch (error) {
      setResult('Error processing request. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const parseReviewSections = (review: string) => {
    const sections = [
      'Abstract Analysis',
      'Introduction and Objectives',
      'Literature Review',
      'Methodology',
      'Results and Analysis',
      'Discussion and Interpretation',
      'Citations and References',
      'Plagiarism Check',
      'Suggestions for Improvement',
      'Strengths and Originality',
      'Formatting and Presentation',
      'Summary of Review',
    ];

    return sections.map((section) => {
      const sectionRegex = new RegExp(`${section}:?([\\s\\S]*?)(?=${sections.join('|')}|$)`);
      const match = review.match(sectionRegex);
      return {
        title: section,
        content: match ? match[1].trim() : '',
      };
    });
  };

  const handleDownload = () => {
    if (!result) return;

    const sections = parseReviewSections(result);
    const doc = generatePDF('Paper Review Report', '', sections);
    doc.save('paper-review-report.pdf');
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <ScrollText className="w-16 h-16 text-indigo-600 mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-gray-800">Paper Reviewer</h1>
        <p className="text-gray-600 mt-2">Get comprehensive academic paper reviews with detailed analysis</p>
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
          } transition-colors duration-300`}
        >
          {loading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2" />
              Analyzing Paper...
            </div>
          ) : (
            'Review Paper'
          )}
        </button>

        {result && (
          <div className="mt-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-800">Review Report</h2>
              <button
                onClick={handleDownload}
                className="flex items-center px-4 py-2 text-sm text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors duration-300"
              >
                <Download className="w-4 h-4 mr-2" />
                Download PDF
              </button>
            </div>
            <div className="p-6 bg-white rounded-lg shadow-sm">
              <MarkdownResult content={formatResult(result, 'review')} /> {/* Display Markdown */}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
