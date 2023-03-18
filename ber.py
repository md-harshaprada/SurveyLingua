from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
tokens = tokenizer.encode('best product', return_tensors='pt')

result = model(tokens)
rating=int(torch.argmax(result.logits))+1
print(rating)