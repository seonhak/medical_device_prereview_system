import torch
from transformers import BertForSequenceClassification
from kobert_transformers import get_tokenizer
from .utils import predict, preprocess_input

def predict_label(input_text):
    
    # 모델 및 토크나이저 로드
    model_dir = "C:\\Users\\USER\\Desktop\식약처\\medical_device_prereview_system\\scripts\\models\\finetuned_kobert"
    tokenizer = get_tokenizer()
    model = BertForSequenceClassification.from_pretrained(model_dir)
    # GPU 사용 가능 여부 확인 후 모델 이동
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    inputs = preprocess_input(input_text, tokenizer)
    # print(inputs)
    predicted_label = predict(input_text, tokenizer, model, device)
    print(f"Predicted Label about {input_text} : {predicted_label}")
    return f"Predicted Label about {input_text} : {predicted_label}"