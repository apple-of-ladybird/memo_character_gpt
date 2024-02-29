import json
import sqlite3
from get_keyword import *

keybert_model = load_keybert()

# 全局变量，存储停用词集合
stop_words = set()

def load_stopwords(stopwords_file):
    global stop_words
    with open(stopwords_file, 'r', encoding='GBK') as f:
        stop_words = {line.strip() for line in f.readlines()}
        
stopwords_file = './database/stop_words.txt'        
load_stopwords(stopwords_file)

import jieba

import numpy as np
from collections import defaultdict

BASEMEMO = 2515
NUM_MEMO_PER_INDEX = 5
NUM_ALL = 15

def get_input():
    sentence = input()

    words = ' '.join(jieba.lcut(sentence))
    keywords_list = keybert_model.extract_keywords(words)
    keywords_with_prob = []
    pc = 0 
    for item in keywords_list:
        if item[0] in stop_words:
            continue
        if item[1] > 0.5:
            keywords_with_prob.append({'keyword': item[0], 'kp1': item[1]})
            continue
        if item[1] > 0.4:
            keywords_with_prob.append({'keyword': item[0], 'kp1': item[1]})
            break
        else:
            break
    return keywords_with_prob

def search(keywords):
    conn = sqlite3.connect('./database/mydatabase.db')
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(memory_id) FROM memo;")
    T = cursor.fetchone()[0] - BASEMEMO
    print(T)
    target_dictionary = []
    for keyword in keywords:# keyword是单个问句中的单个关键词，带概率的
        # print(keyword)
        keyword_ask = keyword['keyword']
        print(keyword_ask)
        kp1 = keyword['kp1']
        cursor.execute('SELECT index_keywords, index_memory, index_matrix, index_id FROM invedex WHERE index_keywords LIKE ?', ('%' + json.dumps(keyword_ask)+ '%',))   
        result = cursor.fetchall()
        if not result:
            continue
        # 目标索引相关信息 关键词列表、记忆编号列表、相似度矩阵
        per_kws = json.loads(result[0][0])
        per_memos = json.loads(result[0][1])
        per_matrix = json.loads(result[0][2])
        per_index_id = result[0][3]
        for per_memo in per_memos:#per_memo单个关键词对应的单条记忆
            per_memo_kws = []
            cursor.execute('SELECT memory_keywords, memory_strength, memory_recall_records FROM memo WHERE memory_id = ?', (per_memo,))
            result2 = cursor.fetchall()
            if not result2:  # 如果result2为空
                continue
            # print("per_memo:",per_memo)
            # print("result2:",result2)
            per_alpha = result2[0][1]
            # print(per_alpha)
            per_final = json.loads(result2[0][2])[-1]
            # print(per_final)
            tar_kws = json.loads(result2[0][0])#目标记忆的所有关键词
            
            for item in tar_kws:#去单条记忆中提取对应关键词 以及对应关键词的概率 item是字典{'keyword': '嘱咐', 'weight': 0.6529}
                if item['keyword'] in per_kws:
                    keyword_fromindex = item['keyword']
                    kp2 = item['weight']
                    item_kw = {
                        "keyword":keyword_fromindex,
                        "weight":kp2
                    }
                    per_memo_kws.append(item_kw)#考虑单句多关键词 如同时出现杨过、小龙女
                    
            for per_memo_kw in per_memo_kws:
                if len(per_matrix) == 1:
                    word_similar = 1
                else:
                    key1_pos = per_kws.index(keyword_ask)
                    key2_pos = per_kws.index(keyword_fromindex)
                    word_similar = per_matrix[key1_pos][key2_pos]
                
                x = T - per_final
                memory_widget = np.exp(-per_alpha * 0.005 * x)
                
                per_score = 0.2 * memory_widget + 0.4 * word_similar * kp2 + 0.4 * kp1
                
                per_dict = {
                    "index_id": per_index_id,
                    "memory_id": per_memo,
                    "memory_score": per_score
                }
                
                target_dictionary.append(per_dict)
                                    
        '''
        for memo_id in memos:
            cursor.execute('SELECT memory_keywords, memory_strength FROM memo WHERE memory_id = ?', (memo_id,))
        '''
        
    # 使用 defaultdict 将字典列表按照 index_id 进行分组
    grouped_dict = defaultdict(list)
    for d in target_dictionary:
        grouped_dict[d["index_id"]].append(d)

    # 对于每个 index_id 对应的字典列表，按照 memory_score 进行降序排序，并保留前五条记录
    result = []
    for _, group in grouped_dict.items():
        sorted_group = sorted(group, key=lambda x: x['memory_score'], reverse=True)[:NUM_MEMO_PER_INDEX]
        result.extend(sorted_group)

    # 对新的字典列表按照 memory_score 进行排序
    final_result = sorted(result, key=lambda x: x['memory_score'], reverse=True)
    
    # 提取前十条
    for item in final_result[:NUM_ALL]:
        cursor.execute('SELECT memory_content FROM memo WHERE memory_id = ?', (item['memory_id'],))
        result2 = cursor.fetchall()[0][0]
        print(json.loads(result2))
        
    conn.close()
    
kws = get_input()
ans = search(kws)