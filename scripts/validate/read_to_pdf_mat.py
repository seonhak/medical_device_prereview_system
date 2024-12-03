import os
import re
import pdfplumber
from .forbidden_words import *
from .save_error_to_txt import *
# 원재료
error_messages = []  # 모든 오류 메시지를 저장할 리스트
fixed_header = ['일련번호', '부분품의명칭', '원재료명또는성분명', '규격', '분량', '비고(인체접촉여부및접촉부위첨가목적)']
    # return 들어갈 자리
fixed_items = [
        ['원재료 공통 기재사항', '일반명', '', '', ''],
        ['원재료 공통 기재사항', '화학명', '', '', ''],
        ['원재료 물리‧화학정보', '구조식', '', '', ''],
        ['원재료 물리‧화학정보', 'CAS 번호(존재 시)', '', '', ''],
        ['원재료 물리‧화학정보', '물질 특성', '', '', ''],
        ['원재료 제조자 정보', '제조자', '', '', ''],
        ['원재료 제조자 정보', '제품명 또는 상품명', '', '', ''],
        ['원재료 제조자 정보', '제품번호 또는 모델명', '', '', '']
    ]
valid_keywords = [
            "원재료공통기재사항",
            "원재료제조자정보",
            "원재료물리‧화학정보"
    ]
valid_keywords2 = [
    "일반명",
    "화학명"
]
valid_keywords3 = [
    "구조식",
    "CAS번호(존재시)",
    "물질특성"
]
valid_keywords4 =[
    "제조자",
    "제품명또는상품명",
    "제품번호또는모델명"
]

def check_invalid_words(data_list):
    """
    데이터 리스트에서 사용 불가 단어를 확인합니다.
    :param data_list: 입력 데이터 리스트 (각각 문자열)
    :param invalid_words: 사용 불가 단어 리스트
    :return: 사용 불가 단어가 포함된 항목 리스트
    """
    for data in data_list:
        for row in data:
            if not isinstance(row, str):  # data가 문자열인지 확인
                print(f"경고: '{row}'는 문자열이 아니므로 건너뜁니다.")
                continue
            for invalid_word in forbidden_words:
                if invalid_word in row:  # 문자열 비교
                    error_messages.append((row, invalid_word))
                    continue  # 하나의 단어만 일치해도 중단

def preprocess_row(row):
    """
    데이터 행(row)을 전처리하여 공백, 특수문자 및 불필요한 줄바꿈 제거.
    문자열, 리스트, None을 모두 안전하게 처리.
    """
    # None 처리
    if row is None:
        return []

    # 문자열이 들어오면 리스트로 변환
    if isinstance(row, str):
        row = [row]

    # row가 리스트가 아닐 경우 예외 처리
    if not isinstance(row, list):
        raise TypeError(f"전처리 중 예상치 못한 데이터 형식 발생: {row}")

    # 리스트 요소별 전처리
    return [
        re.sub(r'[\u200b\u00a0\u3000\s]', '', cell.replace('\n', '').replace('\r', '').replace(',', '').strip()) if cell else ""
        for cell in row
    ]


def clean_and_filter_list(data):
    """
    데이터를 정리하고 유효한 값만 반환.
    - None 값을 빈 리스트로 처리
    - 문자열 또는 리스트를 처리 가능
    - 리스트가 아닌 경우 무시하고 넘어감
    """
    # None 값 처리
    if data is None:
        return []

    # 문자열을 리스트로 변환
    if isinstance(data, str):
        data = [data]

    # 리스트가 아닌 경우 건너뛰기
    if not isinstance(data, list):
        print(f"경고: 입력 데이터가 리스트가 아님, 건너뜀: {data}")
        return []

    # 리스트 값 전처리
    cleaned_list = []
    for item in data:
        if item is None:  # None 값 무시
            continue
        cleaned_item = re.sub(r'\s+', '',str(item))  # 공백 제거
        if cleaned_item:  # 비어 있지 않은 값만 추가
            cleaned_list.append(cleaned_item)

    return cleaned_list

def validate_mat(file_path):
    
    all_tables = []
    all_tables1= []

    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=0):
            page_tables = page.extract_tables()
            for table_number,table in enumerate(page_tables, start=0):
                first_row = preprocess_row(table[0])
                if first_row == fixed_header :
                    for table_data in table[1:]:
                        a = clean_and_filter_list(table_data)
                        if ( len(a) > 0 and
                            a[0] is not None and str(a[0]).isdigit() and
                            a[4] is not None and str(a[4]).isdigit()
                        ):                            
                            all_tables.append(a)
                            # print(a[3])
                            # print(all_tables[0][3])
                            continue
                        elif len(all_tables) == 0:
                            continue
                        elif len(a) > 0 and a[0] in all_tables[0][3]:
                            all_tables1.append(a)
                        elif len(a) > 0 and a[0] in valid_keywords:
                            all_tables1.append(a)
                        elif len(a) > 0 and a[0] in valid_keywords2:
                            a.insert(0,'원재료공통기재사항')
                            all_tables1.append(a)
                        elif len(a) > 0 and a[0] in valid_keywords3:
                            a.insert(0,'원재료제조자정보')
                            all_tables1.append(a)
                        elif len(a) > 0 and a[0] in valid_keywords4:
                            a.insert(0,'제품번호또는모델명')
                            all_tables1.append(a)
                        elif a == '':
                            error_message = (
                                f'데이터가 비어 있습니다 - {a}'
                            )
                            error_messages.append(error_message)                                                        
                        else :
                            # error_message = (
                            #     f'일련번호 또는 분량이 비어있거나 잘못된 형태로 입력되었습니다 - {a}'
                            # )
                            # error_messages.append(error_message)
                            continue                    
                else:
                    error_message = (
                        f'- 형식이 옳바르지 않습니다 - {first_row}'
                    )
                    error_messages.append(error_message)
                    continue

        a = float(0)
        b = all_tables[0][0]
        for data in all_tables:
            if b == data[0]:
                a = a+float(data[4])
            elif not data[0] == b:
                if not a == 100.0:
                    error_message = (
                        f'합이 100이 아닙니다 - {a}'
                    )
                    error_messages.append(error_message)
                    # a 초기화
                a = float(data[4])
                b = data[0]  
        if not a == 100.0:
            error_message = (
                f'합이 100이 아닙니다 - {a}'
            )
            error_messages.append(error_message)
            # a 초기화
        a = float(data[4]) 
        b = data[0]  
    # 사용 불가 단어 검증 로직 #
    check_invalid_words(all_tables1)
    check_invalid_words(all_tables)   
    # for error in error_messages:
    #     print(error)
    all_tables.append(all_tables1)
    # for row in all_tables1:
    #     all_tables.append(all_tables1)
    
    return all_tables, error_messages