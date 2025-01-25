import { jsPDF } from 'jspdf';
import 'jspdf-autotable';

declare module 'jspdf' {
  interface jsPDF {
    autoTable: (options: any) => jsPDF;
  }
}

export const generatePDF = (title: string, content: string, sections?: { title: string; content: string }[]) => {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  const margin = 20;
  const contentWidth = pageWidth - 2 * margin;

  // Add title
  doc.setFontSize(20);
  doc.setTextColor(66, 66, 66);
  const titleLines = doc.splitTextToSize(title, contentWidth);
  doc.text(titleLines, margin, 20);

  let yPosition = 20 + (titleLines.length * 10);

  // Add date
  doc.setFontSize(10);
  doc.setTextColor(128, 128, 128);
  doc.text(`Generated on: ${new Date().toLocaleDateString()}`, margin, yPosition);
  yPosition += 10;

  if (sections) {
    // For structured content (Paper Review)
    sections.forEach(section => {
      if (!section.content) return;

      // Section title
      doc.setFontSize(14);
      doc.setTextColor(66, 66, 66);
      doc.text(section.title, margin, yPosition);
      yPosition += 10;

      // Section content
      doc.setFontSize(12);
      doc.setTextColor(96, 96, 96);
      const contentLines = doc.splitTextToSize(section.content.trim(), contentWidth);
      
      if (yPosition + (contentLines.length * 7) > doc.internal.pageSize.getHeight() - margin) {
        doc.addPage();
        yPosition = 20;
      }
      
      doc.text(contentLines, margin, yPosition);
      yPosition += (contentLines.length * 7) + 10;
    });
  } else {
    // For unstructured content (Plagiarism Check)
    doc.setFontSize(12);
    doc.setTextColor(96, 96, 96);
    const contentLines = doc.splitTextToSize(content, contentWidth);
    doc.text(contentLines, margin, yPosition);
  }

  return doc;
};