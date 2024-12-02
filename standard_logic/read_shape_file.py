from readpdf import *
import os
import os
import re
from read_to_pdf_shape import *
from forbidden_words import *
def find_pdf_files_with_keyword(folder_path, keyword="외형"):
    """
    폴더에서 파일 이름에 특정 키워드가 포함되고, 확장자가 PDF인 파일을 검색합니다.
    키워드 내 공백 및 구분자 무시 처리.
    
    :param folder_path: 검색할 폴더 경로
    :param keyword: 검색할 키워드 (기본값: "외형")
    :return: 검색된 파일 경로 리스트
    """
    found_files = []

    # 키워드를 공백 및 구분자를 무시하는 정규식으로 변환
    keyword_pattern = r'[ \s_.\-]*'.join(keyword)  # 예: "원\s*재\s*료"

    # 폴더가 유효한지 확인
    if not os.path.isdir(folder_path):
        print(f"유효하지 않은 폴더 경로: {folder_path}")
        return found_files

    # 폴더 내 파일 검색
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 확장자가 PDF인지 확인
            if not file.lower().endswith(".pdf"):
                continue
            
            # 파일 이름에서 키워드 정규식 매칭
            if re.search(keyword_pattern, file, re.IGNORECASE):
                found_files.append(os.path.join(root, file))

    return found_files

folder_path = r'C:\Users\USER\Desktop\박창선업무\2024-11-27 - 12-02\압박용밴드 형태별 의료기기 표준서식_test\압박용밴드 형태별 의료기기 표준서식\압박용밴드_스타킹형태 서식'

# 테스트
if __name__ == "__main__":
    pdf_files = find_pdf_files_with_keyword(folder_path, keyword="외형")
    
    if not pdf_files:
        print("조건에 맞는 파일이 없습니다.")
    else:
        for pdf_file in pdf_files:
            print(f"PDF 파일 처리 시작: {pdf_file}")
            validate_pdf_with_dict(pdf_file, fixed_header, forbidden_words)

