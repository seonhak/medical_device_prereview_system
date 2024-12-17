import torch
from transformers import BertForSequenceClassification
from kobert_transformers import get_tokenizer
from .utils import predict, preprocess_input

def predict_label(input_text):
    # if type(input_text) != type(str):
    #     return f"데이터를 읽어오지 못했습니다.\r\n"
    # 모델 및 토크나이저 로드
    model_dir = "C:\\Users\\USER\\Desktop\식약처\\medical_device_prereview_system\\scripts\\models\\finetuned_kobert_label2"
    tokenizer = get_tokenizer()
    model = BertForSequenceClassification.from_pretrained(model_dir)
    # GPU 사용 가능 여부 확인 후 모델 이동
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    inputs = preprocess_input(input_text, tokenizer)
    # print(inputs)
    predicted_label = predict(input_text, tokenizer, model, device)
    
    result = ''
    # print(type(predicted_label))
    if(predict_label == 0) : 
        result = f"입력파일 내용 : {input_text} \r\n 문장에서 오류가 검출되지 않는 것으로 판단됩니다."
        # print(result)
    else :
        result = f"입력파일 내용 : {input_text} \r\n 문장에서 오류가 검출되는 것으로 판단됩니다."
        # print(result)
    return result