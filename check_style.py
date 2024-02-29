import os
import pandas
import torch
from torch import nn
from pathlib import Path
from transformers import BertTokenizer, BertModel

class MyModel(nn.Module):
    def __init__(self, roberta):
        super(MyModel, self).__init__()
        self.bert = roberta
        self.predictor = nn.Sequential(
            nn.Linear(768, 256),
            nn.ReLU(),
            nn.Linear(256, 1)
        )

    def forward(self, src):
        outputs = self.bert(**src).last_hidden_state[:, 0, :]
        return self.predictor(outputs)
    
def load_character_bert():
    model_dir = Path("./drive/character_bert")
    os.makedirs(model_dir) if not os.path.exists(model_dir) else ''
    
    model = torch.load(model_dir / f"model.pt")
    model = model.eval()

    roberta_dir = model_dir /'chinese-roberta-wwm-ext'
    tokenizer = BertTokenizer.from_pretrained(roberta_dir)
    roberta = BertModel.from_pretrained(roberta_dir)
    
    return model,tokenizer

def classify_text(text, model, tokenizer):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    embedding = tokenizer(text, padding='max_length', max_length=128, return_tensors='pt', truncation=True)
    input_tensor = {key: value.to(device) for key, value in embedding.items()}  # 将所有的张量移动到同一个设备上
    model.to(device)  # 将模型移动到设备上
    with torch.no_grad():
        output = model(input_tensor)  # 使用model(input_tensor)来进行前向传播
    output = (output >= 0.5).int().flatten().tolist()[0]  # 注意这里输出可能需要根据你的模型结构进行调整
    return output
