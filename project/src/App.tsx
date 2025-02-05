import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { FileText, AlertTriangle, CheckCircle, Type, FileSearch, FileStack, Sparkles, ScrollText, Moon, Sun } from 'lucide-react';
import AIDetection from './pages/AIDetection';
import GrammarCheck from './pages/GrammarCheck';
import Paraphrase from './pages/Paraphrase';
import PlagiarismCheck from './pages/PlagiarismCheck';
import Summarize from './pages/Summarize';
import PaperReviewer from './pages/PaperReviewer';



const features = [
  { icon: AlertTriangle, name: 'AI Detection', path: '/ai-detection', description: 'Detect AI-generated content with confidence scores', image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?q=80&w=800&auto=format&fit=crop' },
  { icon: CheckCircle, name: 'Grammar Check', path: '/grammar-check', description: 'Professional grammar and style correction', image: 'https://images.unsplash.com/photo-1455390582262-044cdead277a?q=80&w=800&auto=format&fit=crop' },
  { icon: Type, name: 'Paraphrase', path: '/paraphrase', description: 'Rewrite content while maintaining meaning', image: 'https://images.unsplash.com/photo-1456324504439-367cee3b3c32?q=80&w=800&auto=format&fit=crop' },
  { icon: FileSearch, name: 'Plagiarism Check', path: '/plagiarism-check', description: 'Comprehensive plagiarism detection', image: 'https://images.unsplash.com/photo-1516414447565-b14be0adf13e?q=80&w=800&auto=format&fit=crop' },
  { icon: FileStack, name: 'Summarize', path: '/summarize', description: 'Create concise summaries of long texts', image: 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?q=80&w=800&auto=format&fit=crop' },
  { icon: ScrollText, name: 'Paper Reviewer', path: '/paper-reviewer', description: 'Get comprehensive academic paper reviews', image: 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?q=80&w=800&auto=format&fit=crop' },
];

function App() {
 
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-white to-purple-100">
        <nav className="bg-white/80 backdrop-blur-md shadow-md sticky top-0 z-50">
          <div className="container mx-auto px-4">
            <div className="flex items-center justify-between h-16">
              <Link to="/" className="flex items-center space-x-2 group">
                <Sparkles className="w-8 h-8 text-indigo-600 transition-transform group-hover:scale-110 duration-300" />
                <span className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">ScholarMate</span>
              </Link>
              <div className="hidden md:flex space-x-1">
                {features.map((feature) => (
                  <Link
                    key={feature.path}
                    to={feature.path}
                    className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-indigo-600 hover:bg-indigo-50 transition-all duration-300"
                  >
                    <feature.icon className="w-4 h-4 mr-1" />
                    {feature.name}
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </nav>

        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/ai-detection" element={<AIDetection />} />
            <Route path="/grammar-check" element={<GrammarCheck />} />
            <Route path="/paraphrase" element={<Paraphrase />} />
            <Route path="/plagiarism-check" element={<PlagiarismCheck />} />
            <Route path="/summarize" element={<Summarize />} />
            <Route path="/paper-reviewer" element={<PaperReviewer />} />
          </Routes>
          
        </main>
        <footer className="bg-white/80 backdrop-blur-md shadow-md py-6">
          <div className="container mx-auto px-4 text-center">
            <p className="text-gray-700">
              Project Made By: 
              <span className="font-semibold text-indigo-600 ml-2">
                Manas Patil, Ayush Attarde, Soham Kamathi, 
                Gaurav Kuthwal, Ashutoshkumar Tripathi
              </span>
            </p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

function HomePage() {
  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-16 relative overflow-hidden rounded-3xl bg-white shadow-xl p-8">
        <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/10 to-purple-500/10" />
        <div className="relative">
          <div className="flex items-center justify-center mb-6">
            <Sparkles className="w-20 h-20 text-indigo-600 animate-pulse" />
            <h1 className="text-6xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent ml-4">
            ScholarMate🎓
            </h1>
          </div>
          <p className="text-2xl text-gray-600 max-w-3xl mx-auto mb-8">
            Advanced text processing and Paper reviewer powered by cutting-edge AI technology
          </p>
          <div className="flex justify-center space-x-4">
            <Link
              to="/ai-detection"
              className="px-8 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              Get Started
            </Link>
            <a
              href="#features"
              className="px-8 py-3 bg-white text-indigo-600 rounded-lg border-2 border-indigo-600 hover:bg-indigo-50 transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              Learn More
            </a>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div id="features" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {features.map((feature) => (
          <Link
            key={feature.path}
            to={feature.path}
            className="group relative overflow-hidden rounded-xl shadow-lg hover:shadow-xl transition-all duration-500 transform hover:-translate-y-1"
          >
            <div className="absolute inset-0">
              <img
                src={feature.image}
                alt={feature.name}
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-black/20" />
            </div>
            <div className="relative p-8 h-full min-h-[320px] flex flex-col justify-end text-white">
              <div className="mb-4">
                <feature.icon className="w-12 h-12 text-indigo-400 group-hover:text-indigo-300 transition-transform duration-500 group-hover:scale-110" />
              </div>
              <h2 className="text-2xl font-bold mb-2">{feature.name}</h2>
              <p className="text-gray-200">{feature.description}</p>
            </div>
          </Link>
        ))}
      </div>

      {/* Benefits Section */}
      <div className="mt-16 bg-white rounded-3xl shadow-xl p-8">
        <h2 className="text-3xl font-bold text-center mb-12 bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
          Why Choose Our ScholarMate?
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[
            {
              title: 'Advanced AI Technology',
              description: 'Powered by state-of-the-art language models for accurate results',
              icon: '🤖',
            },
            {
              title: 'Multiple Languages',
              description: 'Support for various languages and writing styles',
              icon: '🌍',
            },
            {
              title: 'Secure & Private',
              description: 'No login required and your data is never stored',
              icon: '🔒',
            },
            {
              title: 'Fast Processing',
              description: 'Review your  Papers in seconds with high accuracy',
              icon: '⚡',
            },
            {
              title: 'Easy to Use',
              description: 'Intuitive interface designed for the best user experience',
              icon: '👌',
            },
            {
              title: '24/7 Availability',
              description: 'Access our services anytime, anywhere',
              icon: '🌐',
            },
          ].map((benefit, index) => (
            <div
              key={index}
              className="p-6 rounded-xl bg-gradient-to-br from-indigo-50 to-purple-50 hover:from-indigo-100 hover:to-purple-100 transition-all duration-300"
            >
              <div className="text-4xl mb-4">{benefit.icon}</div>
              <h3 className="text-xl font-semibold mb-2 text-gray-800">{benefit.title}</h3>
              <p className="text-gray-600">{benefit.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
