import React from 'react';
import { Upload } from 'lucide-react';

interface FileUploadProps {
  file: File | null;
  setFile: (file: File | null) => void;
}

export default function FileUpload({ file, setFile }: FileUploadProps) {
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile?.type === 'application/pdf') {
      setFile(droppedFile);
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      className="border-2 border-dashed border-indigo-300 rounded-lg p-8 text-center transition-all duration-300 hover:border-indigo-500 bg-gradient-to-br from-indigo-50/50 to-purple-50/50"
    >
      <input
        type="file"
        accept=".pdf"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
        className="hidden"
        id="file-upload"
      />
      <label
        htmlFor="file-upload"
        className="cursor-pointer flex flex-col items-center group"
      >
        <div className="w-16 h-16 mb-4 rounded-full bg-indigo-100 flex items-center justify-center group-hover:bg-indigo-200 transition-all duration-300">
          <Upload className="w-8 h-8 text-indigo-600 group-hover:scale-110 transition-transform duration-300" />
        </div>
        <span className="text-lg font-medium text-gray-700 mb-2">
          {file ? file.name : 'Drop your file here or click to upload'}
        </span>
        <span className="text-sm text-gray-500">PDF files only</span>
      </label>
    </div>
  );
}