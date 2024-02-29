from sentence_transformers import SentenceTransformer
from keybert import KeyBERT

def load_keybert():
    model = SentenceTransformer('./drive/sentence-transformersparaphrase-multilingual-MiniLM-L12-v2')
    kw_model = KeyBERT(model=model)
    return kw_model
