from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_pre import create_vectorspace, get_suggestion, client
import io
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS
vectorDB = None

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    global vectorDB
    try:
        file = request.files['file']
        pdf_stream = io.BytesIO(file.read())
        vectorDB = create_vectorspace(pdf_stream)
        return jsonify({"message": "PDF uploaded and vector space created."})
    except Exception as e:
        logging.error(f"Error uploading PDF: {e}")
        return jsonify({"error": "Error uploading PDF"}), 500

@app.route('/get_suggestion', methods=['POST'])
def get_suggestion_route():
    global vectorDB
    try:
        if not vectorDB:
            logging.error("VectorDB not initialized")
            return jsonify({"error": "PDF not uploaded"}), 400
            
        data = request.json
        query = data.get('query')
        logging.info(f"Received query: {query}")
        
        suggestion = get_suggestion(client, query, vectorDB)
        logging.info(f"Generated suggestion: {suggestion}")
        
        return jsonify({"suggestion": suggestion})
    except Exception as e:
        logging.error(f"Error in get_suggestion_route: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)