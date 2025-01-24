import pdfplumber
import re
from .validate_utils import *

# 치수
def validate_size(file_path):
    error_messages = []
    product_num = []
    product_name = []
    product_size = []
    total_table = []
    units = []
    
    # 패턴 정의
    num_pattern = re.compile(r'.*(번\s*호|일\s*련\s*번\s*호).*')
    name_pattern = re.compile(r'.*(명\s*칭|모\s*델\s*명|이\s*름|제\s*품\s*명|품\s*명).*')
    size_pattern = re.compile(r'.*(치\s*수|크\s*기).*')
    unit_pattern = re.compile(r'.*\(\s*단\s*위\s*:\s*(\w+)\s*\).*')
    
    # PDF 파일 열기
    pdf = pdfplumber.open(file_path)
    
    # 모든 페이지의 테이블 추출
    for page_num, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        if tables:  # tables가 비어있지 않을 때만 처리
            for table in tables:
                for row in table:
                    if any(row):  # 빈 row가 아닌 경우만 추가
                        total_table.append(row)
    
    # 세 가지 패턴 중 하나라도 매칭되는지 확인
    if not any([
        num_pattern.search(str(cell)) or 
        name_pattern.search(str(cell)) or 
        size_pattern.search(str(cell))
        for row in total_table 
        for cell in row 
        if cell
    ]):
        error_messages.append(
            f" 신고서류 내 검토필요사항 내용 : 일련번호, 명칭, 치수 관련 정보 찾을 수 없음\r\n" +
            f" 검토사항 발생 요인 : 신청제품의 각 부분의 일련번호, 명칭, 치수 정보를 빠짐없이 기재할 것\r\n" +
            f" 검토사항에 대한 근거 : 치수 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다"
        )
        return total_table, error_messages
    
    # 인덱스 초기화
    num_col_idx = []
    name_col_idx = []
    size_col_idx = []
    row_idx = []
    
    # 테이블에서 패턴 찾기
    for i, row in enumerate(total_table):
        patter_matched = False
        if row:
            for j, cell in enumerate(row):
                if cell:
                    # 3. 패턴 매칭 안전하게
                    if unit_pattern.search(str(cell)):
                        unit_match = unit_pattern.search(str(cell))
                        try:
                            unit_value = unit_match.group(1).strip()
                            units.append(unit_value)
                        except (IndexError, AttributeError):
                            pass
                            
                    # 패턴 중 하나라도 일치하면 row_idx에 추가
                    if (num_pattern.search(str(cell)) or 
                        name_pattern.search(str(cell)) or 
                        size_pattern.search(str(cell))):
                        patter_matched = True
                    # 각각의 컬럼 인덱스는 개별적으로 저장
                    if num_pattern.search(str(cell)):
                        num_col_idx.append(j)
                    if name_pattern.search(str(cell)):
                        name_col_idx.append(j)
                    if size_pattern.search(str(cell)):
                        size_col_idx.append(j)
        if patter_matched:
            row_idx.append(i)
    # 건너뛸 헤더 패턴
    skip_pattern = re.compile(r'.*[\(（]\s*단\s위\s*:\s*[mc]m\s*[\)）].*')
    
    for i, row in enumerate(total_table):
        for j, header_row_idx in enumerate(row_idx):
            current_idx = header_row_idx
            
            while current_idx < len(total_table):
                data_row = total_table[current_idx]
                if data_row is None:
                    current_idx += 1
                    continue
                
                if current_idx != header_row_idx and is_skip_header(data_row, skip_pattern):
                    break
                
                # 1. i번째 인덱스가 있는 col_idx들만 모으기
                valid_indices = []
                if i < len(num_col_idx):
                    valid_indices.append(num_col_idx[i])
                    num_value = data_row[num_col_idx[i]]
                if i < len(name_col_idx):
                    valid_indices.append(name_col_idx[i])
                    name_value = data_row[name_col_idx[i]]
                if i < len(size_col_idx):
                    valid_indices.append(size_col_idx[i])
                    size_value = data_row[size_col_idx[i]]

                # 2. 유효한 인덱스들 중 최대값으로 data_row 길이 비교
                if valid_indices and max(valid_indices) < len(data_row):
                    
                    if (not is_empty(num_value) or not is_empty(name_value) or not is_empty(size_value)):
                        if is_empty(num_value) or is_empty(name_value) or is_empty(size_value):
                            error_messages.append(
                                f" 신고서류 내 검토필요사항 내용 : 일부 정보가 누락되었습니다 (번호: {num_value or '누락'}, 명칭: {name_value or '누락'}, 치수: {size_value or '누락'})\r\n" +
                                f" 검토사항 발생 요인 : 신청제품의 각 부분의 정보를 빠짐없이 기재할 것 (셀이 병합되어 있다면 개별 셀로 분리하여 입력)\r\n" +
                                f" 검토사항에 대한 근거 : 치수 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다"
                            )
                    
                    # 기존 데이터 저장 로직
                    if clean_text(num_value) not in [clean_text(num) for num in product_num]:
                        product_num.append(num_value)
                    if clean_text(name_value) not in [clean_text(name) for name in product_name]:
                        product_name.append(name_value)
                    if clean_text(size_value) not in [clean_text(size) for size in product_size]:
                        product_size.append(size_value)
                
                current_idx += 1
    error_messages.extend(validate_factors(product_num, '번호', units))
    error_messages.extend(validate_factors(product_name, '명칭', units))
    error_messages.extend(validate_factors(product_size, '치수', units))
    return total_table, error_messages

def validate_factors(rows, name, units):
    error_messages = []
    blank_dup_flag = False
    
    # 숫자 뒤에 inch 표시가 오는 패턴을 정규식으로 정의
    inch_pattern = re.compile(r'\d+(\.\d+)?\s*\"')  # 예: "123" 또는 "123.45"
    
    if len(rows) == 0:
        error_messages.append(
            f" 신고서류 내 검토필요사항 내용 : {name}(이)가 존재하지 않습니다.\r\n" +
            f" 검토사항 발생 요인 : 신청제품의 각 부분의 {name}(을)를 빠짐없이 기재할 것\r\n" +
            f" 검토사항에 대한 근거 : 치수 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다"
        )
        return error_messages
        
    for row in rows:
        if is_empty(row) and not blank_dup_flag:
            error_messages.append(
                f" 신고서류 내 검토필요사항 내용 : {name}에 빈 칸이 존재합니다.\r\n" +
                f" 검토사항 발생 요인 : 신청제품의 각 부분의 {name}(을)를 빠짐없이 기재할 것\r\n" +
                f"검토사항에 대한 근거 : 치수 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다"
            )
            blank_dup_flag = True
    
    if(name == '치수'):
        inch_pattern = re.compile(r'\d+(\.\d+)?\s*\"')  # 예: "123" 또는 "123.45"
        for row in rows:
            if row :
                if (any(unit in row for unit in ['inch', 'in.']) or inch_pattern.search(str(row))) and row:
                    if not any(unit in row for unit in units):
                        error_messages.append(
                            f" 신고서류 내 검토필요사항 내용 : \'{row}\'\r\n" +
                            f" 검토사항 발생 요인 : 치수 단위 누락, SI 단위로 표기할 것\r\n" +
                            f" 검토사항에 대한 근거 : 치수 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다"
                        )
    return error_messages