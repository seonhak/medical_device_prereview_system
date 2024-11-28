import os
import re
import pdfplumber

def validate_mat(mat_file):
    print("validate mat is called, validating {mat_file}")


def extract_mat(mat_file):
    print("extract mat is called, extracting {mat_file}")
    return "원재료 추출 텍스트"

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
def map_data_to_fixed_items1(tables, fixed_header, fixed_items):
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
        saved_0, saved_1, saved_last = None, None, None  # 이전 행의 0, 1, 마지막 값 저장
        for idx, row in enumerate(table):
            row = preprocess_row(row)  # 데이터 전처리
            # 첫 번째 행(헤더)은 그대로 추가
            if idx == 0:
                mapped_data.append(row)
                continue
            # 1. 빈 값이 아닌 경우만 이전 값 채우기
            if row[1] or row[2] or row[5]:  # row[1] 또는 row[2]에 값이 있을 경우만 처리
                if not row[0] and saved_0 is not None:
                    row[0] = saved_0
                if not row[1] and saved_1 is not None:
                    row[1] = saved_1
            if not row[-1] and saved_last is not None:  # 마지막 값이 비어 있는 경우
                row[-1] = saved_last                    
            # 2. fixed_items 매핑 (row[1] 또는 row[2]를 기준으로 비교)
            for fixed_item in fixed_items:
                if fixed_item[1] == row[1] or fixed_item[1] == row[2]:  # row[1] 또는 row[2]와 비교
                    row[0] = fixed_item[0]  # row[0] 값을 fixed_items[0]으로 설정
                    break
            # 현재 행의 0, 1 값을 저장
            saved_0, saved_1, saved_last = row[0], row[1], row[-1]
            # 결과 추가
            mapped_data.append(row)
    return mapped_data

fixed_header = ['일련 번호', '부분품의 명칭', '원재료명 또는 성분명', '규격', '분량', '비고 (인체접촉여부 및 접촉부위, 첨가목적)']
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
standard_word_list = ['일련 번호', '원재료 공통 기재사항', '일반명']
def validate_and_process_filtered_data(filtered_data):
    """
    filtered_data에서 특정 조건을 검증하고 에러 처리를 수행.
    :param filtered_data: 최종 처리된 데이터
    """
    total_sum = 0  # 합계 초기화
    rows_with_digits = []  # 숫자 값을 가진 행 저장
    for row_idx, row in enumerate(filtered_data, start=1):
        try:
            # row[4]가 숫자인 경우 합산
            value = float(row[4].replace('%', '').strip())
            total_sum += value
            rows_with_digits.append(row)  # 숫자 값을 가진 행 저장
        except (ValueError, IndexError):
            # row[4]가 숫자가 아니거나 값이 없는 경우 무시
            continue

    # 합이 100의 배수가 아니면 에러 처리
    if total_sum % 100 != 0:
        print(f"에러: 합계가 100의 배수가 아님 - 합계: {total_sum}")
        # print(f"문제 발생한 행:")
        # for row in rows_with_digits:
        #     print(row)
        # raise ValueError(f"에러 발생 - 합계가 100의 배수가 아님: {total_sum}")

def process_pdf(file_path, fixed_header, fixed_items):
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
        filtered_data = map_data_to_fixed_items1(cleaned_tables, fixed_header, fixed_items)
        # 최종 결과 출력
        print("\n[최종 처리된 데이터]")
        for table in filtered_data:
            print(table)
    try:
        validate_and_process_filtered_data(filtered_data)
    except ValueError as e:
        print(e)

pdf_file_path = ""

process_pdf(pdf_file_path, fixed_header, fixed_items)