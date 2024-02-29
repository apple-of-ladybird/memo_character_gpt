import json
import os

output_folder = './output'
os.makedirs(output_folder, exist_ok=True)
core_file = output_folder + '/core_memory.json'
base_file = output_folder + '/base_memory.json'

# 读取JSON文件
with open(core_file, 'r') as file:
    dialog_dict = json.load(file)
    
from get_simi_word import *
word2vec_model = load_word2vec()

import sqlite3

# 连接到SQLite数据库
conn = sqlite3.connect('./database/mydatabase.db')
cursor = conn.cursor()

# 创建一个表来存储数据，包括主键ID唯一且自动增加
cursor.execute('''
    CREATE TABLE IF NOT EXISTS memo (
        memory_id INTEGER PRIMARY KEY AUTOINCREMENT,
        memory_rounds INTEGER,
        memory_content TEXT,
        memory_keywords TEXT,
        memory_recall_count INTEGER,
        memory_recall_records TEXT,
        memory_strength REAL,
        memory_category INTEGER,
        memory_trigger INTEGER
    )
''')
conn.commit()

for item in dialog_dict:
    # 将数据插入SQLite数据库
    cursor.execute('''
        INSERT INTO memo (memory_rounds, memory_content, memory_keywords, memory_recall_count, memory_recall_records, memory_strength, memory_category, memory_trigger)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (item["memory_rounds"], json.dumps(item["memory_content"]), json.dumps(item["memory_keywords"]), item["memory_recall_count"], json.dumps(item["memory_recall_records"]), item["memory_strength"], item["memory_category"], item["memory_trigger"]))

    conn.commit()
    
with open(base_file, 'r') as file2:
    dialog_dict2 = json.load(file2)
    
for item in dialog_dict2:
    # 将数据插入SQLite数据库
    cursor.execute('''
        INSERT INTO memo (memory_rounds, memory_content, memory_keywords, memory_recall_count, memory_recall_records, memory_strength, memory_category, memory_trigger)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (item["memory_rounds"], json.dumps(item["memory_content"]), json.dumps(item["memory_keywords"]), item["memory_recall_count"], json.dumps(item["memory_recall_records"]), item["memory_strength"], item["memory_category"], item["memory_trigger"]))

    conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS invedex (
        index_id INTEGER PRIMARY KEY AUTOINCREMENT,
        index_keywords TEXT,
        index_memory TEXT,
        index_matrix TEXT,
        index_trigger INTEGER
    )
''')
conn.commit()

import sqlite3
import json
import numpy as np

# 连接到SQLite数据库
conn = sqlite3.connect('./database/mydatabase.db')
cursor = conn.cursor()

# 从第一个表memo中获取memory_trigger=0的数据
cursor.execute('SELECT memory_id, memory_keywords FROM memo WHERE memory_trigger = 0')
memo_data = cursor.fetchall()

# 遍历第一个表中的数据
for row in memo_data:
    memory_id = row[0]
    data = json.loads(row[1])
    # 遍历memory_keywords中的关键词
    for item in data:
        keyword = item['keyword']
        keyword_w = json.dumps(item['keyword'])
        
        # 在第二个表invedex中搜索匹配的关键词
        cursor.execute('SELECT index_id, index_memory FROM invedex WHERE index_keywords LIKE ?', ('%' + keyword_w+ '%',))
        matching_data = cursor.fetchall()
        if len(matching_data) == 0:
            # 如果找不到匹配的关键词，调用getsimilar函数获取近义词表
            
            try:
                similar_keywords = word2vec_model.wv.most_similar(keyword,topn = 10)
                list_kw = [keyword]
                for item in similar_keywords:
                    if item[1] > 0.6:
                        list_kw.append(item[0])
                    
            
            except KeyError:
                list_kw = [keyword]
                
            similarity_matrix = []

            # 计算相似度并填充相似度矩阵
            if len(list_kw) == 1:
                similarity_matrix = [1]
            else:
                for word1 in list_kw:
                    row = []
                    for word2 in list_kw:
                        similarity = round(word2vec_model.wv.similarity(word1, word2),3)
                        row.append(similarity)
                    similarity_matrix.append(row)
                
            # 将相似度矩阵转换为可序列化的列表
            serializable_matrix = np.array(similarity_matrix).tolist()

            # 插入数据到 SQLite 数据库
            cursor.execute('''
                INSERT INTO invedex (index_keywords, index_memory, index_matrix, index_trigger)
                VALUES (?, ?, ?, ?)
            ''', (json.dumps(list_kw), json.dumps([memory_id]), json.dumps(serializable_matrix), 1))
            conn.commit()
                           
            continue

        # 将匹配到的index_memory中添加第一个记忆的ID
        for match in matching_data:
            
            index_id = match[0]
            index_memory = json.loads(match[1])
            
            if memory_id not in index_memory:
                index_memory.append(memory_id)
                cursor.execute('UPDATE invedex SET index_memory = ?, index_trigger = ? WHERE index_id = ?', (json.dumps(index_memory), 0, index_id))
                conn.commit()
    
    # 插入数据到 SQLite 数据库
    cursor.execute("UPDATE memo SET memory_trigger = ? WHERE memory_id = ?", (1,memory_id))
    conn.commit()
    
    conn.close()  # 关闭数据库连接

    # 在下一个循环开始时重新打开数据库连接
    conn = sqlite3.connect('./database/mydatabase.db')
    cursor = conn.cursor()
                          
conn.close()