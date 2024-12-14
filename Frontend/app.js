const previewBtn = document.querySelector("#preview-button");
const output = document.querySelector(".output");
const toggleBtn = document.querySelector("#toggle-dark-mode");  // Dark mode button

const toolbarOptions = [
  [{ font: [] }],
  [{ header: [1, 2, 3] }],
  ["bold", "italic", "underline", "strike"],
  [{ color: [] }, { background: [] }],
  [{ list: "ordered" }, { list: "bullet" }, { list: "check" }],
  ["blockquote", "code-block"],
  ["link", "image", "video"],
  [{ align: [] }],
];

const quill = new Quill("#editor-container", {
  theme: "snow",
  modules: {
    toolbar: toolbarOptions,
  },
});

// Toggle Dark Mode
toggleBtn.addEventListener('click', function() {
    document.body.classList.toggle('dark-mode');
});
