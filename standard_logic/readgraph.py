import pdfplumber
from readpdf import pdf_file_path

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

def transpose_table(table):
    """
    표 데이터를 전치하여 위에서 아래로 읽도록 변환합니다.
    """
    return list(map(list, zip(*table)))

def process_pdf_table(file_path):
    """
    PDF 파일에서 모든 표 데이터를 위에서 아래로 읽도록 처리.
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            tables = []
            for page_number, page in enumerate(pdf.pages, start=1):
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)

            if not tables:
                print("표 데이터를 찾을 수 없습니다.")
                return

            # 표 데이터 정리
            cleaned_tables = clean_table_data(tables)

            # 표 데이터 전치 및 출력
            for table_index, table in enumerate(cleaned_tables, start=1):
                transposed_table = transpose_table(table)
                print(f"\n[표 {table_index} (위에서 아래)]")
                for row in transposed_table:
                    print(row)

    except Exception as e:
        print(f"PDF 처리 중 오류 발생: {e}")

# 실행
if __name__ == "__main__":
    process_pdf_table(pdf_file_path)
