from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def create_vector_store(chunks):
    """
    Build a TF-IDF vectorizer and matrix for the provided text chunks.
    Returns: (embeddings_matrix, vectorizer, chunks)
    """
    if not chunks:
        return None, None, []
    
    vectorizer = TfidfVectorizer(
        max_features=1000,
        strip_accents='unicode', 
        stop_words='english', 
        ngram_range=(1, 2)
    )
    embeddings = vectorizer.fit_transform(chunks)
    return embeddings, vectorizer, chunks

def retrieve_relevant_chunks(query, embeddings, vectorizer, chunks, top_k=3):
    """
    Return the top_k most relevant chunks for `query`.
    Returns a list of tuples: (chunk_text, score)
    """
    if embeddings is None or vectorizer is None or not chunks:
        return []
    
    q_vec = vectorizer.transform([query])
    sims = cosine_similarity(q_vec, embeddings).flatten()
    
    if np.all(np.isnan(sims)):
        return []
    
    idxs = np.argsort(sims)[::-1][:top_k]
    results = []
    for i in idxs:
        results.append((chunks[int(i)], float(sims[int(i)])))
    
    return results