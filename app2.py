# from scripts.models.predict_label import predict_label
from scripts.validate.write_hwp_report import *
from scripts.validate.testmat import *
from scripts.validate.read_to_pdf_pfu import *
from scripts.validate.read_to_pdf_shape import *
from scripts.validate.read_to_pdf_size import *
from scripts.validate.read_to_pdf_usage import *
from scripts.validate.read_to_pdf_wp import *
from scripts.validate.read_pdf_file_with_keyword import *
from utils import *
import os
shape_table = []
wp_table = []
size_table = []
mat_table = []
usage_table = []
pfu_table = []

def clean_text(text):
    """텍스트에서 공백 및 줄바꿈을 제거하여 비교를 위한 클리닝."""
    return text.replace('\n', '').replace(' ', '').strip() if isinstance(text, str) else ""

def validate_all_docs(folder_path, code):
    # 실제로는 서류 파일을 입력받아 사용해야할 데이터 형식에 맞게 전처리 후 함수 호출 필요
    # 서버 프로젝트 의존성에 파이썬 관련 패키지 추가 필요
    keywords = ['외형', '작용원리', '치수', '원재료', '사용방법', '주의사항']
    error_messages = []
    all_tables = []
    shape_table = []
    wp_table = []
    size_table = []
    mat_table = []
    usage_table = []
    pfu_table = []
    no_error_files = []
    for keyword in keywords :
        if keyword == '외형':
            shape_file = find_pdf_files_with_keyword(folder_path, keyword)
            print('============================== 외형 파일 검증 ==============================')
            if len(shape_file) == 0:
                error_message = (
                    ' [ 외형 파일이 존재하지 않습니다 ] '
                )
                error_messages.append(error_message)
            else:
                shape_table, shape_error = validate_shape(shape_file[0])
                all_tables.append(shape_table)
                if(type(shape_error) != type(None) and len(shape_error) != 0):
                    error_messages.append(f" [ 외형파일에 검토사항이 검출되었습니다. 오류 검출 개수 : {len(shape_error)} ] ")
                    error_messages.append(shape_error)
                else:
                    no_error_files.append('shape')
                #     error_messages.append(f" [ 외형파일에서 문제가 검출되지 않습니다. ] ")
        elif keyword == '작용원리':
            wp_file = find_pdf_files_with_keyword(folder_path, keyword)
            print('============================== 작용원리 파일 검증 ==============================')
            if len(wp_file) == 0:
                error_message=(
                    ' [ 작용원리 파일이 존재하지 않습니다 ] '
                )
                error_messages.append(error_message)
            else:
                wp_table, wp_error = validate_wp(wp_file[0], code)
                all_tables.append(wp_table)
                if(type(wp_error) != type(None) and len(wp_error) != 0):
                    error_messages.append(f" [ 작용원리파일에 검토사항이 검출되었습니다. 오류 검출 개수 : {len(wp_error)} ] ")
                    error_messages.append(wp_error)   
                else:
                    no_error_files.append('wp')
                #     error_messages.append(f" [ 작용원리파일에서 문제가 검출되지 않습니다. ] ")
        elif keyword == '치수':
            size_file = find_pdf_files_with_keyword(folder_path, keyword)
            print('============================== 치수 파일 검증 ==============================')
            if len(size_file) == 0:
                error_message = (
                    ' [ 치수 파일이 존재하지 않습니다 ] '
                )
                error_messages.append(error_message)
            else:
                size_table, size_error = validate_size(size_file[0])
                all_tables.append(size_table)
                if(type(size_error) != type(None) and len(size_error) != 0):
                    error_messages.append(f" [ 치수파일에 검토사항이 검출되었습니다. 오류 검출 개수 : {len(size_error)} ] ")
                    error_messages.append(size_error)
                else:
                    no_error_files.append('size')
                #     error_messages.append(f" [ 치수파일에서 문제가 검출되지 않습니다. ] ")
        elif keyword == '원재료':
            mat_file = find_pdf_files_with_keyword(folder_path, keyword)
            print('============================== 원재료 파일 검증 ==============================')
            if len(mat_file) == 0:
                error_message = (
                    ' [ 원재료 파일이 존재하지 않습니다 ]'
                )
                error_messages.append(error_message)
            else:
                mat_table, mat_error = validate_mat(mat_file[0])
                all_tables.append(mat_table)
                if(type(mat_error) != type(None) and len(mat_error) != 0):
                    error_messages.append(f" [ 원재료파일에 검토사항이 검출되었습니다. 오류 검출 개수 : {len(mat_error)} ] ")
                    error_messages.append(mat_error)
                else:
                    no_error_files.append('mat')
                #     error_messages.append(f" [ 원재료파일에서 문제가 검출되지 않습니다. ] ")
        elif keyword == '사용방법':
            usage_file = find_pdf_files_with_keyword(folder_path, keyword)
            print('============================== 사용방법 파일 검증 ==============================')
            if len(usage_file) == 0:
                error_message = (
                    ' [ 사용방법 파일이 존재하지 않습니다 ]'
                )
                error_messages.append(error_message)
            else:  
                usage_table, usage_error = validate_usage(usage_file[0], code)
                all_tables.append(usage_table)
                if(type(usage_error) != type(None) and len(usage_error) != 0):
                    error_messages.append(f" [ 사용방법파일에 검토사항이 검출되었습니다. 오류 검출 개수 : {len(usage_error)} ] ")
                    error_messages.append(usage_error)
                else:
                    no_error_files.append('usage')
                #     error_messages.append(f" [ 사용방법파일에서 문제가 검출되지 않습니다. ] ")
        elif keyword == '주의사항':
            pfu_file = find_pdf_files_with_keyword(folder_path, keyword)
            print('============================== 주의사항 파일 검증 ==============================')
            if len(pfu_file) == 0 :
                error_message = (
                    ' [ 주의사항 파일이 존재하지 않습니다] '
                )
                error_messages.append(error_message)
            else:
                pfu_table, pfu_error = validate_pfu(pfu_file[0], code)
                all_tables.append(pfu_table)
                if(type(pfu_error) != type(None) and len(pfu_error) != 0):
                    error_messages.append(f" [ 주의사항파일에 검토사항이 검출되었습니다. 검출 개수 : {len(pfu_error)} ] ")
                    error_messages.append(pfu_error)
                else:
                    no_error_files.append('pfu')
                #     error_messages.append(f" [ 주의사항파일에서 문제가 검출되지 않습니다. ] ")
        else:
            print()
    return all_tables, error_messages, no_error_files
# return shape_table, shape_error, size_table, size_error, mat_table, mat_error, wp_table, wp_error, usage_table, usage_error, pfu_table, pfu_error

# spring boot 내부에서 ProcessBuilder를 통해 cmd처럼 커맨드를 실행해 app.py를 실행
# 서버 환경에 따라서 호출 방식과 환경변수 삽입 등이 달라질 수 있음
# 결과 변수를 직접 받는게 아니라, 결과를 출력하면 ProcessBuilder로 출력한 결과를 읽어오는 방식

# 1 : 스타킹형 2 : 벨트형 3 : 자가점착형
folder_path = r"C:\Users\USER\Desktop\test2"
folder_list = get_folders(folder_path)

all_tables = []
error_messages = []
no_error_files = []

# TODO 규칙 기반 검증 후 에러 메시지가 없는 파일은 KoBERT 검증을 통해 생성된 에러 메시지를 저장
# error messages로 받는게 아닌, 형태 별 에러메시지를 따로 저장해서 return 받을 것
for folder in folder_list:
    
    num = os.path.basename(folder).split("_")[0]
    if '스타킹' in folder:
        all_tables, error_messages, no_error_files = validate_all_docs(folder, 1)
    elif '벨트형' in folder:
        all_tables, error_messages, no_error_files = validate_all_docs(folder, 2)
    elif '점착형' in folder:
        all_tables, error_messages, no_error_files = validate_all_docs(folder, 3)
    else:
        print('폴더명이 맞지 않아요')
    
    if error_messages:
        print("에러 검증 진행 중===========================")
        error_result = []
        for errors in error_messages:
            if errors != None and type(errors) == list:
                for row in errors:
                    if row != None:
                        error_result.append(row)
            else: error_result.append(errors)
        save_filepath = fr"C:\Users\USER\Desktop\report1\report{num}.hwp"
        save_list_to_hwp(save_filepath, error_result)
    elif not error_messages and no_error_files :
        pass
        # for no_error_file in no_error_files:
        #     pass
        # kobert_result = []
        # for table in all_tables:
        #     if table != None and type(table) == list:
        #         temp = ''
        #         for row in table:
        #             if row != None and type(row) == str and not clean_text(row) == '':
        #                 temp += row
        #         kobert_result.append(predict_label(temp))
        #     else:
        #         if table != None and type(table) == str and not clean_text(table) == '':
        #             kobert_result.append(predict_label(table))
        # save_filepath = folder + fr"/report{num}.hwp"
        # save_list_to_hwp(save_filepath, kobert_result)