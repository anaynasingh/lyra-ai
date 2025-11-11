import numpy as np
import json
import random
import string
import re

def chunk_text(text, chunk_size=1000, chunk_overlap=200):
    """
    Split text into overlapping chunks without using langchain.
    
    Args:
        text: The text to split
        chunk_size: Maximum size of each chunk
        chunk_overlap: Number of characters to overlap between chunks
    
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    # Split by paragraphs first (double newline)
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        # If adding this paragraph exceeds chunk_size, save current chunk
        if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Start new chunk with overlap from previous chunk
            overlap_start = max(0, len(current_chunk) - chunk_overlap)
            current_chunk = current_chunk[overlap_start:] + "\n\n" + paragraph
        else:
            current_chunk += "\n\n" + paragraph if current_chunk else paragraph
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # If no paragraphs were found, split by sentences
    if len(chunks) == 0 or (len(chunks) == 1 and len(chunks[0]) > chunk_size):
        return chunk_by_sentences(text, chunk_size, chunk_overlap)
    
    return chunks

def chunk_by_sentences(text, chunk_size=1000, chunk_overlap=200):
    """
    Fallback method: split text by sentences if paragraph splitting doesn't work well.
    """
    # Simple sentence splitting (can be improved with nltk if needed)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Start new chunk with overlap
            overlap_start = max(0, len(current_chunk) - chunk_overlap)
            current_chunk = current_chunk[overlap_start:] + " " + sentence
        else:
            current_chunk += " " + sentence if current_chunk else sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def preprocess_text(text):
    """Preprocess the input text for analysis."""
    return text.lower()

def calculate_similarity(vector_a, vector_b):
    """Calculate cosine similarity between two vectors."""
    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return np.dot(vector_a, vector_b) / (norm_a * norm_b)

def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, file_path):
    """Save data to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def generate_random_id(length=8):
    """Generate a random string ID of specified length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))