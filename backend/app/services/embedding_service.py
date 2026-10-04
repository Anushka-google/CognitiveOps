_model = None

def get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except ImportError:
            _model = None
    return _model

def generate_embeddings(chunks):
    model = get_model()
    if model is None:
        return [[] for _ in chunks] # Dummy fallback if ML disabled
    embeddings = model.encode(chunks)
    return embeddings