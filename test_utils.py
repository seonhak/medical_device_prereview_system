import pdfplumber
import os
from scripts.models.predict_label import predict_label
from scripts.validate.write_hwp_report import *
from scripts.validate.testmat import *
from scripts.validate.read_to_pdf_pfu import *
from scripts.validate.read_to_pdf_shape import *
from scripts.validate.read_to_pdf_size import *
from scripts.validate.read_to_pdf_usage import *
from scripts.validate.read_to_pdf_wp import *
from scripts.validate.read_pdf_file_with_keyword import *

def clean_text(text):
    """텍스트에서 공백 및 줄바꿈을 제거하여 비교를 위한 클리닝."""
    return text.replace('\n', '').replace(' ', '').strip() if isinstance(text, str) else ""

def is_valid_pdf(file_path):
    """
    PDF 파일이 유효한지 확인합니다.
    깨진 파일일 경우 False를 반환합니다.
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            # 페이지가 존재하는지 확인
            if len(pdf.pages) > 0:
                return True
            else:
                print(f"No pages found in PDF: {file_path}")
                return False
    except Exception as e:
        print(f"Error reading PDF: {file_path} - {e}")
        return False


def validate(shape_code, file_path) :
    print(f"code : {shape_code}, path : {file_path}")


def process_directories(root_folder, output_root):
    """
    주어진 루트 디렉토리에서 형태코드를 추출하고 validate() 호출.
    """
    if not os.path.exists(root_folder):
        print(f"Root folder '{root_folder}' does not exist.")
        return

    # 루트 디렉토리 내부 디렉토리 순회
    for dir_name in os.listdir(root_folder):
        dir_path = os.path.join(root_folder, dir_name)
        if not os.path.isdir(dir_path):
            continue

        # 형태코드 추출 (맨 앞 숫자 부분)
        shape_code = dir_name.split("_")[0]

        # 디렉토리 내 파일 순회
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            if os.path.isfile(file_path):
                # 경로를 통일하여 '/'로 변환
                validate(shape_code, file_path.replace("\\", "/"))

def get_text_from_pdf(file_path) :
    error_messages = []
    result = ''
    try : 
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if not tables :
                    result = page.extract_text()
                else: 
                    for table in tables:
                        # print(table)
                        for row in table:
                            for str in row :
                                if str and is_in_fixed(clean_text(str)):
                                    break
                                elif str:
                                    result += clean_text(str) + ' '
            return result
    except :         
        error_messages.append(f"cannot read {file_path}")
        print(error_messages)


def is_in_fixed(str):
    fixed_list = ['기재하는경우','일련번호','원재료명또는성분명','분량','비고',]
    for item in fixed_list :
        # print(f"{item} / {clean_text(str)} 비교")
        if item in str:
            return True
    return False

def get_folders(folder_path):
    """
    주어진 폴더의 PDF 파일에서 텍스트를 추출하고 CSV로 저장
    """
    rows = []
    for root, _, files in os.walk(folder_path):
        if folder_path != root and root:
            rows.append(root)
        
    return rows

