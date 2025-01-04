import tkinter as tk
from tkinter import filedialog, font
import PyPDF2
import threading
import sys
import io

# Import necessary functions from rag_prediction
from TypingAssistant.rag_pre import create_vectorspace, get_suggestion, client

# Global variables
current_font_family = "Arial"
current_font_size = 12
pdf_path = ""
vectorDB = None
suggestion_window = None

root = tk.Tk()
root.title('TextPad with RAG Suggestions')
root.geometry("1200x700")

# Function to load PDF
def load_pdf():
    global pdf_path, vectorDB
    pdf_file = filedialog.askopenfilename(initialdir=".", title="Open PDF File", filetypes=(("PDF Files", ".pdf"), ("All Files", ".*")))
    if pdf_file:
        pdf_path = pdf_file
        status_bar.config(text='Loading PDF and creating vector space...')
        
        # Run vector space creation in a separate thread
        thread = threading.Thread(target=create_vector_space, args=(pdf_file,))
        thread.start()

def create_vector_space(pdf_file):
    global vectorDB
    
    try:
        vectorDB = create_vectorspace(pdf_file)
        root.after(0, lambda: status_bar.config(text='PDF loaded and vector space created.'))
    except Exception as e:
        root.after(0, lambda: status_bar.config(text=f'Error: {str(e)}'))

# Function to get suggestions
def get_suggestions(event=None):
    global vectorDB, suggestion_window
    
    if not vectorDB:
        status_bar.config(text="Please load a PDF first")
        return
    
    try:
        current_text = my_text.get("1.0", tk.END).strip()
        sentences = current_text.split('.')
        last_sentence = sentences[-1].strip() if sentences else ""
        
        current_line = my_text.get("insert linestart", "insert").strip()
        if current_line.endswith(':') and len(current_line) > 1:
            # Destroy old suggestion window if it exists
            if suggestion_window:
                suggestion_window.destroy()
            
            words_before_colon = current_line.split(':')[0].strip()
            query = f"{words_before_colon}. {last_sentence}"
            suggestion = get_suggestion(client, query, vectorDB)
            show_suggestion_window(suggestion)
        else:
            status_bar.config(text="Type a colon (:) at the end of a non-empty line for suggestions")
    except Exception as e:
        print(f"Error in get_suggestions: {e}")
        status_bar.config(text="Error getting suggestions")

def show_suggestion_window(suggestion):
    global suggestion_window
    suggestion_window = tk.Toplevel(root)
    suggestion_window.overrideredirect(True)
    suggestion_window.attributes('-topmost', True)
    
    # Position the window at the bottom of the screen
    x = root.winfo_x() + my_text.winfo_x()
    y = root.winfo_y() + root.winfo_height() - 50  # 50 pixels from the bottom
    suggestion_window.geometry(f"+{x}+{y}")
    
    btn = tk.Button(suggestion_window, text=suggestion, 
                    command=lambda: insert_suggestion(suggestion, suggestion_window),
                    bg='#f0f0f0', fg='#333333', font=('Arial', 10))
    btn.pack(fill=tk.X, padx=5, pady=5)

def insert_suggestion(suggestion, window):
    my_text.insert(tk.INSERT, f" {suggestion}")
    window.destroy()

# Creating main frame
my_frame = tk.Frame(root, padx=10, pady=10)
my_frame.pack(pady=5, fill=tk.BOTH, expand=True)

# Text box scroll bar
text_scroll = tk.Scrollbar(my_frame)
text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

# Text box with word wrap enabled
my_text = tk.Text(my_frame, font=(current_font_family, current_font_size), 
                  selectbackground='#a6a6a6', selectforeground='black', undo=True, 
                  yscrollcommand=text_scroll.set, wrap='word', bg='#f5f5f5', fg='#333333')
my_text.pack(expand=True, fill=tk.BOTH)
my_text.bind('<Key>', get_suggestions)  # Trigger suggestions on any key press

# Configure scrollbar
text_scroll.config(command=my_text.yview)

# Create menu
my_menu = tk.Menu(root)
root.config(menu=my_menu)

# Add file menu
file_menu = tk.Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="New", command=lambda: my_text.delete("1.0", tk.END))
file_menu.add_command(label="Open", command=lambda: my_text.insert(tk.END, open(filedialog.askopenfilename()).read()))
file_menu.add_command(label="Save", command=lambda: open(filedialog.asksaveasfilename(), 'w').write(my_text.get("1.0", tk.END)))
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

# Add edit menu
edit_menu = tk.Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Cut", command=lambda: my_text.event_generate("<<Cut>>"))
edit_menu.add_command(label="Copy", command=lambda: my_text.event_generate("<<Copy>>"))
edit_menu.add_command(label="Paste", command=lambda: my_text.event_generate("<<Paste>>"))

# Add RAG menu
rag_menu = tk.Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="RAG", menu=rag_menu)
rag_menu.add_command(label="Load PDF", command=load_pdf)

# Add status bar
status_bar = tk.Label(root, text='Ready', anchor=tk.E, bg='#e0e0e0', fg='#333333')
status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=5)

# Redirect stdout to avoid encoding errors
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

root.mainloop()