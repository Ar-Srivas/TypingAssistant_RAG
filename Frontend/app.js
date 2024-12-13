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

// Preview Button Logic
previewBtn.addEventListener("click", () => {
  const content = quill.root.innerHTML;
  output.classList.add("active");
  setTimeout(() => {
    output.innerHTML = content;  // Use innerHTML instead of textContent
  }, 1200);
});

// Toggle Dark Mode
toggleBtn.addEventListener("click", () => {
  document.body.classList.toggle("dark-mode");

  // Change Quill theme colors on toggle
  const editorContainer = document.querySelector("#editor-container");
  editorContainer.classList.toggle("dark-editor");

  toggleBtn.textContent = document.body.classList.contains("dark-mode")
    ? "Switch to Light Mode"
    : "Switch to Dark Mode";
});
