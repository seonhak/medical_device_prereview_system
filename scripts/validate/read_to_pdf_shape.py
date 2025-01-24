import pdfplumber
from .forbidden_words import forbidden_words  # 금지 단어 리스트
from .save_error_to_txt import save_error_to_file  # 에러 저장 함수
from .validate_utils import *
# 외형

fixed_header = ['번호', '명칭', '기능 및 역할']
fixed_header_str = '번호명칭기능및역할'

def table_to_dict(table):
    """테이블 데이터를 딕셔너리 리스트로 변환."""
    keys = ['번호', '명칭', '기능 및 역할']
    dict_list = []
    for row in table[1:]:  # 첫 행은 헤더이므로 제외
        if len(row) < len(keys):
            continue
        dict_item = {keys[i]: clean_text(row[i]) for i in range(len(keys))}
        dict_list.append(dict_item)
    return dict_list

def validate_dict_data(dict_data, forbidden_words):
    """딕셔너리 데이터를 검증."""
    error_messages = []  # 모든 오류 메시지를 저장할 리스트
    for idx, item in enumerate(dict_data, start=1):
        row_errors = []
        # "번호" 검증
        if any(keyword in item['번호'] for keyword in ['외관사진', '외관설명']):
            continue
        else:
            # if not item['번호'].isdigit():
            #     row_errors.append(
            #         f" 신고서류 내 검토필요사항 : {item['번호']} \r\n 검토사항 발생 요인 : 잘못된 데이터 형식이 발견되었습니다.('번호'가 숫자가 아님) \r\n 검토사항에 대한 근거 : 외형 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다" 
            #         )
            # "명칭" 검증
            if not item['번호']:
                row_errors.append(f"신고 서류 내 검토필요사항 : {item['명칭']} \r\n 검토사항 발생 요인 : '번호'가 비어 있습니다.  \r\n 검토사항에 대한 근거 : 외형 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다")
            if not item['명칭']:
                row_errors.append(f"신고 서류 내 검토필요사항 : {item['명칭']} \r\n 검토사항 발생 요인 : '명칭'이 비어 있습니다.  \r\n 검토사항에 대한 근거 : 외형 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다")
            else:
                for word in forbidden_words:
                    if word in item['명칭']:
                        row_errors.append(
                            f" 신고서류 내 검토필요사항 내용 : {item['명칭']} \r\n 검토사항 발생 요인 : 사용 불가 단어 \'{word}\'(이)가 확인되었습니다. \r\n 검토사항에 대한 근거 : 외형 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다"                         
                            )

            # "기능 및 역할" 검증
            if not item['기능 및 역할']:
                row_errors.append(f"신고서류 내 검토필요사항 내용 : {item['기능 및 역할']} \r\n 검토사항 발생 요인 : '기능 및 역할'이 비어 있음 \r\n 검토사항에 대한 근거 : 외형 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다")
            else:
                for word in forbidden_words:
                    if word in item['기능 및 역할']:
                        row_errors.append(
                            f" 신고서류 내 검토필요사항 내용: {item['기능 및 역할']} \r\n 검토사항 발생 요인 : 사용 불가 단어 \'{word}\'(이)가 확인되었습니다. \r\n 검토사항에 대한 근거 : 외형 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다"                         
                            )

        if row_errors:
            # error_messages.append("row : {idx}, errors : {row_errors}")
            for row in row_errors :
                error_messages.append(row)
    return error_messages

def validate_shape(file_path):
    """PDF 파일을 읽고 딕셔너리를 기반으로 검증."""
    all_tables = []
    error_messages = []

    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            # 페이지별로 테이블 추출
            page_tables = page.extract_tables()
            if not page_tables:
                continue
            
            
            for table in page_tables:
                # 첫 번째 행 검증 (정규화된 비교)
                first_row = normalize_header(table[0])
                normalized_fixed_header = normalize_header(fixed_header)

                # "외관사진" 또는 "외관설명" 포함 여부 확인
                contains_exterior_info = any(
                    "외관사진" in clean_text(cell) or "외관설명" in clean_text(cell)
                    for cell in table[0]
                )

                # "외관사진" 또는 "외관설명" 포함 시 이 테이블은 건너뜀
                if contains_exterior_info:
                    continue

                # 테이블 데이터 딕셔너리로 변환 및 검증
                dict_data = table_to_dict(table)
                for row in table:
                    add_row = ''
                    for a in row:
                        a = clean_text(a)
                        add_row = add_row + ' ' + a

                    if not clean_text(add_row) == '' and not clean_text(add_row) == clean_text(fixed_header_str):
                        all_tables.append(add_row)
                        error_messages.extend(check_invalid_words(add_row))

                # 데이터 검증
                errors = validate_dict_data(dict_data, forbidden_words)
                if errors:
                    for error in errors:
                        error_messages.append(error)

    return all_tables, error_messages




def validate_shape_test(file_path):
    error_messages = []
    print("함수 시작")
    with pdfplumber.open(file_path) as pdf:
        print("PDF 파일 열기 성공")
        total_tables = []
        
        # 번호, 명칭, 치수 리스트는 각각 번호, 명칭, 치수 값들만 저장
        product_num = []
        product_name = []
        product_size = []
        
        # idx 변수들은 각 행의 몇 번째 테이블이 각각 번호, 명칭, 치수인지 위치를 저장
        num_idx = []
        name_idx = []
        size_idx = []
        units = []
        # row_idx는 번호, 명칭, 치수가 들어있는 열이 어디인지 위치를 저장
        row_idx = []
        
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            total_tables.extend(tables)
        
        # 정규식 패턴 컴파일 (헤더)
        num_pattern = re.compile(r'.*(번\s*호|일\s*련\s*번\s*호).*')
        name_pattern = re.compile(r'.*(명\s*칭|모\s*델\s*명|이\s*름|제\s*품\s*명|품\s*명).*')
        size_pattern = re.compile(r'.*(치\s*수|크\s*기).*')
        unit_pattern = re.compile(r'.*단위\s*:\s*\(?(\w+)\)?')
        
        for table in total_tables:
            for row in table:
                for i, cell in enumerate(row):
                    if cell:
                        if unit_pattern.search(str(cell)):
                            unit_match = unit_pattern.search(str(cell))
                            unit_value = unit_match.group(1).strip()
                            units.append(unit_value)
                        if num_pattern.search(str(cell)):
                            num_idx.append(i)
                            row_idx.append(i)
                        if name_pattern.search(str(cell)):
                            name_idx.append(i)
                        if size_pattern.search(str(cell)):
                            size_idx.append(i)
        # num_idx, name_idx, size_idx는 헤더가 있는 테이블에서 num, name, size가 있는 열의 위치를 저장
        # row_idx는 번호, 명칭, 치수가 들어있는 행이 어디인지 위치를 저장
        # product_num, product_name, product_size는 번호, 명칭, 치수 값들을 저장
        # 모든 테이블을 순회하면서 헤더가 있는 행의 위치를 찾고
        # 그 위치 아래에 있는 값들을 각각 product_num, product_name, product_size에 저장
        for table in total_tables:
            for i, row in enumerate(row_idx):
                # 헤더 행 이후의 모든 행을 순회
                for data_row in table[row+1:]:
                    length = len(data_row)
                    if max(num_idx[i], name_idx[i], size_idx[i]) < len(data_row):
                        # if data_row[num_idx[i]]:
                        #     # 중복된 일련번호 입니다.
                        #     if clean_text(data_row[num_idx[i]]) in [clean_text(num) for num in product_num]:
                        #         error_messages.append(
                        #             f" 신고서류 내 검토필요사항 내용 : \'{data_row[num_idx[i]]}\'\r\n 검토사항 발생 요인 : 중복된 일련번호가 존재합니다.\r\n 검토사항에 대한 근거 : 치수 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다."
                        #         )
                        # if data_row[name_idx[i]]:
                        #     # 중복된 명칭 입니다.
                        #     if clean_text(data_row[name_idx[i]]) in [clean_text(num) for num in product_name]:
                        #         error_messages.append(
                        #             f" 신고서류 내 검토필요사항 내용 : \'{data_row[name_idx[i]]}\'\r\n 검토사항 발생 요인 : 중복된 명칭이 존재합니다.\r\n 검토사항에 대한 근거 : 치수 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다."
                        #         )
                        # 치수는 중복될 수 있음
                        
                        # 넣을 데이터들이 이미 있는 데이터면 저장하지 않음
                        if clean_text(data_row[num_idx[i]]) not in [clean_text(num) for num in product_num]:
                            product_num.append(data_row[num_idx[i]])
                        if clean_text(data_row[name_idx[i]]) not in [clean_text(name) for name in product_name]:
                            product_name.append(data_row[name_idx[i]])
                        if clean_text(data_row[size_idx[i]]) not in [clean_text(size) for size in product_size]:
                            product_size.append(data_row[size_idx[i]])
                        
        if(len(product_num) > 0 and len(product_name) > 0 and len(product_size) > 0):
            error_messages.extend(validate_num(product_num))
            error_messages.extend(validate_name(product_name))
            error_messages.extend(validate_size(product_size, units))
        else:
            error_messages.append(
                f" 신고서류 내 검토필요사항 내용 : 일련번호, 명칭, 치수 관련 정보 찾을 수 없음\r\n 검토사항 발생 요인 : 신청제품의 각 부분의 일련번호, 명칭, 치수 정보를 빠짐없이 기재할 것\r\n 검토사항에 대한 근거 : 치수 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다"
            )
        return total_tables, error_messages

def validate_num(rows):
    error_messages = []
    blank_dup_flag = False
    if(len(rows) == 0):
        error_messages.append(
            f" 신고서류 내 검토필요사항 내용 : 일련번호가 존재하지 않습니다.\r\n 검토사항 발생 요인 : 신청제품의 각 부분의 일련번호를 빠짐없이 기재할 것\r\n 검토사항에 대한 근거 : 치수 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다"
        )
        return error_messages
    for row in rows:
        if (not row or str(row).strip() == '') and blank_dup_flag == False:
            error_messages.append(
                f" 신고서류 내 검토필요사항 내용 : 일련번호에 빈 칸이 존재합니다.\r\n 검토사항 발생 요인 : 신청제품의 각 부분의 일련번호를 빠짐없이 기재할 것\r\n 검토사항에 대한 근거 : 치수 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다"
            )
            blank_dup_flag = True
    return error_messages

def validate_name(rows):
    error_messages = []
    blank_dup_flag = False
    error_messages.extend(check_invalid_words(rows))
    if(len(rows) == 0):
        error_messages.append(
            f" 신고서류 내 검토필요사항 내용 : 명칭이 존재하지 않습니다.\r\n 검토사항 발생 요인 : 신청제품의 각 부분의 명칭을 빠짐없이 기재할 것\r\n 검토사항에 대한 근거 : 치수 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다"
        )
        return error_messages
    for row in rows:
        if (not row or str(row).strip() == '') and blank_dup_flag == False:
            error_messages.append(
                f" 신고서류 내 검토필요사항 내용 : 명칭에 빈 칸이 존재합니다.\r\n 검토사항 발생 요인 : 신청제품의 각 부분의 명칭을 빠짐없이 기재할 것\r\n 검토사항에 대한 근거 : 치수 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다"
            )
            blank_dup_flag = True
    return error_messages

def validate_size(rows, units):
    error_messages = []
    blank_dup_flag = False
    
    # 숫자 뒤에 inch 표시가 오는 패턴을 정규식으로 정의
    inch_pattern = re.compile(r'\d+(\.\d+)?\s*\"')  # 예: "123" 또는 "123.45"
    if(len(rows) == 0):
        error_messages.append(
            f" 신고서류 내 검토필요사항 내용 : 치수가 존재하지 않습니다.\r\n 검토사항 발생 요인 : 신청제품의 각 부분의 치수 정보를 빠짐없이 기재할 것\r\n 검토사항에 대한 근거 : 치수 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다"
        )
        return error_messages
    for row in rows:
        if (not row or str(row).strip() == '') and blank_dup_flag == False:
            error_messages.append(
                f" 신고서류 내 검토필요사항 내용 : 치수에 빈 칸이 존재합니다.\r\n 검토사항 발생 요인 : 신청제품의 각 부분의 치수 정보를 빠짐없이 기재할 것\r\n 검토사항에 대한 근거 : 치수 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다"
            )
            blank_dup_flag = True
            
        # inch 단위가 있을 경우, SI 단위가 함께 있는지 확인, inch 단위만 있을 경우 error 발생
        if any(unit in row for unit in ['inch', 'in.']) or inch_pattern.search(str(row)):
            if not any(unit in row for unit in units):
                error_messages.append(
                    f" 신고서류 내 검토필요사항 내용 : \'{row}\'\r\n 검토사항 발생 요인 : 치수 단위 누락, SI 단위로 표기할 것\r\n 검토사항에 대한 근거 : 치수 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다"
                )
    
    return error_messages

# tmp_file = fr"C:\Users\USER\Desktop\식약처\고도화\고도화용 데이터 53건\검증용 데이터 53건\21_20240095369_벨트형\모양및구조-치수.pdf"
# validate_test(tmp_file)
