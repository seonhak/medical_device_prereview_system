import re
from .forbidden_words import *
def validate_include_phrase(required_phrases, normalized_data):
    error_messages = []
    not_included_phrase = []
    for phrase_pattern in required_phrases:
        normalized_phrase = normalize_text(phrase_pattern)  # 필수 문장 정규화
        if not clean_text(normalized_phrase) in clean_text(normalized_data):
            not_included_phrase.append(phrase_pattern)
    if len(not_included_phrase) != 0:
        message = ""
        for item in not_included_phrase:        
            # if item == not_included_phrase[-1]:
            #     message += item
            # else:
                message += "- " + item + '\r\n'
        message += f"위 내용을 빠짐없이 기재"
        error_messages.append(message)
    return error_messages

def clean_text(text):
    """텍스트에서 공백 및 줄바꿈을 제거하여 비교를 위한 클리닝."""
    return text.replace('\n', '').replace(' ', '').strip() if isinstance(text, str) else ""

# 정규화 함수 확장
def normalize_text(text):
    """
    텍스트 정규화:
    - 불필요한 공백 및 특수 공백 제거
    - '\n', '\r' 등 개행 문자 제거
    - 일반 공백 문자 및 특수 공백 문자(\u200b, \u00a0, \u3000) 제거
    """
    # 줄바꿈 및 특수 공백 제거
    normalized = re.sub(r'[\u200b\u00a0\u3000\.]', '', text)  # 특수 공백과 온점 제거
    normalized = re.sub(r'\s+', '', normalized)  # 일반 공백 제거
    return normalized.strip()

def check_invalid_words(data_list):
    """
    데이터 리스트에서 사용 불가 단어를 확인합니다.
    :param data_list: 입력 데이터 리스트 (각각 문자열)
    :param invalid_words: 사용 불가 단어 리스트
    :return: 사용 불가 단어가 포함된 항목 리스트
    """
    error_messages = []
    for data in data_list:
        for row in data:
            if not isinstance(row, str):  # data가 문자열인지 확인
                print(f"경고: '{row}'는 문자열이 아니므로 건너뜁니다.")
                continue
            for invalid_word in forbidden_words:
                if invalid_word in row:  # 문자열 비교
                    error_message = (
                        f"사용 불가 단어 : \r\n 사용자 데이터 : \'{row}\'\r\n 사용 불가 단어 : \'{invalid_word}\' \r\n 시행규칙 45조(별표 7 제1호~10호) 내용 확인이 필요합니다."
                    )
                    error_messages.append(error_message)
    return error_messages

def normalize_header(header_row):
    """헤더 행을 정규화하여 공백과 대소문자를 통일."""
    return [clean_text(cell).lower().replace(" ", "") for cell in header_row]