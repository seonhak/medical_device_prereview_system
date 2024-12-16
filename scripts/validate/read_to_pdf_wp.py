import os
import re
import pdfplumber 
from .required_wp import *
from .forbidden_words import *
# 작용원리

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

def process_data_with_normalization(data, required_phrases, forbidden_words):
    error_messages = []  # 모든 오류 메시지를 저장할 리스트
    # 데이터 정규화
    normalized_data = normalize_text(data)
    # print(normalized_data)
    # 필수 문장 포함 여부 확인
    found_required_phrase = False
    for phrase_pattern in required_phrases:
        normalized_phrase = normalize_text(phrase_pattern)  
        if clean_text(normalized_phrase) in clean_text(normalized_data):
            found_required_phrase = True 
            break  
    # 필수 문장이 하나도 포함되지 않은 경우 에러 메시지 추가
    if not found_required_phrase:
        error_messages.append(
            f" 신고서류 내 검토필요사항 내용: {data} \r\n 검토사항 발생 요인 : 필수 문장이 하나도 포함되지 않았습니다. \r\n 검토사항에 대한 근거 : 작용원리 - 규정 제12조 내용 확인이 필요합니다"
        )
    # 금지 단어 포함 여부 확인
    lines = data.splitlines()
    for line_number, line in enumerate(lines, start=1):
        normalized_line = normalize_text(line)  # 각 줄 정규화
        for word_pattern in forbidden_words:
            normalized_word = normalize_text(word_pattern)  # 금지 단어 정규화
            if re.search(normalized_word, normalized_line):
                error_messages.append(
                    f" 신고서류 내 검토필요요사항 내용: {normalized_line} \r\n 검토사항 발생 요인 : 금지 단어 \'{normalized_word}\'(이)가 포함되었습니다. \r\n 검토사항에 대한 근거 : 작용원리 - 규정 제12조 내용 확인이 필요합니다"
                    )
    return error_messages

#############################################################
#스타킹#
def validate_wp_stockings1(pdf_file_path):
    try:
        full_text = ""  # 전체 PDF 텍스트를 저장할 변수
        with pdfplumber.open(pdf_file_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                # 페이지 텍스트 추출
                text = page.extract_text()
                if text:
                    full_text += text + "\n"  # 페이지 구분을 위해 줄바꿈 추가
        
        # 전체 텍스트를 한 번에 처리
        error_messages = process_data_with_normalization(full_text, required_phrases_stockings, forbidden_words)
        full_text = full_text.rstrip("\n")
    except Exception as e:
        print(f"Error reading PDF: {e}")
    finally:
        return full_text, error_messages

#################################################
#벨트#
def validate_wp_belt1(pdf_file_path):
    try:
        full_text = ""  # 전체 PDF 텍스트를 저장할 변수
        with pdfplumber.open(pdf_file_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                # 페이지 텍스트 추출
                text = page.extract_text()
                if text:
                    full_text += text + "\n"  # 페이지 구분을 위해 줄바꿈 추가

        # 전체 텍스트를 한 번에 처리
        error_messages = process_data_with_normalization(full_text, required_phrases_belt, forbidden_words)
        full_text = full_text.rstrip("\n")

    except Exception as e:
        print(f"Error reading PDF: {e}")
    finally:
        return full_text, error_messages

#############################################################
#자가점착형밴드#
def validate_wp_self_adhesive_bandage1(pdf_file_path):
    try:
        full_text = ""  # 전체 PDF 텍스트를 저장할 변수
        with pdfplumber.open(pdf_file_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                # 페이지 텍스트 추출
                text = page.extract_text()
                if text:
                    full_text += text + "\n"  # 페이지 구분을 위해 줄바꿈 추가

        # 전체 텍스트를 한 번에 처리
        error_messages = process_data_with_normalization(full_text, required_phrases_self_adhesive_bandage, forbidden_words)
        full_text = full_text.rstrip("\n")

        
    except Exception as e:
        print(f"Error reading PDF: {e}")
    finally:
        return full_text, error_messages

#################################################

def validate_wp(file_path, code):
    if code == 1:
        return validate_wp_stockings1(file_path)
    elif code == 2:
        return validate_wp_belt1(file_path)
    elif code ==3:
        return validate_wp_self_adhesive_bandage1(file_path)

# pdf_file_path = r"C:\Users\USER\Desktop\박창선업무\2024-11-27\압박용밴드 형태별 의료기기 표준서식_test\압박용밴드 형태별 의료기기 표준서식\압박용밴드_스타킹형태 서식\사용방법 (3).pdf"
# pdf_file_path1 = r"C:\Users\USER\Desktop\박창선업무\2024-11-27\압박용밴드 형태별 의료기기 표준서식_test\압박용밴드 형태별 의료기기 표준서식\압박용밴드_스타킹형태 서식\모양및구조-작용원리_스타킹.pdf"
# #read_pdf_with_pdfplumber_belt(pdf_file_path)
# read_pdf_with_pdfplumber_stockings1(pdf_file_path1)