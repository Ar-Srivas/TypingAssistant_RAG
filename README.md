# Text Prediction and Information Retrieval Assistant

## Overview

This project integrates a **text prediction model** with a **Retrieval-Augmented Generation (RAG) model** using an LLM (Large Language Model) to provide an intelligent assistant capable of predicting text in real-time and retrieving relevant information from PDF documents. The goal is to enhance user productivity by combining predictive typing with document-based information retrieval.


## Features

- **Contextual Text Prediction**: The assistant offers word and phrase suggestions as you type, based on the content of uploaded documents.
- **Information Retrieval from PDFs**: The RAG model can extract relevant information from a corpus of PDF documents, answering user queries contextually.
- **AI-Powered Response Generation**: By using a hybrid of retrieval and generation, the assistant can both fetch exact information from the PDFs and generate natural responses based on LLMs.

## Workflow and Functionality

The application functions in two major workflows:

1. **Text Prediction**:
    - Uses a pre-trained language model for providing word suggestions.
    - Takes into account the content of the uploaded PDFs to give context-aware suggestions.
  
2. **Retrieval-Augmented Generation (RAG)**:
    - Leverages a RAG model that combines a retriever and generator.
    - The retriever fetches relevant text passages from PDFs, and the generator (LLM) produces a response based on both the retrieved information and the user’s input.


  
### Dependencies

Ensure the following dependencies are available inside your AI Workbench environment:
- **Python 3.8+**
- **Libraries**:
  - `Tkinter`
  - `Tensorflow`
  - `faiss-cpu==1.8.0.post1`
  - `huggingface-hub==0.25.1`
  - `langchain==0.3.1`
  - `langchain-community==0.3.1`
  - `langchain-core==0.3.6`
  - `langchain-text-splitters==0.3.0`
  - `langsmith==0.1.129`
  - `numpy==1.26.4`
  - `PyPDF2==3.0.1`
  - `threadpoolctl==3.5.0`
  - `tokenizers==0.20.0`
  - `torch==2.4.1`
  - `transformers==4.45.1`


### Restrictions

- **Models**: The application requires pre-trained language models from **Hugging Face** (microsoft/Phi-3.5-mini-instruct) and a **retrieval model** for RAG.
- 

## Project Structure

- **`text_editor.py`**: Contains the logic for the text prediction module.
- **`rag_pre.py`**: Implements the RAG model for document-based information retrieval and response generation.
- **`requirements.txt`**: Lists all dependencies necessary to run the project.
- **Dockerfile**: Defines the container image for the application to run on NVIDIA AI Workbench.

## Getting Started

1. **Clone the Repository**:
    you can use github to easily clone or get started with a workspace. Install all the requirements.
2. **Download Requirements**:
    By using requirements.txt
3. **Python files**:
    Ensure all files are in the same directory including the pdf you want to read for this version followed by running only the texteditor.py file 
4: **Usage**:
    Start typing as normal and use ':' and a space to trigger the RAG model. After you get the suggestions, you can select it to autofill. (Check for API rate limit if text editor prompts error in finding suggestions)

