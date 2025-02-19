import re
from .forbidden_words import *

def validate_include_phrase(required_phrases, normalized_data, error_count, file_name, rule_name):
    error_messages = []
    not_included_phrase = []
    for phrase_pattern in required_phrases:
        normalized_phrase = normalize_text(phrase_pattern)  # 필수 문장 정규화
        if not clean_text(normalized_phrase) in clean_text(normalized_data):
            not_included_phrase.append(phrase_pattern)
    if len(not_included_phrase) != 0:
        message = f"{error_count}. 신고서류 {file_name} 파일에서 필수 문장이 포함되지 않은 것으로 확인됩니다. "
        message += f"재검토 원인은 필수 내용 미기재입니다. "
        for item in not_included_phrase:  
            message += '\r\n- ' + item
            if item == '사용 전':
                message += ' 준비사항'
            elif item == '사용 후':
                message += ' 보관 및 관리방법'
        message += f"\r\n관련 규정은 {rule_name}를 확인하시고, 위 필수 내용을 빠짐없이 기재하신 후 제출하시기 바랍니다.\r\n"
        error_messages.append(message)
        error_count += 1
    return error_messages, error_count

def clean_text(text):
    """텍스트에서 공백 및 줄바꿈을 제거하여 비교를 위한 클리닝."""
    return text.replace('\n', '').replace(' ', '').strip() if isinstance(text, str) else ""

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

def check_invalid_words(rows, error_count, file_name):
    """
    데이터 리스트에서 사용 불가 단어를 확인합니다.
    :param rows: 검사할 문자열 리스트
    :return: 에러 메시지 리스트
    """
    error_messages = []
    
    if not rows:  # rows가 None이거나 빈 리스트인 경우
        return error_messages, error_count
        
    for row in rows:
        if not row or not isinstance(row, str):  # row가 None이거나 문자열이 아닌 경우
            continue
            
        row = normalize_text(str(row).strip())
        if not row:  # 정규화 후 빈 문자열인 경우
            continue
            
        for invalid_word in forbidden_words:
            if invalid_word in row:
                error_messages.append(
                    f"{error_count}. 신고서류 {file_name} 파일에서 사용 불가 단어 \'{row}\'가 존재하는 것으로 확인됩니다. " +
                    f"재검토 원인은 명칭 내 사용 불가 단어 포함입니다. " +
                    f"관련 규정은 시행규칙 45조(별표 7 제1호~10호)를 확인하시고, 사용 불가 단어를 제거하신 후 제출하시기 바랍니다.\r\n"
                )
                error_count += 1
    
    return error_messages, error_count

def normalize_header(header_row):
    """헤더 행을 정규화하여 공백과 대소문자를 통일."""
    return [clean_text(cell).lower().replace(" ", "") for cell in header_row]

def is_skip_header(row, pattern):
    """
    주어진 행이 건너뛸 헤더인지 확인합니다.
    """
    cells = [str(cell) for cell in row if cell]
    return any(pattern.search(cell) for cell in cells)

def is_empty(value):
    """
    값이 비어있는지 확인합니다.
    
    Args:
        value: 확인할 값 (문자열, None 등)
    Returns:
        bool: 비어있으면 True, 아니면 False
    """
    return not value or str(value).strip() == ''