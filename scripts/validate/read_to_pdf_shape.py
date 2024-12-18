import pdfplumber
from .forbidden_words import forbidden_words  # 금지 단어 리스트
from .save_error_to_txt import save_error_to_file  # 에러 저장 함수
# 외형

fixed_header = ['번호', '명칭', '기능 및 역할']
fixed_header_str = '번호명칭기능및역할'

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
        if any(keyword in item['번호'] for keyword in ['외관사진', '외관설명']):
            continue
        else:
            if item['번호'] is None or str(item['번호']).strip() == '':
                row_errors.append(
                    f" 신고서류 내 검토필요사항 : {item['번호']} \r\n 검토사항 발생 요인 : 잘못된 데이터 형식이 발견되었습니다.('번호'가 숫자가 아님) \r\n 검토사항에 대한 근거 : 외형 - 규정 제9조(모양 및 구조) 내용 확인이 필요합니다" 
                    )
            # "명칭" 검증
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
def table_to_list(table):
    """테이블 데이터를 리스트 형태로 변환."""
    result_list = []
    for row in table[1:]:  # 첫 행은 헤더이므로 제외
        clean_row = [clean_text(cell) for cell in row]
        result_list.append(clean_row)
    return result_list
def validate_shape(file_path):
    """PDF 파일을 읽고 테이블 데이터를 리스트로 추출 및 검증."""
    all_tables = []  # 모든 테이블 데이터를 리스트로 저장
    error_messages = []  # 검증 중 발생한 에러 메시지 저장
    current_table_data = []  # 현재 검증 중인 테이블 데이터
    validation_in_progress = False  # 검증 활성화 여부

    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            # 페이지의 테이블 데이터 추출
            page_tables = page.extract_tables()
            if not page_tables:  # 테이블이 없으면 건너뛴다.
                continue

            for table in page_tables:
                if not table or len(table) == 0:  # 테이블이 비어있을 경우 처리
                    continue

                # 첫 번째 행 검증 (정규화된 비교)
                first_row = normalize_header(table[0])
                normalized_fixed_header = normalize_header(fixed_header)

                # `fixed_header`가 나타나는 경우
                if first_row == normalized_fixed_header:
                    # 이전 검증 데이터 처리
                    if validation_in_progress:
                        dict_data = table_to_dict(current_table_data)
                        errors = validate_dict_data(dict_data, forbidden_words)
                        error_messages.extend(errors)
                        all_tables.extend(current_table_data)
                        current_table_data = []  # 현재 테이블 데이터 초기화

                    # 새로운 검증 시작
                    validation_in_progress = True
                    continue  # 헤더는 처리하지 않음

                # 검증 활성화 상태일 때만 데이터 추가
                if validation_in_progress:
                    table_data = table_to_list(table)  # 테이블 데이터를 리스트로 변환
                    if table_data:
                        current_table_data.extend(table_data)

        # 마지막 검증 데이터 처리
        if validation_in_progress and current_table_data:
            dict_data = table_to_dict(current_table_data)
            errors = validate_dict_data(dict_data, forbidden_words)
            error_messages.extend(errors)
            all_tables.extend(current_table_data)

    return all_tables, error_messages





