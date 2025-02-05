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
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 20;
  const contentWidth = pageWidth - 2 * margin;
  let yPosition = 30;

  // ✅ **Styled Title Section**
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(20);
  doc.setTextColor(255, 255, 255);
  doc.setFillColor(33, 150, 243); // Blue background
  doc.rect(margin, yPosition - 10, contentWidth, 15, 'F'); // Background box
  doc.text(title, pageWidth / 2, yPosition, { align: 'center' });
  yPosition += 20;

  // ✅ **Title Separator**
  doc.setDrawColor(200, 200, 200);
  doc.line(margin, yPosition, pageWidth - margin, yPosition);
  yPosition += 10;

  // ✅ **Date**
  doc.setFont('helvetica', 'italic');
  doc.setFontSize(10);
  doc.setTextColor(100, 100, 100);
  doc.text(`Generated on: ${new Date().toLocaleDateString()}`, margin, yPosition);
  yPosition += 15;

  // 🔄 **New Page Handler**
  const addNewPage = () => {
    doc.addPage();
    yPosition = 20;
  };

  // ✅ **Content Processing with Auto-Pagination**
  const addContent = (text: string, fontSize = 12, bold = false) => {
    doc.setFont('helvetica', bold ? 'bold' : 'normal');
    doc.setFontSize(fontSize);
    doc.setTextColor(80, 80, 80);

    const lines = doc.splitTextToSize(text.trim(), contentWidth);
    for (let i = 0; i < lines.length; i++) {
      if (yPosition + 10 > pageHeight - margin) addNewPage();
      doc.text(lines[i], margin, yPosition);
      yPosition += 7;
    }
    yPosition += 5; // Extra spacing after paragraphs
  };

  if (sections) {
    // ✅ **Structured Content with Sections**
    sections.forEach(section => {
      if (!section.content) return;
      if (yPosition + 20 > pageHeight - margin) addNewPage();

      // Section Title
      addContent(section.title, 16, true);
      addContent(section.content);
    });
  } else {
    // ✅ **Unstructured Content**
    addContent(content);
  }

  // ✅ **Page Numbering**
  const totalPages = doc.internal.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    doc.setFontSize(10);
    doc.setTextColor(150, 150, 150);
    doc.text(`Page ${i} of ${totalPages}`, pageWidth - margin, pageHeight - 10, { align: 'right' });
  }

  return doc;
};
