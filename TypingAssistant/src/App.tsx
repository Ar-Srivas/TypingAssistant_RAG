import { useEffect, useRef, useState } from 'react';
import Quill from 'quill';
import { Document, Page, pdfjs } from 'react-pdf';
import 'quill/dist/quill.snow.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import './app.css';
import debounce from 'lodash.debounce';

pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

const App = () => {
  const editorRef = useRef<Quill | null>(null);
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [pdfFile, setPdfFile] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);

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

      editorRef.current.on('text-change', debounce(handleTextChange, 500));
    }
  }, []);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    setError(null);
    setIsLoading(true);

    if (file) {
      try {
        const fileUrl = URL.createObjectURL(file);
        setPdfFile(fileUrl);
        setPageNumber(1);

        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('http://127.0.0.1:5000/upload_pdf', {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          throw new Error('Error uploading PDF file');
        }

      } catch (err) {
        setError('Error uploading PDF file');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleTextChange = async () => {
    if (!editorRef.current) return;

    const text = editorRef.current.getText();
    const lastChar = text.slice(-2, -1); // Check the second last character

    if (lastChar === ':') {
      const query = text.slice(0, -2).trim(); // Remove the last two characters
      try {
        const response = await fetch('http://127.0.0.1:5000/get_suggestion', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ query })
        });

        const data = await response.json();

        if (data.suggestion) {
          setSuggestions([data.suggestion]);
        }
      } catch (err) {
        console.error('Error in handleTextChange:', err);
        setError('Failed to get suggestion');
      }
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    if (editorRef.current) {
      const insertPosition = editorRef.current.getLength() - 1;
      editorRef.current.insertText(insertPosition, ` ${suggestion}`);
      setSuggestions([]);
    }
  };

  return (
    <div className="wrapper">
      <div className="container">
        <div className="editor-section">
          <div id="editor-container"></div>
          <button className="save-button btn">Save</button>
          {suggestions.length > 0 && (
            <div className="suggestion-dropdown">
              {suggestions.map((suggestion, index) => (
                <div
                  key={index}
                  className="suggestion-item"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion}
                </div>
              ))}
            </div>
          )}
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
