import { useEffect, useRef } from 'react';
import Quill from 'quill';
import 'quill/dist/quill.snow.css';
import './app.css';

const App = () => {
  const editorRef = useRef<Quill | null>(null);

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
        [{ align: [] }],
      ];

      editorRef.current = new Quill("#editor-container", {
        theme: "snow",
        modules: {
          toolbar: toolbarOptions,
        },
      });
    }
  }, []);

  return (
    <div className="wrapper">
      <div className="editor">
        <div id="editor-container"></div>
        <button className="save-button btn" id="save-button">Save</button>
      </div>
      <div id="output" className="output"></div>
    </div>
  );
};

export default App;
