import os
import re
import pdfplumber 
from forbidden_words import *
def check_forbidden_words(data, forbidden_words):
    """
    데이터에서 금지 단어를 탐지.
    :param data: 필터링된 데이터 (filtered_data 또는 cleaned_tables)
    :param forbidden_words: 금지 단어 리스트
    :return: 금지 단어가 포함된 행 및 단어 목록
    """
    problems = []
    for row_idx, row in enumerate(data, start=1):
        for cell in row:
            if cell:
                for word in forbidden_words:
                    if word in cell:
                        problems.append((row_idx, word, cell))
    return problems


# 금지 단어 탐지 실행
def validate_data_forbidden_words(filtered_data, forbidden_words):
    problems = check_forbidden_words(filtered_data, forbidden_words)
    if problems:
        print("\n[금지 단어 발견]")
        for problem in problems:
            row_idx, word, cell = problem
            print(f"금지 단어 '{word}'가 {row_idx}번째 행에 발견됨: '{cell}'")
    else:
        print("\n금지 단어 없음.")

def preprocess_row(row):
    """
    데이터 행(row)을 전처리하여 공백 및 특수문자를 제거.
    """
    # row가 리스트가 아닐 경우 예외 처리
    if not isinstance(row, list):
        raise TypeError(f"전처리 중 예상치 못한 데이터 형식 발생: {row}")
    return [
        re.sub(r'[\u200b\u00a0\u3000]', '', cell.replace('\n', ' ').replace('\r', '').strip()) if cell else ""
        for cell in row
    ]

def clean_table_data(tables):
    """
    표 데이터에서 줄바꿈 제거 및 None 값을 처리하여 데이터를 정리.
    """
    cleaned_tables = []
    for table in tables:
        cleaned_table = []
        for row in table:
            cleaned_row = []
            for cell in row:
                if cell is not None:
                    cleaned_row.append(cell.replace('\n', ' ').strip())  # 줄바꿈 제거 및 공백 정리
                else:
                    cleaned_row.append("")  # None 값을 빈 문자열로 대체
            cleaned_table.append(cleaned_row)
        cleaned_tables.append(cleaned_table)
    return cleaned_tables


def map_data_to_fixed_items1(tables):
    """
    데이터가 fixed_items에 매핑될 경우 해당 값을 채우고,
    빈 값을 이전 행의 값으로 처리.
    :param tables: 정리된 표 데이터
    :param fixed_header: 고정된 헤더 값
    :param fixed_items: 고정된 항목 값
    :return: 매핑된 데이터
    """
    mapped_data = []
    for table in tables:
        if not table:
            continue
        for idx, row in enumerate(table):
            row = preprocess_row(row)  # 데이터 전처리
            mapped_data.append(row)
    return mapped_data


def process_pdf(file_path):
    """
    PDF 파일을 처리하여 모든 테이블 데이터를 한 번에 출력.
    :param file_path: PDF 파일 경로
    :param fixed_header: 고정된 헤더 값
    :param fixed_items: 고정된 항목 값
    """
    with pdfplumber.open(file_path) as pdf:
        all_tables = []
        # 모든 페이지의 데이터를 처리하고 병합
        for page in pdf.pages:
            page_tables = page.extract_tables()
            if page_tables:
                all_tables.extend(page_tables)

        if not all_tables:
            print("표 데이터를 찾을 수 없습니다.")
            return
        # 테이블 데이터 전처리 및 매핑
        cleaned_tables = clean_table_data(all_tables)
        filtered_data = map_data_to_fixed_items1(cleaned_tables)
        # 금지 단어 검증        
        validate_data_forbidden_words(filtered_data, forbidden_words)
        # 최종 결과 출력
        print("\n[최종 처리된 데이터]")
        for table in filtered_data:
            print(table)

    # return 들어갈 자리

pdf_file_path = r""

process_pdf(pdf_file_path)