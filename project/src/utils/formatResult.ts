export const formatResult = (
  result: string,
  type: 'plagiarism' | 'grammar' | 'paraphrase' | 'summary' | 'ai-detection' | 'paper-review'
): string => {
  if (!result.trim()) return `# ${type.replace('-', ' ').toUpperCase()} Report\n\n*No data available.*`;

  switch (type) {
    case 'plagiarism':
      return formatPlagiarismResult(result);
    case 'paper-review':
      return formatPaperReviewResult(result);
    case 'grammar':
      return formatGrammarResult(result);
    case 'paraphrase':
      return formatParaphraseResult(result);
    case 'summary':
      return formatSummaryResult(result);
    case 'ai-detection':
      return formatAIDetectionResult(result);
    default:
      return result;
  }
};

// ✅ **Plagiarism Formatting**
const formatPlagiarismResult = (result: string): string => {
  return `# 🛑 Plagiarism Detection Report

${result
  .split('\n')
  .map(line => {
    if (line.includes('Plagiarism detected:')) return `## 🚨 ${line}\n`;
    if (line.includes('Source:')) return `> 📌 ${line}\n`;
    return line;
  })
  .join('\n')}`;
};

// ✅ **Paper Review Formatting**
const formatPaperReviewResult = (result: string): string => {
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
    'Summary of Review'
  ];

  let formattedResult = '# 📄 Paper Review Report\n\n';

  sections.forEach(section => {
    const regex = new RegExp(`${section}:?([\\s\\S]*?)(?=${sections.join('|')}|$)`);
    const match = result.match(regex);
    if (match && match[1].trim()) {
      formattedResult += `## 🔹 ${section}\n\n${match[1].trim()}\n\n`;
    }
  });

  return formattedResult;
};

// ✅ **Grammar Check Formatting**
const formatGrammarResult = (result: string): string => {
  return `# ✍️ Grammar Check Results

${result
  .split('\n')
  .map(line => {
    if (line.includes('Error:')) return `## ❌ Error Found\n${line.replace('Error:', '').trim()}\n`;
    if (line.includes('Suggestion:')) return `> 💡 Suggestion: ${line.replace('Suggestion:', '').trim()}\n`;
    return line;
  })
  .join('\n')}`;
};

// ✅ **Paraphrased Text Formatting**
const formatParaphraseResult = (result: string): string => {
  const parts = result.split('Paraphrased version:');
  return `# 🔄 Paraphrased Text\n\n## 🔹 Original Text\n${parts[0].trim() || '*No original text provided.*'}`;
};

// ✅ **Summary Formatting**
const formatSummaryResult = (result: string): string => {
  return `# 📌 Text Summary

## 🔹 Key Points
${result
  .split('\n')
  .map(line => (line.trim() ? `- ${line.trim()}` : ''))
  .join('\n')}`;
};

// ✅ **AI Content Detection Formatting**
const formatAIDetectionResult = (result: string): string => {
  return `# 🤖 AI Content Detection Results

${result
  .split('\n')
  .map(line => {
    if (line.includes('Confidence:')) return `## 🎯 Detection Confidence\n${line.trim()}\n`;
    if (line.includes('Analysis:')) return `### 📊 Detailed Analysis\n${line.replace('Analysis:', '').trim()}\n`;
    return line;
  })
  .join('\n')}`;
};
