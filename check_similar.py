from pathlib import Path
from sentence_transformers import SentenceTransformer, util

def load_simimlar_bert():
    model_dir = Path("./drive")
    model_save_path = model_dir / 'similar_bert'
    model =  SentenceTransformer(model_save_path)
    return model

def classify_similar(sentence1, sentence2,model):
    embedding1 = model.encode(sentence1, convert_to_tensor=True)
    embedding2 = model.encode(sentence2, convert_to_tensor=True)
    similarity = util.cos_sim(embedding1, embedding2)
    similarity = (similarity >= 0.5).int().flatten()
    return similarity.item()