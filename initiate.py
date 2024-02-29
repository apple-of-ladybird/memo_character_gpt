import os

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 要依次运行的 Python 文件列表
python_files = ['get_temp_base.py', 'get_temp_core.py', 'write.py', 'clean.py']

# 逐个运行 Python 文件
for file in python_files:
    file_path = os.path.join(current_dir, file)
    os.system(f'python {file_path}')
