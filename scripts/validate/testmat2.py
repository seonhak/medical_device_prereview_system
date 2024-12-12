import os
import re
import pdfplumber
# from .forbidden_words import *
from forbidden_words import *
import unicodedata
# from save_error_to_txt import *

fixed_header = ['일련번호', '부분품의명칭', '원재료명또는성분명', '규격', '분량', '비고(인체접촉여부및접촉부위첨가목적)']
    # return 들어갈 자리
fixed_items = [
        ['원재료공통기재사항', '일반명', '', '', ''],
        ['원재료공통기재사항', '화학명', '', '', ''],
        ['원재료물리‧화학정보', '구조식', '', '', ''],
        ['원재료물리‧화학정보', 'CAS번호(존재시)', '', '', ''],
        ['원재료물리‧화학정보', '물질특성', '', '', ''],
        ['원재료제조자정보', '제조자', '', '', ''],
        ['원재료제조자정보', '제품명또는상품명', '', '', ''],
        ['원재료제조자정보', '제품번호또는모델명', '', '', '']
    ]
valid_keywords0 = [
            "원재료 공통 기재사항",
            "원재료 제조자 정보",
            "원재료 물리‧화학정보"
    ]
valid_keywords = [
            "원재료공통기재사항",
            "원재료제조자정보",
            "원재료물리‧화학정보",
            "일련번호"
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
valid_keywords5 = [
    "일반명",
    "화학명",
    "구조식",
    "CAS번호(존재시)",
    "물질특성",
    "제조자",
    "제품명또는상품명",
    "제품번호또는모델명"
]

def clean_text(text):
    """텍스트에서 공백 및 줄바꿈을 제거하여 비교를 위한 클리닝."""
    return text.replace('\n', '').replace(' ', '').strip() if isinstance(text, str) else ""

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
                    error_message = (
                        f'사용 불가 단어가 확인되었습니다. 사용자 데이터 : {row}  사용 불가 단어 : {invalid_word}'
                    )
                    error_messages.append(error_message)
                    continue  # 하나의 단어만 일치해도 중단

import re

def preprocess_row(row):
    """
    데이터 행(row)을 전처리하여 공백, 특수문자 및 불필요한 줄바꿈 제거.
    문자열, 숫자, 리스트, 튜플, None을 모두 안전하게 처리.
    입력이 튜플인 경우 리스트로 변환 후 처리.
    """
    # None 처리
    if row is None:
        return []

    # 문자열이 들어오면 리스트로 변환
    if isinstance(row, str):
        row = [row]

    # 튜플을 리스트로 변환
    if isinstance(row, tuple):
        row = list(row)

    # row가 리스트가 아닐 경우 예외 처리
    if not isinstance(row, list):
        raise TypeError(f"전처리 중 예상치 못한 데이터 형식 발생: {row}")

    # 리스트 요소별 전처리
    return [
        re.sub(r'[\u200b\u00a0\u3000\s]', '', str(cell).replace('\n', '').replace('\r', '').replace(',', '').strip()) if cell else ""
        for cell in row
    ]

def clean_and_filter_list(data):
    """
    데이터를 정리하고 유효한 값만 반환.
    - None 값을 빈 리스트로 처리
    - 문자열, 리스트, 튜플을 처리 가능
    - 리스트나 튜플이 아닌 경우 무시하고 넘어감
    """
    # None 값 처리
    if data is None:
        return []

    # 문자열을 리스트로 변환
    if isinstance(data, str):
        data = [data]

    # 리스트 또는 튜플인지 확인
    if not isinstance(data, (list, tuple)):
        print(f"경고: 입력 데이터가 리스트나 튜플이 아님, 건너뜀: {data}")
        return []

    # 리스트나 튜플로 처리
    if isinstance(data, (list, tuple)):
        cleaned_list = []
        for item in data:
            if item is None:  # None 값 무시
                continue
            # 문자열로 변환
            item = str(item)
            # 유니코드 정규화(NFKC)로 유사 문자 통일
            item = unicodedata.normalize('NFKC', item)
            # 공백, %, `·`, `‧` 제거
            cleaned_item = re.sub(r'[\s\n]+|%', '', item)

            if cleaned_item:  # 비어 있지 않은 값만 추가
                cleaned_list.append(cleaned_item)
        return cleaned_list

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
def validate_mat(file_path):
    error_messages = []  # 모든 오류 메시지를 저장할 리스트
    result_tables = []
    all_tables = []
    all_tables1 = []
    all_tables2 = []
    temp_data = []
    temp_data1 =[]
    try:
        with pdfplumber.open(file_path) as pdf:
            # 페이지 0번부터 읽기를 시작한다 page : 총 페이지 수 / page_number : 페이지 번호 출력
            for page_number , page in enumerate(pdf.pages, start=0):
                page_tables = page.extract_tables()
                # 페이지 0번에서 읽어온 테이블(표)를 for문을 통해 갖고 온다
                if not page_tables:  # 테이블이 없으면 다음 페이지로 넘어감
                    continue   
                for table_number,tables in enumerate(page_tables,start=0):
                    # 페이지에서 읽어온 테이블의 첫 번째 행
                    first_row = preprocess_row(tables[0])
                    clean_first_row = clean_and_filter_list(first_row)
                    try:
                        if len(first_row)>6:
                            error_message = (
                                f' 신고서류 내 오류 내용 : {first_row} \r\n 오류 발생 요인 : 양식에서 제공된 표와 다르게 인식되고 있습니다. \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                            )
                            error_messages.append(error_message)
                        
                        elif first_row == fixed_header :
                            # table_clean = clean_and_filter_list(tables)
                        # print(table_clean)
                            for table1 in tables[1:]:
                                clean_table1 = clean_and_filter_list(table1)
                                if len(clean_table1)>0 and clean_table1[0].isdigit():
                                    for row in table1:
                                        if row == None or str(row).strip() == '':
                                            error_message = (
                                                f' 신고서류 내 오류 내용 : {table1}\r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                            )
                                            error_messages.append(error_message)
                                            if len(temp_data) > 0 :
                                                if table1[5] == None or str(table1[5]).strip() =='':
                                                    clean_table1.insert(5,temp_data[5])
                                            elif len(temp_data) == 0:
                                                if table1[5] == None or str(table1[5]).strip() =='':
                                                    clean_table1.insert(5,'검증오류방지')
                                                    if table1[4] == None or str(table1[4]).strip() =='':
                                                        clean_table1.insert(4,float(0))
                                                    if table1[3] == None or str(table1[3]).strip() =='':
                                                        clean_table1.insert(3,'검증오류방지')
                                                        break
                                    all_tables.append(clean_table1)
                                    temp_data = clean_table1
                                    temp_data1.append(temp_data[3])
                                elif len(clean_table1) == 1 and not clean_table1[0] in (valid_keywords2 + valid_keywords3 + valid_keywords4):
                                    all_tables2.append(clean_table1)
                                elif len(table1) > 0 and (
                                    (len(clean_table1) > 0 and clean_table1[0] in valid_keywords2) or
                                    (len(clean_table1) > 1 and clean_table1[1] in valid_keywords2) or
                                    (len(clean_table1) > 0 and clean_table1[0] in '원재료공통기재사항')
                                ):
                                # elif len(table1) > 0 and (len(clean_table1)>0 and clean_table1[0] in valid_keywords2) or (len(clean_table1)> 1 and clean_table1[1] in valid_keywords2 or clean_table1[0] in '원재료공통기재사항'):
                                    if table1[4] == None or str(table1[4]).strip() == '':
                                            error_message = (
                                                f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                            )
                                            error_messages.append(error_message)     
                                    if len(clean_table1) < 3 and not (clean_table1[0] == '원재료공통기재사항'):
                                        clean_table1.insert(0,'원재료공통기재사항')
                                    all_tables1.append(clean_table1)
                                elif (
                                    len(table1) > 0 and (
                                        (len(clean_table1) > 0 and clean_table1[0] in valid_keywords3) or
                                        (len(clean_table1) > 1 and clean_table1[1] in valid_keywords3) or
                                        (len(clean_table1) > 0 and clean_table1[0] in '원재료물리‧화학정보')
                                    )
                                ):                                
                                # elif (len(table1) > 0 and (len(clean_table1)>0 and clean_table1[0] in valid_keywords3) or (len(clean_table1)>1 and clean_table1[1] in valid_keywords3) or clean_table1[0] in '원재료물리‧화학정보'):
                                    if table1[4] == None or str(table1[4]).strip() == '':
                                            error_message = (
                                                f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                            )
                                            error_messages.append(error_message)
                                    # print(type(clean_table1[0]))                                  
                                    if len(clean_table1) < 3 and not (clean_table1[0] == '원재료물리‧화학정보'):
                                        clean_table1.insert(0,'원재료물리‧화학정보')
                                    all_tables1.append(clean_table1)                                   
                                elif (
                                    len(table1) > 0 and (
                                        (len(clean_table1) > 0 and clean_table1[0] in valid_keywords4) or
                                        (len(clean_table1) > 1 and clean_table1[1] in valid_keywords4) or
                                        (len(clean_table1) > 0 and clean_table1[0] in '원재료제조자정보')
                                    )
                                ):                                    
                                # elif len(table1) > 0 and (len(clean_table1)>0 and clean_table1[0] in valid_keywords4) or (len(clean_table1)>1 and clean_table1[1] in valid_keywords4 or clean_table1[0] in '원재료제조자정보'):
                                    if table1[4] == None or str(table1[4]).strip() == '':
                                            error_message = (
                                                f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                            )
                                            error_messages.append(error_message)                                  
                                    if len(clean_table1) < 3 and  not (clean_table1[0] == '원재료제조자정보'):
                                        clean_table1.insert(0,'원재료제조자정보')
                                    all_tables1.append(clean_table1)    
                                elif table1[0] == None or '':
                                    clean_table1.insert(0,temp_data[0])
                                    if table1[1] == None or '':
                                        clean_table1.insert(1,temp_data[1])
                                    if table1[5] == None or '':
                                        clean_table1.insert(5,temp_data[5])
                                    if ((table1[2] in (None, '')) or (table1[3] in (None, '')) or (table1[4] in (None, ''))):
                                        error_message = (
                                            f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                        )
                                        error_messages.append(error_message)
                                        if table1[2] in (None,''):
                                            clean_table1.insert(2,'검증오류방지')
                                        if table1[3] in (None,''):
                                            clean_table1.insert(3,'검증오류방지')
                                        if table1[4] in (None,''):
                                            clena_table1.insert(4,float(0))
                                        if table1[5] in (None,''):
                                            clean_table1.insert(5,'검증오류방지')
                                            all_tables.append(clean_table1)                                            
                                        else:
                                            all_tables.append(clean_table1)
                                    elif any('검증오류방지' in item for item in clean_table1):
                                        error_message = (
                                         f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'   
                                        )
                                        error_messages.append(error_message)
                                    else:
                                        all_tables.append(clean_table1)
                                elif table1[0] == '일련번호':
                                    continue
                                elif len(clean_table1) == 0:
                                    error_message = (
                                        f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                    )
                                    error_messages.append(error_message)
                                    continue
                                # 분기 추가
                                elif isinstance(table1[0],str):
                                    # error_message = (
                                    #     f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 일련 번호가 숫자(특수문자 금지) 또는 신고서류 양식과 일치하지 않습니다 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                    # )
                                    for row in table1:
                                        if row == None or str(row).strip() == '':
                                            error_message = (
                                                f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                            )
                                            error_messages.append(error_message)
                                            if len(temp_data) > 0 :
                                                if table1[5] == None or str(table1[5]).strip() =='':
                                                    clean_table1.insert(5,temp_data[5])
                                            elif len(temp_data) == 0:
                                                if table1[5] == None or str(table1[5]).strip() =='':
                                                    clean_table1.insert(5,'검증오류방지')
                                                    if table1[4] == None or str(table1[4]).strip() =='':
                                                        clean_table1.insert(4,float(0))
                                                    if table1[3] == None or str(table1[3]).strip() =='':
                                                        clean_table1.insert(3,'검증오류방지')
                                                        break
                                                if table1[4] == None or str(table1[4]).strip() == '':
                                                    clean_table1.insert(4,float(0))
                                                if table1[3] == None or str(table1[3]).strip() == '':
                                                    clean_table1.insert(3,'검증오류방지')
                                                if table1[2] == None or str(table1[2]).strip() == '':
                                                    clean_table1.insert(2,'검증오류방지')
                                                if table1[1] == None or str(table1[1]).strip() == '':
                                                    clean_table1.insert(1,'검증오류방지')
                                                if table1[0] == None or str(table1[0]).strip() == '':
                                                    clean_table1.insert(0,'검증오류방지')
                                    all_tables.append(clean_table1)
                                    temp_data = clean_table1
                                    temp_data1.append(temp_data[3])
                                elif len(clean_table1) == 1 and not clean_table1[0] in (valid_keywords2 + valid_keywords3 + valid_keywords4):
                                    all_tables2.append(clean_table1)
                                elif (len(table1) > 0 and (len(clean_table1)>0 and clean_table1[0] in valid_keywords2) or (len(clean_table1)> 1 and clean_table1[1] in valid_keywords2 or clean_table1[0] in '원재료공통기재사항')):
                                    if table1[4] == None or str(table1[4]).strip() == '':
                                            error_message = (
                                                f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                            )
                                            error_messages.append(error_message)     
                                    if len(clean_table1) < 3 and not (clean_table1[0] == '원재료공통기재사항'):
                                        clean_table1.insert(0,'원재료공통기재사항')
                                    all_tables1.append(clean_table1)
                                elif (len(table1) > 0 and (len(clean_table1)>0 and clean_table1[0] in valid_keywords3) or (len(clean_table1)>1 and clean_table1[1] in valid_keywords3) or clean_table1[0] in '원재료물리‧화학정보'):
                                    if table1[4] == None or str(table1[4]).strip() == '':
                                            error_message = (
                                                f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                            )
                                            error_messages.append(error_message)
                                    # print(type(clean_table1[0]))                                  
                                    if len(clean_table1) < 3 and not (clean_table1[0] == '원재료물리‧화학정보'):
                                        clean_table1.insert(0,'원재료물리‧화학정보')
                                    all_tables1.append(clean_table1)                                   
                                elif len(table1) > 0 and (len(clean_table1)>0 and clean_table1[0] in valid_keywords4) or (len(clean_table1)>1 and clean_table1[1] in valid_keywords4 or clean_table1[0] in '원재료제조자정보'):
                                    if table1[4] == None or str(table1[4]).strip() == '':
                                            error_message = (
                                                f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                            )
                                            error_messages.append(error_message)                                  
                                    if len(clean_table1) < 3 and  not (clean_table1[0] == '원재료제조자정보'):
                                        clean_table1.insert(0,'원재료제조자정보')
                                    all_tables1.append(clean_table1)    
                                elif table1[0] == None or '':
                                    clean_table1.insert(0,temp_data[0])
                                    if table1[1] == None or '':
                                        clean_table1.insert(1,temp_data[1])
                                    if table1[5] == None or '':
                                        clean_table1.insert(5,temp_data[5])
                                    if ((table1[2] in (None, '')) or (table1[3] in (None, '')) or (table1[4] in (None, ''))):
                                        error_message = (
                                            f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                        )
                                        error_messages.append(error_message)
                                        if table1[2] in (None,''):
                                            clean_table1.insert(2,'검증오류방지')
                                        if table1[3] in (None,''):
                                            clean_table1.insert(3,'검증오류방지')
                                        if table1[4] in (None,''):
                                            clena_table1.insert(4,float(0))
                                        if table1[5] in (None,''):
                                            clean_table1.insert(5,'검증오류방지')
                                            all_tables.append(clean_table1)                                            
                                        else:
                                            all_tables.append(clean_table1)
                                    else:
                                        all_tables.append(clean_table1)
                                else:
                                    error_message = (
                                        f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 일련 번호가 숫자(특수문자 금지) 또는 신고서류 양식과 일치하지 않습니다 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                    )
                                    error_messages.append(error_message)                               
                        elif len(first_row)>1 and first_row[0] in valid_keywords or first_row[1] in valid_keywords5:
                            for table1 in tables:
                                clean_table1 = clean_and_filter_list(table1)                            
                                if clean_table1[0].isdigit():
                                    for row in table1:
                                        if row == None or str(row).strip() == '':
                                            error_message = (
                                                f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                            )
                                            error_messages.append(error_message)
                                            if len(temp_data) > 0 :
                                                if table1[5] == None or str(table1[5]).strip() =='':
                                                    clean_table1.insert(5,temp_data[5])
                                            elif len(temp_data) == 0:
                                                clean_table1.insert(5,'검증오류방지')                                                                                
                                    all_tables.append(clean_table1)
                                    temp_data = clean_table1
                                    temp_data1.append(temp_data[3])
                                elif len(clean_table1) == 1 and not clean_table1[0] in (valid_keywords2 + valid_keywords3 + valid_keywords4):
                                    all_tables2.append(clean_table1)
                                elif (len(table1) > 0 and (len(clean_table1)>0 and clean_table1[0] in valid_keywords2) or (len(clean_table1)>1 and clean_table1[1] in valid_keywords2 or clean_table1[0] in '원재료공통기재사항')):
                                    if len(table1) == 6:
                                        if table1[4] == None or str(table1[4]).strip() == '':
                                                error_message = (
                                                    f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                                )
                                                error_messages.append(error_message)     
                                        if not (clean_table1[0] == '원재료공통기재사항'):
                                            clean_table1.insert(0,'원재료공통기재사항')
                                        all_tables1.append(clean_table1)
                                    elif len(table1) == 3:
                                        if table1[2] == None or str(table1[2]).strip() == '':
                                                error_message = (
                                                    f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                                )
                                                error_messages.append(error_message)     
                                        if not (clean_table1[0] == '원재료공통기재사항'):
                                            clean_table1.insert(0,'원재료공통기재사항')
                                        all_tables1.append(clean_table1)                                    
                                elif (len(table1) > 0 and (len(clean_table1)>0 and clean_table1[0] in valid_keywords3) or (len(clean_table1)>1 and clean_table1[1] in valid_keywords3) or clean_table1[0] in '원재료물리‧화학정보'):                                    
                                    if len(table1) == 3:
                                        if table1[2] == None or str(table1[2]).strip() == '':
                                                error_message = (
                                                    f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                                )
                                                error_messages.append(error_message)
                                        if not (clean_table1[0] == '원재료물리‧화학정보'):
                                            clean_table1.insert(0,'원재료물리‧화학정보')
                                        all_tables1.append(clean_table1)
                                    elif len(table1) == 6:
                                        if table1[4] == None or str(table1[4]).strip() == '':
                                                error_message = (
                                                    f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                                )
                                                error_messages.append(error_message)
                                        if not (clean_table1[0] == '원재료물리‧화학정보'):
                                            clean_table1.insert(0,'원재료물리‧화학정보')
                                        all_tables1.append(clean_table1)                                                                         
                                elif len(table1) > 0 and (len (clean_table1)>0 and clean_table1[0] in valid_keywords4)  or (len(clean_table1)>1 and clean_table1[1] in valid_keywords4 or clean_table1[0] in '원재료제조자정보'):
                                    if len(table1) == 3:
                                        if table1[2] == None or str(table1[2]).strip() == '':
                                                error_message = (
                                                    f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                                )
                                                error_messages.append(error_message)                                  
                                        if not (clean_table1[0] == '원재료제조자정보'):
                                            clean_table1.insert(0,'원재료제조자정보')
                                        all_tables1.append(clean_table1)
                                    elif  len(table1) == 6:
                                        if table1[4] == None or str(table1[4]).strip() == '':
                                                error_message = (
                                                    f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                                )
                                                error_messages.append(error_message)                                  
                                        if not (clean_table1[0] == '원재료제조자정보'):
                                            clean_table1.insert(0,'원재료제조자정보')
                                        all_tables1.append(clean_table1)                                     
                                elif table1[0] == None or '':
                                    clean_table1.insert(0,temp_data[0])
                                    if table1[1] == None or '':
                                        clean_table1.insert(1,temp_data[1])
                                    if table1[5] == None or '':
                                        clean_table1.insert(5,temp_data[5])
                                    if table1[3] == None or '':
                                        clean_table1.insert(3,'검증오류방지')
                                    if table1[4] == None or '':
                                        clean_table1.insert(4,float(0))                                        
                                    all_tables.append(clean_table1)       
                                elif table1[0] == '일련번호':
                                    continue        
                                elif len(clean_table1) == 0:
                                    error_message = (
                                        f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                    )
                                    # error_messages.append(error_message)
                                    continue                                                                                                 
                                else:
                                    error_message = (
                                        f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 일련 번호가 숫자(특수문자 금지) 또는 신고서류 양식과 일치하지 않습니다 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                    )
                                    error_messages.append(error_message)                                
                                # table1 = clean_and_filter_list(table1)
                                # if table1[0].isdigit():
                                #     all_tables.append(table1)
                                # elif len(table1) > 0 and (table1[0] in valid_keywords2 or (len(table1) > 1 and table1[1] in valid_keywords2)):
                                #     all_tables2.append(table1)
                                # elif len(table1) > 0 and (table1[0] in valid_keywords2 or (len(table1) > 1 and table1[1] in valid_keywords2)):
                                #     if not (table1[0] == '원재료공통기재사항'):
                                #         table1.insert(0,'원재료공통기재사항')
                                #     all_tables1.append(table1)
                                # elif len(table1) > 0 and (table1[0] in valid_keywords3 or (len(table1) > 1 and table1[1] in valid_keywords3)):
                                #     if(table1[0] == '원재료물리‧화학정보'):
                                #         all_tables1.append(table1)
                                #     else:
                                #         table1.insert(0,'원재료물리‧화학정보')
                                #         all_tables1.append(table1)                                    
                                # elif len(table1) > 0 and (table1[0] in valid_keywords4 or (len(table1) > 1 and table1[1] in valid_keywords4)):
                                #     if(table1[0] == '원재료제조자정보'):
                                #         all_tables1.append(table1)
                                #     else:
                                #         table1.insert(0,'원재료제조자정보')
                                #         all_tables1.append(table1)    
                                # else:
                                #     pass      
                        elif len(first_row) > 6:
                            error_message = (
                                f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 양식에서 제공된 표와 다르게 인식되고 있습니다. \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다' 
                            )
                            error_messages.append(error_message)
                        elif len(clean_first_row) == 1 :
                            for table1 in tables[1:]:
                                clean_table1 = clean_and_filter_list(table1)                            
                                if clean_table1[0].isdigit():
                                    for row in table1:
                                        if row == None or str(row).strip() == '':
                                            error_message = (
                                                f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                            )
                                            error_messages.append(error_message)
                                            if len(temp_data) > 0 :
                                                if table1[5] == None or str(table1[5]).strip() =='':
                                                    clean_table1.insert(5,temp_data[5])
                                            elif len(temp_data) == 0:
                                                clean_table1.insert(5,'검증오류방지')                                                                                
                                    all_tables.append(clean_table1)
                                    temp_data = clean_table1
                                    temp_data1.append(temp_data[3])
                                elif len(clean_table1) == 1 and not clean_table1[0] in (valid_keywords2 + valid_keywords3 + valid_keywords4):
                                    all_tables2.append(clean_table1)
                                elif (len(table1) > 0 and (len(clean_table1)>0 and clean_table1[0] in valid_keywords2) or (len(clean_table1)>1 and clean_table1[1] in valid_keywords2 or clean_table1[0] in '원재료공통기재사항')):
                                    if len(table1) == 6:
                                        if table1[4] == None or str(table1[4]).strip() == '':
                                                error_message = (
                                                    f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                                )
                                                error_messages.append(error_message)     
                                        if not (clean_table1[0] == '원재료공통기재사항'):
                                            clean_table1.insert(0,'원재료공통기재사항')
                                        all_tables1.append(clean_table1)
                                    elif len(table1) == 3:
                                        if table1[2] == None or str(table1[2]).strip() == '':
                                                error_message = (
                                                    f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                                )
                                                error_messages.append(error_message)     
                                        if not (clean_table1[0] == '원재료공통기재사항'):
                                            clean_table1.insert(0,'원재료공통기재사항')
                                        all_tables1.append(clean_table1)                                    
                                elif (len(table1) > 0 and (len(clean_table1)>0 and clean_table1[0] in valid_keywords3) or (len(clean_table1)>1 and clean_table1[1] in valid_keywords3) or clean_table1[0] in '원재료물리‧화학정보'):                                    
                                    if len(table1) == 3:
                                        if table1[2] == None or str(table1[2]).strip() == '':
                                                error_message = (
                                                    f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                                )
                                                error_messages.append(error_message)
                                        if not (clean_table1[0] == '원재료물리‧화학정보'):
                                            clean_table1.insert(0,'원재료물리‧화학정보')
                                        all_tables1.append(clean_table1)
                                    elif len(table1) == 6:
                                        if table1[4] == None or str(table1[4]).strip() == '':
                                                error_message = (
                                                    f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                                )
                                                error_messages.append(error_message)
                                        if not (clean_table1[0] == '원재료물리‧화학정보'):
                                            clean_table1.insert(0,'원재료물리‧화학정보')
                                        all_tables1.append(clean_table1)                                                                         
                                elif len(table1) > 0 and (len (clean_table1)>0 and clean_table1[0] in valid_keywords4)  or (len(clean_table1)>1 and clean_table1[1] in valid_keywords4 or clean_table1[0] in '원재료제조자정보'):
                                    if len(table1) == 3:
                                        if table1[2] == None or str(table1[2]).strip() == '':
                                                error_message = (
                                                    f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                                )
                                                error_messages.append(error_message)                                  
                                        if not (clean_table1[0] == '원재료제조자정보'):
                                            clean_table1.insert(0,'원재료제조자정보')
                                        all_tables1.append(clean_table1)
                                    elif  len(table1) == 6:
                                        if table1[4] == None or str(table1[4]).strip() == '':
                                                error_message = (
                                                    f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                                )
                                                error_messages.append(error_message)                                  
                                        if not (clean_table1[0] == '원재료제조자정보'):
                                            clean_table1.insert(0,'원재료제조자정보')
                                        all_tables1.append(clean_table1)                                     
                                elif table1[0] == None or '':
                                    clean_table1.insert(0,temp_data[0])
                                    if table1[1] == None or '':
                                        clean_table1.insert(1,temp_data[1])
                                    if table1[5] == None or '':
                                        clean_table1.insert(5,temp_data[5])
                                    if table1[3] == None or '':
                                        clean_table1.insert(3,'검증오류방지')
                                    if table1[4] == None or '':
                                        clean_table1.insert(4,float(0))                                        
                                    all_tables.append(clean_table1)       
                                elif table1[0] == '일련번호':
                                    continue        
                                elif len(clean_table1) == 0:
                                    error_message = (
                                        f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                    )
                                    error_messages.append(error_message)
                                    continue                                                                                                 
                                else:
                                    error_message = (
                                        f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 일련 번호가 숫자(특수문자 금지) 또는 신고서류 양식과 일치하지 않습니다 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                    )
                                    error_messages.append(error_message)                               
                        elif len(temp_data1) > 0:
                            for temp in temp_data1:
                                if temp in first_row[0]:
                                    for table1 in tables:
                                        clean_table1 = clean_and_filter_list(table1)
                                        if clean_table1[0].isdigit():
                                            for row in table1:
                                                if row == None or str(row).strip() == '':
                                                    error_message = (
                                                        f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                                    )
                                                    error_messages.append(error_message)
                                                    if len(temp_data) > 0 :
                                                        if len(table1)>5 and table1[5] == None or str(table1[5]).strip() =='':
                                                            clean_table1.insert(5,temp_data[5])
                                                    elif len(temp_data) == 0:
                                                        clean_table1.insert(5,'검증오류방지')                                                                                
                                            all_tables.append(clean_table1)
                                            temp_data = clean_table1
                                            temp_data1.append(temp_data[3])
                                        elif len(clean_table1) == 1 and not clean_table1[0] in (valid_keywords2 + valid_keywords3 + valid_keywords4):
                                            all_tables2.append(clean_table1)
                                        elif (len(table1) > 0 and (clean_table1[0] in valid_keywords2 or clean_table1[0] in '원재료공통기재사항')):
                                            if len(table1) == 6:
                                                if table1[4] == None or str(table1[4]).strip() == '':
                                                        error_message = (
                                                            f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                                        )
                                                        error_messages.append(error_message)     
                                                if not (clean_table1[0] == '원재료공통기재사항'):
                                                    clean_table1.insert(0,'원재료공통기재사항')
                                                all_tables1.append(clean_table1)
                                            elif len(table1) == 3:
                                                if table1[2] == None or str(table1[2]).strip() == '':
                                                        error_message = (
                                                            f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                                        )
                                                        error_messages.append(error_message)     
                                                if not (clean_table1[0] == '원재료공통기재사항'):
                                                    clean_table1.insert(0,'원재료공통기재사항')
                                                all_tables1.append(clean_table1)                                    
                                        elif (len(table1) > 0 and (clean_table1[0] in valid_keywords3) or clean_table1[0] in '원재료물리‧화학정보'):
                                            if len(table1) == 3:
                                                if table1[2] == None or str(table1[2]).strip() == '':
                                                        error_message = (
                                                            f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                                        )
                                                        error_messages.append(error_message)
                                                if not (clean_table1[0] == '원재료물리‧화학정보'):
                                                    clean_table1.insert(0,'원재료물리‧화학정보')
                                                all_tables1.append(clean_table1)
                                            elif len(table1) == 6:
                                                if table1[4] == None or str(table1[4]).strip() == '':
                                                        error_message = (
                                                            f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                                        )
                                                        error_messages.append(error_message)
                                                if not (clean_table1[0] == '원재료물리‧화학정보'):
                                                    clean_table1.insert(0,'원재료물리‧화학정보')
                                                all_tables1.append(clean_table1)                                                                         
                                        elif len(table1) > 0 and (clean_table1[0] in valid_keywords4 or clean_table1[0] in '원재료제조자정보'):
                                            if len(table1) == 3:
                                                if table1[2] == None or str(table1[2]).strip() == '':
                                                        error_message = (
                                                            f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                                        )
                                                        error_messages.append(error_message)                                  
                                                if not (clean_table1[0] == '원재료제조자정보'):
                                                    clean_table1.insert(0,'원재료제조자정보')
                                                all_tables1.append(clean_table1)
                                            elif  len(table1) == 6:
                                                if table1[4] == None or str(table1[4]).strip() == '':
                                                        error_message = (
                                                            f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                                        )
                                                        error_messages.append(error_message)                                  
                                                if not (clean_table1[0] == '원재료제조자정보'):
                                                    clean_table1.insert(0,'원재료제조자정보')
                                                all_tables1.append(clean_table1)                                     
                                        elif table1[0] == None or '':
                                            clean_table1.insert(0,temp_data[0])
                                            if len(table1) > 1 and table1[1] == None or '':
                                                clean_table1.insert(1,temp_data[1])
                                            all_tables.append(clean_table1)                                   
                                        else:
                                            error_message = (
                                                f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 일련 번호가 숫자(특수문자 금지) 또는 신고서류 양식과 일치하지 않습니다 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                            )
                                            error_messages.append(error_message)    
                        elif  ('접촉' in item for item in first_row):
                            for table1 in tables[2:]:
                                clean_table1 = clean_and_filter_list(table1)
                                if clean_table1[0].isdigit():
                                    for row in table1:
                                        if row == None or str(row).strip() == '':
                                            error_message = (
                                                f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                            )
                                            error_messages.append(error_message)
                                            if len(temp_data) > 0 :
                                                if table1[5] == None or str(table1[5]).strip() =='':
                                                    clean_table1.insert(5,temp_data[5])
                                            elif len(temp_data) == 0:
                                                clean_table1.insert(5,'검증오류방지')
                                    all_tables.append(clean_table1)
                                    temp_data = clean_table1
                                    temp_data1.append(temp_data[3])
                                elif len(clean_table1) == 1 and not clean_table1[0] in (valid_keywords2 + valid_keywords3 + valid_keywords4):
                                    all_tables2.append(clean_table1)
                                elif (len(table1) > 0 and (clean_table1[0] in valid_keywords2 or clean_table1[0] in '원재료공통기재사항')):
                                    if table1[4] == None or str(table1[4]).strip() == '':
                                            error_message = (
                                                f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                            )
                                            error_messages.append(error_message)     
                                    if not (clean_table1[0] == '원재료공통기재사항'):
                                        clean_table1.insert(0,'원재료공통기재사항')
                                    all_tables1.append(clean_table1)
                                elif (len(table1) > 0 and (clean_table1[0] in valid_keywords3) or clean_table1[0] in '원재료물리‧화학정보'):
                                    if table1[4] == None or str(table1[4]).strip() == '':
                                            error_message = (
                                                f' 신고서류 내 오류 내용 : {table1}\r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                            )
                                            error_messages.append(error_message)
                                    # print(type(clean_table1[0]))                                  
                                    if not (clean_table1[0] == '원재료물리‧화학정보'):
                                        clean_table1.insert(0,'원재료물리‧화학정보')
                                    all_tables1.append(clean_table1)                                   
                                elif len(table1) > 0 and (clean_table1[0] in valid_keywords4 or clean_table1[0] in '원재료제조자정보'):
                                    if table1[4] == None or str(table1[4]).strip() == '':
                                            error_message = (
                                                f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 데이터가 입력되지 않았습니다. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요. 해당되지 않는 곳에 해당없음을 기재해주세요 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                            )
                                            error_messages.append(error_message)                                  
                                    if not (clean_table1[0] == '원재료제조자정보'):
                                        clean_table1.insert(0,'원재료제조자정보')
                                    all_tables1.append(clean_table1)    
                                elif table1[0] == None or '':
                                    clean_table1.insert(0,temp_data[0])
                                    if table1[1] == None or '':
                                        clean_table1.insert(1,temp_data[1])
                                    if table1[5] == None or '':
                                        clean_table1.insert(5,temp_data[5])
                                    all_tables.append(clean_table1)
                                elif table1[0] == '일련번호':
                                    continue                                   
                                else:
                                    error_message = (
                                        f' 신고서류 내 오류 내용 : {table1} \r\n 오류 발생 요인 : 일련 번호가 숫자(특수문자 금지) 또는 신고서류 양식과 일치하지 않습니다 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                                    )
                                    error_messages.append(error_message)                                                                
                        else:
                            error_message = (
                                f' 신고서류 내 오류 내용 : {first_row}  \r\n 오류 발생 요인 : 양식에서 제공된 내용과 일치하지 않습니다. \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                            )
                            error_messages.append(error_message)
                    except IndexError:
                        error_message = (
                                f' 신고서류 내 오류 내용 : {table1}  \r\n 오류 발생 요인 : 데이터를 읽을 수 없습니다. \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다'
                            )
                        error_messages.append(error_message)
                        pass
        if len(all_tables) == 0:
            error_message =(
                f' 신고서류 내 오류 내용 : {all_tables} \r\n 오류 발생 요인 : 원재료에 대한 정보가 입력되지 않았습니다. \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다' 
            )
            error_messages.append(error_message)    
        if len(all_tables1) == 0:
            error_message =(
                f' 신고서류 내 오류 내용 : {all_tables1} \r\n 오류 발생 요인 : 자사규격에 관련된 정보 입력이 되지 않았습니다. \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다' 
            )
            error_messages.append(error_message)
        if len(all_tables) > 0:
            a = float(0)
            b = all_tables[0][0]
            for data in all_tables:
                if not len(data) == 6 :
                    pass
                else:
                    if b == data[0]:
                        a = a+float(data[4])
                    elif not data[0] == b:
                        if not a == 100.0:
                            error_message = (
                                f' 신고서류 내 오류 내용 : 일련번호 {b}의 분량 합 : {a}% \r\n 오류 발생 요인 : 일련번호 {b} 분량 합이 100%가 되지 않았습니다 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다' 
                            )
                            error_messages.append(error_message)
                            # a 초기화
                        if is_float(data[4]):
                            a = float(data[4])
                            b = data[0]  
                        else:
                            pass
            if not a == 100.0:
                error_message = (
                    f' 신고서류 내 오류 내용 : 일련번호 {b}의 분량 합 : {a}% \r\n 오류 발생 요인 : 일련번호 {b} 분량 합이 100%가 되지 않았습니다 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조(원재료) 내용 확인이 필요합니다' 
                )
                error_messages.append(error_message)
                # a 초기화
            if len(data) == 6:
                if  is_float(data[4]):
                    a = float(data[4])
                    b = data[0]  
                else:
                    pass            
            # a = float(data[4]) 
            # b = data[0]          
        else :
            error_message = (
                f' 신고서류 내 오류 내용: 원재료 합을 구할 수 없습니다  \r\n 오류 발생 요인 : 일련번호 또는 분량이 숫자로만 이루어지지 않았습니다 \r\n 오류 사항에 대한 근거 : 원재료 - 규정 제10조 내용 확인이 필요합니다'
            )
            error_messages.append(error_message)      
        # 사용 불가 단어 검증 로직 #
        all_tables.append(all_tables1)
        # check_invalid_words(all_tables)
        # check_invalid_words(all_tables)
        # return all_tables, error_messages
    except FileNotFoundError:
        error_message = (
            '원재료 파일이 없습니다'
        )
        error_messages.append(error_message)
    except Exception as e:
        error_messages.append(e)
    # return all_tables, error_messages

    print(len(error_messages))
    for i in error_messages:
        print(i)
validate_mat(r"C:\Users\USER\Documents\카카오톡 받은 파일\원재료 (2).pdf")
