import pdfplumber
from .forbidden_words import forbidden_words  # 금지 단어 리스트
from .save_error_to_txt import save_error_to_file  # 에러 저장 함수
# 외형

fixed_header = ['번호', '명칭', '기능 및 역할']

def clean_text(text):
    """텍스트에서 공백 및 줄바꿈을 제거하여 비교를 위한 클리닝."""
    return text.replace('\n', '').replace(' ', '').strip() if isinstance(text, str) else ""

def normalize_header(header_row):
    """헤더 행을 정규화하여 공백과 대소문자를 통일."""
    return [clean_text(cell).lower().replace(" ", "") for cell in header_row]

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
        if not item['번호'].isdigit():
            row_errors.append(f"'번호'가 숫자가 아님: {item['번호']}")

        # "명칭" 검증
        if not item['명칭']:
            row_errors.append(f"'명칭'이 비어 있음")
        else:
            for word in forbidden_words:
                if word in item['명칭']:
                    row_errors.append(f"'명칭'에 금지 단어 {word} 포함")

        # "기능 및 역할" 검증
        if not item['기능 및 역할']:
            row_errors.append(f"'기능 및 역할'이 비어 있음")
        else:
            for word in forbidden_words:
                if word in item['기능 및 역할']:
                    row_errors.append(f"'기능 및 역할'에 금지 단어 {word} 포함")

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
            # print(f"페이지 {page_number} 처리 중...")
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

                if not contains_exterior_info and first_row != normalized_fixed_header:
                    error_messages.append(
                        f"페이지 {page_number}: 첫 번째 행이 fixed_header와 일치하지 않음. 행: {table[0]}"
                    )

                # 딕셔너리 변환
                dict_data = table_to_dict(table)
                
                for row in table :
                    add_row = ''
                    for a in row :
                        a = clean_text(a)
                        add_row = add_row + ' ' + a
                    all_tables.append(add_row)
                
                # 데이터 검증
                errors = validate_dict_data(dict_data, forbidden_words)
                if errors:
                    for error in errors:
                        error_messages.append(error)
                
    return all_tables, error_messages




