export const formatResult = (result: string, type: 'plagiarism' | 'grammar' | 'paraphrase' | 'summary' | 'ai-detection' | 'paper-review'): string => {
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

const formatPlagiarismResult = (result: string): string => {
  return `# Plagiarism Detection Report

${result.split('\n').map(line => {
  if (line.includes('Plagiarism detected:')) {
    return `## ${line}\n`;
  }
  if (line.includes('Source:')) {
    return `> ${line}\n`;
  }
  return line;
}).join('\n')}`;
};

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

  let formattedResult = '# Paper Review Report\n\n';
  
  sections.forEach(section => {
    const regex = new RegExp(`${section}:?([\\s\\S]*?)(?=${sections.join('|')}|$)`);
    const match = result.match(regex);
    if (match && match[1].trim()) {
      formattedResult += `## ${section}\n\n${match[1].trim()}\n\n`;
    }
  });

  return formattedResult;
};

const formatGrammarResult = (result: string): string => {
  return `# Grammar Check Results

${result.split('\n').map(line => {
  if (line.includes('Error:')) {
    return `## Error Found\n${line.replace('Error:', '')}\n`;
  }
  if (line.includes('Suggestion:')) {
    return `> Suggestion: ${line.replace('Suggestion:', '')}\n`;
  }
  return line;
}).join('\n')}`;
};

const formatParaphraseResult = (result: string): string => {
  return `# Paraphrased Text

## Original Text
${result.split('Paraphrased version:')[0]}

## Paraphrased Version
${result.split('Paraphrased version:')[1] || ''}`;
};

const formatSummaryResult = (result: string): string => {
  return `# Text Summary

## Key Points
${result.split('\n').map(line => `- ${line}`).join('\n')}`;
};

const formatAIDetectionResult = (result: string): string => {
  return `# AI Content Detection Results

${result.split('\n').map(line => {
  if (line.includes('Confidence:')) {
    return `## Detection Confidence\n${line}\n`;
  }
  if (line.includes('Analysis:')) {
    return `### Detailed Analysis\n${line.replace('Analysis:', '')}\n`;
  }
  return line;
}).join('\n')}`;
};