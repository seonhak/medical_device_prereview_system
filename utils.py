import pdfplumber
import os
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


def get_text_from_pdf(file_path) :
    path = ''
    if type(file_path) == list:
        for item in file_path:
            path += item
    else:
        path = file_path
    error_messages = []
    result = ''
    try : 
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if not tables :
                    result = page.extract_text()
                else: 
                    for table in tables:
                        for row in table:
                            for str in row :
                                result += clean_text(str) + ' '
            return result
    except :         
        error_messages.append(f"cannot export text from : {path}")
        print(error_messages)

def get_folders(folder_path):
    """
    주어진 폴더의 PDF 파일에서 텍스트를 추출하고 CSV로 저장
    """
    rows = []
    for root, _, files in os.walk(folder_path):
        if folder_path != root and root:
            rows.append(root)
        
    return rows