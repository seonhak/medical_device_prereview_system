import pdfplumber
from .forbidden_words import forbidden_words  # 금지 단어 리스트
from .validate_utils import *
# 외형
def validate_shape(file_path):
    error_count = 1
    error_messages = []
    product_num = []
    product_name = []
    product_role = []
    total_table = []
    units = []
    
    # 패턴 정의
    num_pattern = re.compile(r'.*(번\s*호|일\s*련\s*번\s*호).*')
    name_pattern = re.compile(r'.*(명\s*칭|모\s*델\s*명|이\s*름|제\s*품\s*명|품\s*명).*')
    role_pattern = re.compile(r'.*(기\s*능|역\s*할).*')
    
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
        role_pattern.search(str(cell))
        for row in total_table 
        for cell in row 
        if cell
    ]):
        error_messages.append(
            f"{error_count}. 신고서류 외형 파일에서 번호, 명칭, 기능 및 역할 관련 정보 찾을 수 없는 것으로 확인됩니다. " +
            f"재검토 원인은 필수정보 미기재 입니다. " +
            f"관련 규정은 외형 - 규정 제9조(모양 및 구조)를 확인하시기 바랍니다.\r\n"
        )
        error_count += 1
        return total_table, error_messages, error_count
    
    # 인덱스 초기화
    num_col_idx = []
    name_col_idx = []
    role_col_idx = []
    row_idx = []
    
    # 테이블에서 패턴 찾기
    for i, row in enumerate(total_table):
        pattern_matched = False
        if row:
            for j, cell in enumerate(row):
                if cell:    
                    # 패턴 중 하나라도 일치하면 row_idx에 추가
                    if (num_pattern.search(str(cell)) or 
                        name_pattern.search(str(cell)) or 
                        role_pattern.search(str(cell))):
                        pattern_matched = True
                    # 각각의 컬럼 인덱스는 개별적으로 저장
                    if num_pattern.search(str(cell)):
                        num_col_idx.append(j)
                    if name_pattern.search(str(cell)):
                        name_col_idx.append(j)
                    if role_pattern.search(str(cell)):
                        role_col_idx.append(j)
        if pattern_matched:
            row_idx.append(i)
    # 건너뛸 헤더 패턴
    skip_pattern = re.compile(r'.*(외\s*관\s*설\s*명|외\s*관\s*사\s*진).*')  
    for j, header_row_idx in enumerate(row_idx):
        # 다음 헤더의 인덱스를 찾거나, 없으면 테이블 끝까지
        next_header_row_idx = row_idx[j + 1] if j + 1 < len(row_idx) else len(total_table)
        
        # 현재 헤더 다음 행부터 다음 헤더 전까지 순회
        for current_row_idx in range(header_row_idx + 1, next_header_row_idx):
            data_row = total_table[current_row_idx]
            
            if is_skip_header(data_row, skip_pattern):
                continue
                
            # 데이터 행의 길이 확인
            if (j < len(num_col_idx) and num_col_idx[j] < len(data_row)):
                num_value = data_row[num_col_idx[j]]
                if clean_text(num_value) not in [clean_text(num) for num in product_num]:
                    product_num.append(num_value)
            
            if (j < len(name_col_idx) and name_col_idx[j] < len(data_row)):
                name_value = data_row[name_col_idx[j]]
                if clean_text(name_value) not in [clean_text(name) for name in product_name]:
                    product_name.append(name_value)
            
            if (j < len(role_col_idx) and role_col_idx[j] < len(data_row)):
                role_value = data_row[role_col_idx[j]]
                if clean_text(role_value) not in [clean_text(role) for role in product_role]:
                    product_role.append(role_value)

    temp_error_messages, error_count = validate_shape_factors(product_num, '번호', error_count)
    error_messages.extend(temp_error_messages)
    temp_error_messages, error_count = validate_shape_factors(product_name, '명칭', error_count)
    error_messages.extend(temp_error_messages)
    temp_error_messages, error_count = validate_shape_factors(product_role, '기능및역할', error_count)
    error_messages.extend(temp_error_messages)
    return total_table, error_messages, error_count

def validate_shape_factors(rows, name, error_count):
    error_messages = []
    blank_dup_flag = False
    
    if len(rows) == 0:
        error_messages.append(
            f"{error_count}. 신고서류 외형 파일에서 {name}(이)가 존재하지 않는 것으로 확인됩니다. " +
            f"재검토 원인은 {name} 미기재 입니다. " +
            f"관련 규정은 외형 - 규정 제9조(모양 및 구조)를 확인하시고, {name} 정보를 기재하신 후 제출하시기 바랍니다.\r\n"
        )
        error_count += 1
        return error_messages, error_count
    
    if(name == '명칭'):
        temp_error_messages, error_count = check_invalid_words(rows, error_count, '외형')
        error_messages.extend(temp_error_messages)
    return error_messages, error_count