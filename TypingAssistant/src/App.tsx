import { useEffect, useRef, useState } from 'react';
import Quill from 'quill';
import { Document, Page, pdfjs } from 'react-pdf';
import 'quill/dist/quill.snow.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import './app.css';

// Update PDF.js worker configuration
pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

const App = () => {
  const editorRef = useRef<Quill | null>(null);
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [pdfFile, setPdfFile] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!editorRef.current) {
      const toolbarOptions = [
        [{ font: [] }],
        [{ header: [1, 2, 3, 4] }],
        ["bold", "italic", "underline", "strike"],
        [{ color: [] }, { background: [] }],
        [{ list: "ordered" }, { list: "bullet" }, { list: "check" }],
        ["blockquote", "code-block"],
        ["link", "image", "video"],
        [{ align: [] }]
      ];

      editorRef.current = new Quill("#editor-container", {
        theme: "snow",
        modules: {
          toolbar: toolbarOptions
        }
      });
    }
  }, []);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    setError(null);
    setIsLoading(true);
    
    if (file) {
      try {
        const fileUrl = URL.createObjectURL(file);
        setPdfFile(fileUrl);
        setPageNumber(1);
      } catch (err) {
        setError('Error loading PDF file');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="wrapper">
      <div className="container">
        <div className="editor-section">
          <div id="editor-container"></div>
          <button className="save-button btn">Save</button>
        </div>
        <div className="pdf-section">
          <input 
            type="file" 
            accept=".pdf,application/pdf"
            onChange={handleFileChange}
            className="file-input"
          />
          {error && <div className="error-message">{error}</div>}
          {isLoading && <div>Loading PDF...</div>}
          {pdfFile && (
            <Document 
              file={pdfFile}
              onLoadSuccess={({ numPages }) => setNumPages(numPages)}
              onLoadError={(err) => {
                console.error(err);
                setError('Error loading PDF');
              }}
              loading={<div>Loading PDF...</div>}
            >
              <Page 
                pageNumber={pageNumber}
                renderTextLayer={true}
                renderAnnotationLayer={true}
              />
            </Document>
          )}
          {numPages > 0 && (
            <div className="pdf-controls">
              <button 
                className="btn"
                onClick={() => setPageNumber(p => Math.max(1, p - 1))}
                disabled={pageNumber <= 1}
              >
                Previous
              </button>
              <span>Page {pageNumber} of {numPages}</span>
              <button 
                className="btn"
                onClick={() => setPageNumber(p => Math.min(numPages, p + 1))}
                disabled={pageNumber >= numPages}
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
