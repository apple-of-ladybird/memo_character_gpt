from check_similar import *
similar_bert_model = load_simimlar_bert()
import sqlite3
import json
from collections import Counter

conn = sqlite3.connect('./database/mydatabase.db')
cursor = conn.cursor()
cursor.execute('SELECT index_id, index_memory FROM invedex WHERE index_trigger = 0')
results = cursor.fetchall()

delete_ids = []

# 遍历查询结果并处理
for result in results:
    delete_temp = []
    
    memo_dicts = []
    index_id = result[0]
    memos = json.loads(result[1])
    # print(memos)
    
    for memo_id in memos:
        cursor.execute('SELECT memory_rounds, memory_content FROM memo WHERE memory_id = ?', (memo_id,))
        memo_info = cursor.fetchall()[0]
        content = json.loads(memo_info[1])
        memo_dict = {
            "memory_id": memo_id,
            "memory_rounds": memo_info[0],
            "memory_content": content
        }
        memo_dicts.append(memo_dict)
    
    for i in range(len(memo_dicts) - 1):
        dialog_a = memo_dicts[i]['memory_content']
        for j in range(i + 1, len(memo_dicts)):
            dialog_b = memo_dicts[j]['memory_content']
            skip_flag = False
            if len(dialog_a) == len(dialog_b):
                for k in range(len(dialog_a)):
                    if classify_similar(dialog_a[k][3:], dialog_b[k][3:], similar_bert_model) < 0.5:
                        skip_flag = True
                        break
            else:
                skip_flag = True
                break
                
            if skip_flag:
                continue
            else:
                print("delete------------------------------------")
                delete_ids.append(memo_dicts[i]['memory_id'])
                delete_temp.append(memo_dicts[i]['memory_id'])
                break
                
    new_memos = [memo for memo in memos if memo not in delete_temp]
    
    cursor.execute("UPDATE invedex SET index_trigger = 1, index_memory = ? WHERE index_id = ?", (json.dumps(new_memos),index_id,))
    #事实上这里并没有在索引中删除掉所有的删除记忆：因为某记忆可能有多个关键词，它可能仅仅只在一个索引中被删掉了，因此，应当在搜索记忆时添加纠错机制
    conn.commit()
    
    print(index_id)
    print("over")
        
print(delete_ids)      

for id in delete_ids:
    cursor.execute('DELETE FROM memo WHERE memory_id = ?',(id,))
    conn.commit()

conn.close()