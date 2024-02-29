from check_similar import *
from check_style import *
from get_simi_word import *
from get_keyword import *

similar_bert_model = load_simimlar_bert()
style_bert_model,style_bert_tokenizer = load_character_bert()
word2vec_model = load_word2vec()
keybert_model = load_keybert()




















'''
print(classify_text("嗯……你已经很棒了，别害怕。",style_bert_model,style_bert_tokenizer)) 

print(classify_similar("用户：可以问你几个问题吗？助手：你尽管问吧，只要我知道，就会告诉你。",
                 "用户：你好，我有个问题想问你。助手：嗯，什么事？你问吧，我都说。",similar_bert_model))
print(word2vec_model.wv.most_similar('朱元璋'))
print(keybert_model.extract_keywords("""城东 新开 的 那家 咖啡馆 怎么样 ？
嗯 …… 我 上次 去过 一次 ， 感觉 还行 。
环境 怎么 样 ？
挺 安静 的 ， 我 还 蛮 中意 。"""))

'''

