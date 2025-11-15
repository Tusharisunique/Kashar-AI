from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# File size limit (10MB)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise

def chunk_text(text, chunk_size=1000, overlap=200):
    """Split text into chunks with overlap"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Find the last complete sentence in the chunk
        if end < len(text):
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            last_break = max(last_period, last_newline)
            
            if last_break > start + chunk_size // 2:
                chunk = chunk[:last_break + 1]
                end = start + len(chunk)
        
        chunks.append(chunk.strip())
        start = end - overlap
        
        if start >= len(text):
            break
    
    return [chunk for chunk in chunks if len(chunk.strip()) > 50]

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/parse-pdf', methods=['POST'])
def parse_pdf():
    """Parse PDF and return extracted text chunks"""
    try:
        # Validate request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Only PDF files are allowed"}), 400
        
        # Extract text from PDF
        pdf_content = io.BytesIO(file.read())
        text = extract_text_from_pdf(pdf_content)
        
        if not text.strip():
            return jsonify({"error": "No text found in PDF"}), 400
        
        # Chunk the text
        chunks = chunk_text(text)
        
        logger.info(f"Successfully parsed PDF: {file.filename}, {len(chunks)} chunks")
        
        return jsonify({
            "filename": file.filename,
            "text": text,
            "chunks": chunks,
            "chunk_count": len(chunks)
        })
        
    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")
        return jsonify({"error": "Failed to parse PDF"}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large. Maximum size is 10MB"}), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
