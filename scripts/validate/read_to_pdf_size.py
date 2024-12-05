import pdfplumber
from .forbidden_words import forbidden_words  # 금지 단어 리스트
from .save_error_to_txt import save_error_to_file  # 에러 저장 함수
# 치수

fixed_header = ['번호', '명칭', '치수']
fixed_header_str = '번호명칭치수'
def clean_text(text):
    """텍스트에서 공백 및 줄바꿈을 제거하여 비교를 위한 클리닝."""
    return text.replace('\n', '').replace(' ', '').strip() if isinstance(text, str) else ""

def normalize_header(header_row):
    """헤더 행을 정규화하여 공백과 대소문자를 통일."""
    return [clean_text(cell).lower().replace(" ", "") for cell in header_row]

def table_to_dict(table):
    """테이블 데이터를 딕셔너리 리스트로 변환."""
    keys = ['번호', '명칭', '치수']
    dict_list = []
    for row_idx, row in enumerate(table[1:], start=2):  # 첫 행은 헤더이므로 제외
        # 데이터 디버깅
        # print(f"페이지 테이블 행 {row_idx}: {row}")
        
        # 빈 행 건너뜀
        if all(cell.strip() == "" for cell in row):
            # print(f"빈 행 건너뜀: {row}")
            continue
        
        # 줄바꿈 제거 및 데이터 클리닝
        row = [clean_text(cell.replace('\n', '')) for cell in row]
        
        # 누락된 열은 빈 문자열로 보완
        row = row + [''] * (len(keys) - len(row))
        if len(row) < len(keys):  # 예상보다 짧은 경우 무시
            # print(f"행 {row_idx}가 예상 키 길이에 맞지 않음: {row}")
            continue
        
        # 딕셔너리 변환
        dict_item = {keys[i]: row[i] for i in range(len(keys))}
        dict_list.append(dict_item)
    return dict_list


def validate_dict_data(dict_data, forbidden_words):
    """딕셔너리 데이터를 검증."""
    error_messages = []  # 모든 오류 메시지를 저장할 리스트
    for idx, item in enumerate(dict_data, start=1):
        row_errors = []
        # "번호" 검증 - 숫자여야 하며 부등호 포함 불가
        if not item['번호'].isdigit() or '>' in item['번호'] or '<' in item['번호']:
            row_errors.append(
                f"----잘못된 데이터 형식이 발견되었습니다.('번호'가 숫자가 아님)---- \r\n 사용자 데이터: {item['번호']} \r\n 치수 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다" 
                )

        # "명칭" 검증
        if not item['명칭']:
            row_errors.append(f"'명칭'이 비어 있음")
        else:
            for word in forbidden_words:
                if word in item['명칭']:
                    row_errors.append(
                        f"----사용 불가 단어가 확인되었습니다.---- \r\n 사용자 데이터 : {item['명칭']}\r\n 사용 불가 단어 : {word} \r\n 시행규칙 45조(별표 7 제1호~10호) 내용 확인이 필요합니다."
                        )

        # "치수" 검증 - 숫자여야 하며 부등호 포함 불가
        if not item['치수'].replace('.', '', 1).isdigit() or '>' in item['치수'] or '<' in item['치수']:
            row_errors.append(
                f"----잘못된 데이터 형식이 발견되었습니다.('치수'가 숫자가 아님)---- \r\n 사용자 데이터 : {item['치수']} \r\n 치수 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다"
                )

        if row_errors:
            for row in row_errors :
                error_messages.append(row)    
    return error_messages

def validate_size(file_path):
    """PDF 파일을 읽고 고정 헤더와 비교하며, 고정 헤더 불일치 시 검증을 중단."""
    all_tables = []
    error_messages = []
    validation_stopped = False  # 검증 중단 여부 플래그

    allowed_headers = [normalize_header(['(단위 : mm)'])]  # 허용된 추가 헤더

    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            if validation_stopped:
                break  # 검증 중단 시 남은 페이지 무시

            # print(f"페이지 {page_number} 처리 중...")
            page_tables = page.extract_tables()
            if not page_tables:
                continue

            for table_idx, table in enumerate(page_tables, start=1):
                if validation_stopped:
                    break  # 검증 중단 시 남은 테이블 무시

                # 첫 번째 행 (헤더) 검증
                if not table or not table[0]:
                    error_messages.append(
                        f"페이지 {page_number}, 테이블 {table_idx}: 테이블 헤더가 비어 있음."
                    )
                    continue

                first_row = normalize_header(table[0])
                normalized_fixed_header = normalize_header(fixed_header)
                
                # 헤더가 고정된 형식 또는 허용된 헤더 중 하나와 일치하지 않는 경우
                if first_row != normalized_fixed_header and first_row not in allowed_headers:
                    error_messages.append(
                        f"페이지 {page_number}, 테이블 {table_idx}: 헤더가 고정 헤더와 일치하지 않음. 추출된 헤더: {table[0]}"
                    )
                    validation_stopped = True  # 이후 검증 중단
                    break

                # 딕셔너리 변환
                dict_data = table_to_dict(table)
                # all_tables.extend(dict_data)
                for row in table :
                    add_row = ''
                    for a in row :
                        a = clean_text(a)
                        add_row = add_row + ' ' + a
                    if not clean_text(add_row) == '' and not clean_text(add_row) == clean_text(fixed_header_str):
                        all_tables.append(add_row)
                    
                # 데이터 검증
                errors = validate_dict_data(dict_data, forbidden_words)
                if errors:
                    for error in errors:
                        error_messages.append(error)

    return all_tables, error_messages
