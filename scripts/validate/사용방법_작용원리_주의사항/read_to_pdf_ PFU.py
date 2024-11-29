import os
import re
import pdfplumber 
from required_PFU import *
from forbidden_words import *


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
    problems = []
    # 데이터 정규화
    normalized_data = normalize_text(data)
    # 필수 문장 포함 여부 확인
    for phrase_pattern in required_phrases:
        normalized_phrase = normalize_text(phrase_pattern)  # 필수 문장 정규화
        if normalized_phrase not in normalized_data:
            problems.append(f"문제: 필수 문장 '{phrase_pattern}'가 데이터 전체에 포함되지 않았습니다.")

    # 금지 단어 포함 여부 확인
    lines = data.splitlines()
    for line_number, line in enumerate(lines, start=1):
        normalized_line = normalize_text(line)  # 각 줄 정규화
        for word_pattern in forbidden_words:
            normalized_word = normalize_text(word_pattern)  # 금지 단어 정규화
            if re.search(normalized_word, normalized_line):
                problems.append(f"문제: 금지 단어 '{word_pattern}'가 {line_number}번째 줄에 발견되었습니다.")
    # 결과 출력
    if problems:
        print("다음과 같은 문제가 발견되었습니다:")
        for problem in problems:
            print(problem)
    else:
        print("문제 없음. 모든 조건을 만족합니다.")

#############################################################
def read_pdf_with_pdfplumber_stockings1(pdf_file_path):
    try:
        full_text = ""  # 전체 PDF 텍스트를 저장할 변수
        with pdfplumber.open(pdf_file_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                # 페이지 텍스트 추출
                text = page.extract_text()
                if text:
                    full_text += text + "\n"  # 페이지 구분을 위해 줄바꿈 추가

        # 전체 텍스트를 한 번에 처리
        print("\n--- Processing Entire PDF ---\n")
        process_data_with_normalization(full_text, required_phrases_stockings, forbidden_words)
        
        # 전체 텍스트 출력 (선택 사항)
        print("\n--- Full Extracted Text ---\n")
        print(full_text)
        
    except Exception as e:
        print(f"Error reading PDF: {e}")

#################################################

def read_pdf_with_pdfplumber_belt1(pdf_file_path):
    try:
        full_text = ""  # 전체 PDF 텍스트를 저장할 변수
        with pdfplumber.open(pdf_file_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                # 페이지 텍스트 추출
                text = page.extract_text()
                if text:
                    full_text += text + "\n"  # 페이지 구분을 위해 줄바꿈 추가

        # 전체 텍스트를 한 번에 처리
        print("\n--- Processing Entire PDF ---\n")
        process_data_with_normalization(full_text, required_phrases_belt, forbidden_words)
        
        # 전체 텍스트 출력 (선택 사항)
        print("\n--- Full Extracted Text ---\n")
        print(full_text)
        
    except Exception as e:
        print(f"Error reading PDF: {e}")

#############################################################
def read_pdf_with_pdfplumber_self_adhesive_bandage1(pdf_file_path):
    try:
        full_text = ""  # 전체 PDF 텍스트를 저장할 변수
        with pdfplumber.open(pdf_file_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                # 페이지 텍스트 추출
                text = page.extract_text()
                if text:
                    full_text += text + "\n"  # 페이지 구분을 위해 줄바꿈 추가

        # 전체 텍스트를 한 번에 처리
        print("\n--- Processing Entire PDF ---\n")
        process_data_with_normalization(full_text, required_phrases_self_adhesive_bandage, forbidden_words)
        
        # 전체 텍스트 출력 (선택 사항)
        print("\n--- Full Extracted Text ---\n")
        print(full_text)
        
    except Exception as e:
        print(f"Error reading PDF: {e}")

#################################################


pdf_file_path1= r""
read_pdf_with_pdfplumber_self_adhesive_bandage1(pdf_file_path1)
#read_pdf_with_pdfplumber_self_adhesive_bandage1(pdf_file_path)