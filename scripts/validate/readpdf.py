import pdfplumber

def read_pdf_to_memory(file_path):
    """
    PDF 파일을 읽고 내용을 메모리에 로드하여 출력합니다.
    :param file_path: PDF 파일 경로
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            # 모든 페이지의 내용을 읽어서 하나의 문자열로 합칩니다.
            pdf_text = ""
            for page in pdf.pages:
                pdf_text += page.extract_text() + "\n"  # 각 페이지의 텍스트를 추출하고 줄바꿈 추가

            # 메모리에 로드된 텍스트 출력
            print("PDF 내용 출력:")
            print(pdf_text)

            return pdf_text  # 추출된 텍스트를 반환

    except Exception as e:
        print(f"PDF를 읽는 중 오류 발생: {e}")
        return None

# 테스트
# pdf_file_path = r"C:\Users\USER\Desktop\박창선업무\2024-11-27\압박용밴드 형태별 의료기기 표준서식_test\압박용밴드 형태별 의료기기 표준서식\압박용밴드_스타킹형태 서식\원재료_test.pdf"
# read_pdf_to_memory(pdf_file_path)
