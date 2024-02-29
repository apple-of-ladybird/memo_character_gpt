from check_similar import *
from check_style import *
from get_simi_word import *
from get_keyword import *
import jieba

similar_bert_model = load_simimlar_bert()
style_bert_model,style_bert_tokenizer = load_character_bert()
word2vec_model = load_word2vec()
keybert_model = load_keybert()

# 全局变量，存储停用词集合
stop_words = set()

def load_stopwords(stopwords_file):
    global stop_words
    with open(stopwords_file, 'r', encoding='GBK') as f:
        stop_words = {line.strip() for line in f.readlines()}
        
import json
input_file = './database/core_memory.jsonl'
output_folder = './output'
os.makedirs(output_folder, exist_ok=True)

output_file = output_folder + '/core_memory.json'

stopwords_file = './database/stop_words.txt'
load_stopwords(stopwords_file)

with open(input_file,'r',encoding='utf-8') as input:
    lines = input.readlines()
    dialogs = []
    for line in lines:
        temp = json.loads(line)
        dialog = []
        for item in temp['conversations']:
            if item['role'] == 'user':
                dialog.append('用户：'+item['content'])
            elif item['role'] == 'assistant':
                dialog.append('助手：'+item['content'])
        dialogs.append(dialog)

new_dialogs = []
for i in range(len(dialogs) - 1):
    dialog_a = dialogs[i]
    keep_dialog = True
    for j in range(i + 1, len(dialogs)):
        dialog_b = dialogs[j]
        if classify_similar(dialog_a[0][3:], dialog_b[0][3:], similar_bert_model) > 0.5 and classify_similar(dialog_a[1][3:], dialog_b[1][3:], similar_bert_model) > 0.5:
            print(dialog_a, dialog_b)
            keep_dialog = False
            break
    if keep_dialog:
        new_dialogs.append(dialog_a)
dialogs = new_dialogs

import json

# 构建字典列表，并手动添加其他字段信息
new_dialogs_with_info = []
for idx, content in enumerate(new_dialogs):
    dialog_dict = {
        "memory_id": idx + 1,
        "memory_rounds": 2,
        "memory_content": content,
        "memory_keywords": [],
        "memory_recall_count": 1,
        "memory_recall_records": [-1],
        "memory_strength": 1.0,
        "memory_category": 0,
        "memory_trigger": 0
    }
    new_dialogs_with_info.append(dialog_dict)

# 建立一个新的列表代替new_dialogs_with_info
new_list = []

# 遍历 new_dialogs_with_info 列表，对每个字典中的 memory_content 字段进行处理
for dialog in new_dialogs_with_info:
    # 将 memory_content 中的两个字符串拼接成一个字符串
    content = dialog['memory_content'][0][3:] + ' ' + dialog['memory_content'][1][3:]
    # 使用 jieba 进行分词
    words = ' '.join(jieba.lcut(content))
    # 用 keybert 提取关键词列表和概率
    keywords_list = keybert_model.extract_keywords(words)
    # 将筛选出的关键词和概率写入到 memory_keywords 字段中
    keywords_with_prob = []
    pc = 0 
    for item in keywords_list:
        if item[0] in stop_words:
            continue
        if item[1] > 0.6:
            keywords_with_prob.append({'keyword': item[0], 'weight': item[1]})
            continue
        if item[1] > 0.5:
            keywords_with_prob.append({'keyword': item[0], 'weight': item[1]})
            break
        else:
            break
    dialog['memory_keywords'] = keywords_with_prob

    # 如果 keywords_with_prob 不为空，将其加入新列表
    if keywords_with_prob:  
        new_list.append(dialog)

# 现在 new_list 中包含了根据关键词情况筛选后的新数据

# 将字典列表转换为JSON格式并写入文件
with open(output_file, 'w') as f:
    json.dump(new_list, f, indent=4)