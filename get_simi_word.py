from gensim.models import Word2Vec
from pathlib import Path

def load_word2vec():
    model_save_path = './drive/word2vec/wiki_zh.model'
    model = Word2Vec.load(model_save_path)
    return model

'''model=load_word2vec()
res = model.wv.most_similar('激动')
print(res)'''
