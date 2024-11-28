import torch
def predict(text, tokenizer, model, device):
    # 입력값 전처리
    inputs = preprocess_input(text, tokenizer)
    input_ids = inputs['input_ids'].to(device)
    attention_mask = inputs['attention_mask'].to(device)

    # 모델 추론
    model.eval()
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits

    # 레이블 예측
    predicted_label = torch.argmax(logits, dim=1).item()
    return predicted_label


def preprocess_input(text, tokenizer, max_length=128):
    inputs = tokenizer(
        text,
        max_length=max_length,
        padding='max_length',
        truncation=True,
        return_tensors="pt"
    )
    return inputs