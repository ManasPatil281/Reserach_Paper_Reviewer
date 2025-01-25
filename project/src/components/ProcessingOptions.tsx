import React from 'react';

interface ProcessingOptionsProps {
  mode: string;
  language: string;
  setMode: (mode: string) => void;
  setLanguage: (language: string) => void;
}

export default function ProcessingOptions({
  mode,
  language,
  setMode,
  setLanguage,
}: ProcessingOptionsProps) {
  return (
    <div className="grid grid-cols-2 gap-4 mb-6">
      <div className="relative">
        <label className="block text-sm font-medium text-gray-700 mb-1">Processing Mode</label>
        <select
          value={mode}
          onChange={(e) => setMode(e.target.value)}
          className="w-full p-2.5 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-300 appearance-none cursor-pointer hover:border-indigo-300"
        >
          <option value="standard">Standard Mode</option>
          <option value="academic">Academic Mode</option>
          <option value="creative">Creative Mode</option>
          <option value="business">Business Mode</option>
        </select>
        <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none text-gray-500">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      <div className="relative">
        <label className="block text-sm font-medium text-gray-700 mb-1">Language</label>
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="w-full p-2.5 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-300 appearance-none cursor-pointer hover:border-indigo-300"
        >
          <option value="English">English</option>
          <option value="Spanish">Spanish</option>
          <option value="French">French</option>
          <option value="German">German</option>
        </select>
        <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none text-gray-500">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
    </div>
  );
}