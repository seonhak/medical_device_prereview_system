import os
import re
import pdfplumber 
from .required_pfu import *
from .forbidden_words import *
from .save_error_to_txt import save_error_to_file  # 에러 저장 함수
from .validate_utils import *
# 사용 시 주의사항

def process_data_with_normalization(data, required_phrases, forbidden_words):
    error_messages = []
    # 데이터 정규화
    normalized_data = normalize_text(data)
    # 필수 문장 포함 여부 확인
    # 필수 문장이 하나도 포함되지 않은 경우 에러 메시지 추가
    error_messages.extend(validate_include_phrase(required_phrases, normalized_data))
    # 필수 공통 문장이 하나도 포함되지 않은 경우 에러 메시지 추가
    error_messages.extend(validate_include_phrase(common_phrases, normalized_data))
    # 금지 단어 포함 여부 확인
    error_messages.extend(check_invalid_words(normalized_data))
    return error_messages

#############################################################
# 스타킹 #
def validate_pfu_stockings1(pdf_file_path):
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
        error_messages.append(e)
    finally:
        return full_text, error_messages

#################################################

def validate_pfu_belt1(pdf_file_path):
#벨트#
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
        error_messages.append(e)
    finally:
        return full_text, error_messages

#############################################################
#자기점착형#
def validate_pfu_self_adhesive_bandage1(pdf_file_path):
    try:
        full_text = ""  # 전체 PDF 텍스트를 저장할 변수
        with pdfplumber.open(pdf_file_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                # 페이지 텍스트 추출
                text = page.extract_text()
                if text:
                    full_text += text + "\n"  # 페이지 구분을 위해 줄바꿈 추가
        error_messages = process_data_with_normalization(full_text, required_phrases_self_adhesive_bandage, forbidden_words)
        full_text = full_text.rstrip("\n")
        
    except Exception as e:
        print(f"Error reading PDF: {e}")
        error_messages.append(e)
    finally:
        return full_text, error_messages

#################################################

def validate_pfu(file_path, code):
    if code == 1:
        return validate_pfu_stockings1(file_path)
    elif code == 2:
        return validate_pfu_belt1(file_path)
    elif code ==3:
        return validate_pfu_self_adhesive_bandage1(file_path)
