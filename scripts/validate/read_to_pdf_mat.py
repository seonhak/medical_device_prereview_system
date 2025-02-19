import os
import re
import pdfplumber
from .forbidden_words import *
from .save_error_to_txt import *
from .validate_utils import *

# 원재료
def validate_mat(file_path):
    error_count = 1
    error_messages = []
    
    product_num = []
    product_name = []
    product_mat_name = []
    product_std = []
    product_amount = []
    product_bigo = []
    
    total_table = []
    units = []
    # 패턴 정의
    num_pattern = re.compile(r'.*(일\s*련\s*번\s*호|번\s*호).*')
    name_pattern = re.compile(r'.*부\s*분\s*품\s*의\s*명\s*칭.*')
    mat_name_pattern = re.compile(r'.*원\s*재\s*료\s*명.*')
    std_pattern = re.compile(r'^\s*규\s*격\s*$')
    amount_pattern = re.compile(r'.*(분\s*량).*')
    bigo_pattern = re.compile(r'.*(비\s*고).*')
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
        mat_name_pattern.search(str(cell)) or 
        std_pattern.search(str(cell)) or 
        amount_pattern.search(str(cell)) or 
        bigo_pattern.search(str(cell))
        for row in total_table 
        for cell in row 
        if cell
    ]):
        error_messages.append(
            f"{error_count}. 신고서류 원재료 파일에서 일련번호, 명칭, 원재료 관련 정보 찾을 수 없는 것으로 확인됩니다. " +
            f"재검토 원인은 필수정보 미기재 입니다. " +
            f"관련 규정은 원재료 - 규정 제10조(원재료)를 확인하시기 바랍니다.\r\n"
        )
        error_count += 1
        print(error_messages)
        return total_table, error_messages
    
    # 인덱스 초기화
    num_col_idx = []
    name_col_idx = []
    mat_name_col_idx = []
    std_col_idx = []
    amount_col_idx = []
    bigo_col_idx = []
    row_idx = []
    
    # 테이블에서 패턴 찾기
    for i, row in enumerate(total_table):
        pattern_matched = False
        if row:
            none_count = sum(1 for cell in row if cell in [None, ''])
            if none_count >= 3:
                continue
            else:
                for j, cell in enumerate(row):
                    if cell:
                        # 패턴 중 하나라도 일치하면 row_idx에 추가
                        if (num_pattern.search(str(cell)) or 
                            name_pattern.search(str(cell)) or 
                            mat_name_pattern.search(str(cell)) or 
                            std_pattern.search(str(cell)) or 
                            amount_pattern.search(str(cell)) or 
                            bigo_pattern.search(str(cell))): 
                            pattern_matched = True
                        # 각각의 컬럼 인덱스는 개별적으로 저장
                        if num_pattern.search(str(cell)):
                            num_col_idx.append(j)
                        if name_pattern.search(str(cell)):
                            name_col_idx.append(j)
                        if mat_name_pattern.search(str(cell)):
                            mat_name_col_idx.append(j)
                        if std_pattern.search(str(cell)):
                            std_col_idx.append(j)
                        if amount_pattern.search(str(cell)):
                            amount_col_idx.append(j)
                        if bigo_pattern.search(str(cell)):
                            bigo_col_idx.append(j)
        if pattern_matched:
            row_idx.append(i)
    
    for j, header_row_idx in enumerate(row_idx):
        next_header_row_idx = row_idx[j + 1] if j + 1 < len(row_idx) else len(total_table)
        
        for current_row_idx in range(header_row_idx + 1, next_header_row_idx):
            data_row = total_table[current_row_idx]
            
            # None 값이나 빈 문자열의 개수가 3개 이상이면 break
            none_count = sum(1 for cell in data_row if cell in [None, ''])
            if none_count >= 3:
                break
                
            # 기존 데이터 수집 로직
            if (j < len(num_col_idx) and num_col_idx[j] < len(data_row)):
                num_value = data_row[num_col_idx[j]]
                if not is_empty(num_value):
                    product_num.append(num_value)
            
            if (j < len(name_col_idx) and name_col_idx[j] < len(data_row)):
                name_value = data_row[name_col_idx[j]]
                if not is_empty(name_value):
                    product_name.append(name_value)
            
            if (j < len(mat_name_col_idx) and mat_name_col_idx[j] < len(data_row)):
                mat_name_value = data_row[mat_name_col_idx[j]]
                if not is_empty(mat_name_value):
                    product_mat_name.append(mat_name_value)
            
            if (j < len(std_col_idx) and std_col_idx[j] < len(data_row)):
                std_value = data_row[std_col_idx[j]]
                if not is_empty(std_value):
                    product_std.append(std_value)
            
            if (j < len(amount_col_idx) and amount_col_idx[j] < len(data_row)): 
                amount_value = data_row[amount_col_idx[j]]
                if not is_empty(amount_value):
                    product_amount.append(amount_value)
            
            if (j < len(bigo_col_idx) and bigo_col_idx[j] < len(data_row)):
                bigo_value = data_row[bigo_col_idx[j]]
                if not is_empty(bigo_value):
                    product_bigo.append(bigo_value)
    
    temp_error_messages, error_count = validate_mat_factors(product_num, '번호', units, error_count)
    error_messages.extend(temp_error_messages)
    temp_error_messages, error_count = validate_mat_factors(product_name, '부분품의 명칭', units, error_count)
    error_messages.extend(temp_error_messages)
    temp_error_messages, error_count = validate_mat_factors(product_mat_name, '원재료명', units, error_count)
    error_messages.extend(temp_error_messages)
    temp_error_messages, error_count = validate_mat_factors(product_std, '규격', units, error_count)
    error_messages.extend(temp_error_messages)
    temp_error_messages, error_count = validate_mat_factors(product_amount, '분량', units, error_count)
    error_messages.extend(temp_error_messages)
    temp_error_messages, error_count = validate_mat_factors(product_bigo, '비고', units, error_count)
    error_messages.extend(temp_error_messages)
    
    total_text = ''
    for page_num, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text:
            total_text += text
    
    for std in product_std:
        std_count = total_text.count(std)
        
        if std_count == 1:
            if not '- 자사규격(아래 기재양식 중에서 해당되는 하나만 선택하여 기재하여 주시기 바랍니다.)' in total_text:
                error_messages.append(
                    f"{error_count}. 신고서류 원재료 파일에서 {std}에 대한 상세 정보가 없는 것으로 확인됩니다. " +
                    f"재검토 원인은 규격 정보 미기재입니다. " + 
                    f"관련 규정은 원재료 - 규정 제10조(원재료)를 확인하시고, 해당 규격에 대한 상세 정보를 기재하신 후 제출하시기 바랍니다.\r\n"
                )
            error_count += 1
    
    return total_table, error_messages, error_count

def validate_mat_factors(rows, name, units, error_count):
    error_messages = []
    blank_dup_flag = False
    
    if len(rows) == 0:
        error_messages.append(
            f"{error_count}. 신고서류 원재료 파일에서 {name}(이)가 존재하지 않는 것으로 확인됩니다. " +
            f"재검토 원인은 {name} 미기재 입니다. " +
            f"관련 규정은 원재료 - 규정 제10조(원재료)를 확인하시고, {name} 정보를 기재하신 후 제출하시기 바랍니다.(병합된 셀은 병합을 해제해주세요)\r\n"
        )
        error_count += 1
        return error_messages, error_count
    
    if(name == '분량'):
        # 숫자가 포함된 분량 값만 필터링
        valid_amounts = []
        for row in rows:
            if row and isinstance(row, str):
                # 문자열에서 숫자만 추출
                # 소수점을 포함한 숫자 추출을 위한 정규식 패턴
                numbers = re.findall(r'\d*\.?\d+', row)
                if numbers:
                    valid_amounts.append(float(numbers[0]))
                    
        if valid_amounts:
            
            sum_of_amount = sum(valid_amounts)
            if sum_of_amount % 100 != 0:
                error_messages.append(
                    f"{error_count}. 신고서류 원재료 파일에서 분량의 합이 {sum_of_amount % 100}% 입니다." +
                    f"재검토 원인은 분량 합이 100%가 아닙니다. " +
                    f"관련 규정은 원재료 - 규정 제10조(원재료)를 확인하시고, 분량을 정확하게 기재하신 후 제출하시기 바랍니다.\r\n"
                )
                error_count += 1
    
    return error_messages, error_count
