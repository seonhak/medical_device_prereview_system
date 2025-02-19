from scripts.models.predict_label import predict_label
from scripts.validate.write_hwp_report import *
from scripts.validate.read_to_pdf_pfu import *
from scripts.validate.read_to_pdf_shape import *
from scripts.validate.read_to_pdf_size import *
from scripts.validate.read_to_pdf_usage import *
from scripts.validate.read_to_pdf_wp import *
from scripts.validate.read_to_pdf_mat import *
from scripts.validate.read_pdf_file_with_keyword import *
from utils import *
import os
shape_table = []
wp_table = []
size_table = []
mat_table = []
usage_table = []
pfu_table = []
keywords = ['외형', '작용원리', '치수', '원재료', '사용방법', '주의사항']
def clean_text(text):
    """텍스트에서 공백 및 줄바꿈을 제거하여 비교를 위한 클리닝."""
    return text.replace('\n', '').replace(' ', '').strip() if isinstance(text, str) else ""

def validate_all_docs(folder_path, code):
    # 서류 파일을 입력받아 사용해야할 데이터 형식에 맞게 전처리 후 함수 호출 필요
    # 서버 프로젝트 의존성에 파이썬 관련 패키지 추가 필요
    error_messages = []
    all_tables = []
    shape_table = []
    wp_table = []
    size_table = []
    mat_table = []
    usage_table = []
    pfu_table = []
    for keyword in keywords :
        label = 0
        if keyword == '외형':
            shape_file = find_pdf_files_with_keyword(folder_path, keyword)
            error_messages.append(f"가. 모양 및 구조-외형")
            if len(shape_file) == 0:
                error_messages.append(f"[민원 서류 사전 검토 결과 모양 및 구조-외형 파일을 발견하지 못했습니다]\r\n")
            else:
                shape_table, shape_error, error_count = validate_shape(shape_file[0])
                all_tables.append(shape_table)
                label = predict_label(get_text_from_pdf(shape_file[0]))
                if label == 1:
                    error_messages.append(
                        f"{error_count}. 신고서류 치수 파일에서 검토사항이 있는 것으로 확인됩니다. " +
                        f"관련 규정은 치수 - 규정 제9조(모양 및 구조)를 확인하시고, SI 단위를 표기하신 후 제출하시기 바랍니다.\r\n"
                    )
                if(type(shape_error) != type(None) and len(shape_error) != 0):
                    error_messages.append(f"[신고 서류 사전 검토 결과 다음과 같은 재검토 사항을 발견하였습니다]")
                    error_messages.append(shape_error)
                elif len(shape_error) == 1:
                    error_messages.append(f"[민원 서류 사전 검토 결과 보완 사항을 발견하지 못했습니다]\r\n")
        elif keyword == '작용원리':
            wp_file = find_pdf_files_with_keyword(folder_path, keyword)
            error_messages.append(f"나. 모양 및 구조-작용원리")
            if len(shape_file) == 0:
                error_messages.append(f"[민원 서류 사전 검토 결과 모양 및 구조-작용원리 파일을 발견하지 못했습니다]\r\n")
            else:
                wp_table, wp_error, error_count = validate_wp(wp_file[0], code)
                all_tables.append(wp_table)
                label = predict_label(get_text_from_pdf(wp_file[0]))
                if label == 1:
                    error_messages.append(
                        f"{error_count}. 신고서류 치수 파일에서 검토사항이 있는 것으로 확인됩니다. " +
                        f"관련 규정은 치수 - 규정 제9조(모양 및 구조)를 확인하시고, SI 단위를 표기하신 후 제출하시기 바랍니다.\r\n"
                    )
                if(type(wp_error) != type(None) and len(wp_error) != 0):
                    error_messages.append(f"[신고 서류 사전 검토 결과 다음과 같은 재검토 사항을 발견하였습니다]")
                    error_messages.append(wp_error)
                elif len(shape_error) == 1:
                    error_messages.append(f"[민원 서류 사전 검토 결과 보완 사항을 발견하지 못했습니다]\r\n")
        elif keyword == '치수':
            size_file = find_pdf_files_with_keyword(folder_path, keyword)
            error_messages.append(f"다. 모양 및 구조-치수")
            if len(shape_file) == 0:
                error_messages.append(f"[민원 서류 사전 검토 결과 모양 및 구조-치수 파일을 발견하지 못했습니다]\r\n")
            else:
                size_table, size_error, error_count = validate_size(size_file[0])
                all_tables.append(size_table)
                label = predict_label(get_text_from_pdf(size_file[0]))
                if label == 1:
                    error_messages.append(
                        f"{error_count}. 신고서류 치수 파일에서 검토사항이 있는 것으로 확인됩니다. " +
                        f"관련 규정은 치수 - 규정 제9조(모양 및 구조)를 확인하시고, SI 단위를 표기하신 후 제출하시기 바랍니다.\r\n"
                        )
                if(type(size_error) != type(None) and len(size_error) != 0):
                    error_messages.append(f"[신고 서류 사전 검토 결과 다음과 같은 재검토 사항을 발견하였습니다]")
                    error_messages.append(size_error)
                elif len(shape_error) == 1:
                    error_messages.append(f"[민원 서류 사전 검토 결과 보완 사항을 발견하지 못했습니다]\r\n")
        elif keyword == '원재료':
            mat_file = find_pdf_files_with_keyword(folder_path, keyword)
            error_messages.append(f"라. 원재료")
            if len(shape_file) == 0:
                error_messages.append(f"[민원 서류 사전 검토 결과 원재료 파일을 발견하지 못했습니다]\r\n")
            else:
                mat_table, mat_error, error_count = validate_mat(mat_file[0])
                all_tables.append(mat_table)
                label = predict_label(get_text_from_pdf(mat_file))
                if label == 1:
                    error_messages.append(
                        f"{error_count}. 신고서류 치수 파일에서 검토사항이 있는 것으로 확인됩니다. " +
                        f"관련 규정은 치수 - 규정 제9조(모양 및 구조)를 확인하시고, SI 단위를 표기하신 후 제출하시기 바랍니다.\r\n"
                    )
                if(type(mat_error) != type(None) and len(mat_error) != 0):
                    error_messages.append(f"[신고 서류 사전 검토 결과 다음과 같은 재검토 사항을 발견하였습니다]")
                    error_messages.append(mat_error)
                elif len(shape_error) == 1:
                    error_messages.append(f"[민원 서류 사전 검토 결과 보완 사항을 발견하지 못했습니다]\r\n")
        elif keyword == '사용방법':
            usage_file = find_pdf_files_with_keyword(folder_path, keyword)
            error_messages.append(f"마. 사용방법")
            if len(shape_file) == 0:
                error_messages.append(f"[민원 서류 사전 검토 결과 사용방법 파일을 발견하지 못했습니다]\r\n")
            else:  
                usage_table, usage_error, error_count = validate_usage(usage_file[0], code)
                all_tables.append(usage_table)
                label = predict_label(get_text_from_pdf(usage_file[0]))
                if label == 1:
                    error_messages.append(
                        f"{error_count}. 신고서류 치수 파일에서 검토사항이 있는 것으로 확인됩니다. " +
                        f"관련 규정은 치수 - 규정 제9조(모양 및 구조)를 확인하시고, SI 단위를 표기하신 후 제출하시기 바랍니다.\r\n"
                    )
                if(type(usage_error) != type(None) and len(usage_error) != 0):
                    error_messages.append(f"[신고 서류 사전 검토 결과 다음과 같은 재검토 사항을 발견하였습니다]")
                    error_messages.append(usage_error)
                elif len(shape_error) == 1:
                    error_messages.append(f"[민원 서류 사전 검토 결과 보완 사항을 발견하지 못했습니다]\r\n")
        elif keyword == '주의사항':
            pfu_file = find_pdf_files_with_keyword(folder_path, keyword)
            error_messages.append(f"바. 사용 시 주의사항")
            if len(shape_file) == 0:
                error_messages.append(f"[민원 서류 사전 검토 결과 사용 시 주의사항 파일을 발견하지 못했습니다]\r\n")
            else:
                pfu_table, pfu_error, error_count = validate_pfu(pfu_file[0], code)
                all_tables.append(pfu_table)
                label = predict_label(get_text_from_pdf(pfu_file[0]))
                if label == 1:
                    error_messages.append(
                        f"{error_count}. 신고서류 치수 파일에서 검토사항이 있는 것으로 확인됩니다. " +
                        f"관련 규정은 치수 - 규정 제9조(모양 및 구조)를 확인하시고, SI 단위를 표기하신 후 제출하시기 바랍니다.\r\n"
                    )
                if(type(pfu_error) != type(None) and len(pfu_error) != 0):
                    error_messages.append(f"[신고 서류 사전 검토 결과 다음과 같은 재검토 사항을 발견하였습니다]")
                    error_messages.append(pfu_error)
                elif len(shape_error) == 1:
                    error_messages.append(f"[민원 서류 사전 검토 결과 보완 사항을 발견하지 못했습니다]\r\n")
        else:
            pass
    return all_tables, error_messages

# spring boot 내부에서 ProcessBuilder를 통해 cmd처럼 커맨드를 실행해 app.py를 실행
# 서버 환경에 따라서 호출 방식과 환경변수 삽입 등이 달라질 수 있음

# 형태코드 1 : 스타킹형 2 : 벨트형 3 : 자가점착형
# 현재 폴더에 넣어놓은 데이터에서 폴더명에 입력돼있는 형태코드를 입력받아 사용용
folder_path = r"C:\Users\USER\Desktop\식약처\고도화\검증용 데이터 9건_추가정답11개\test"
folder_list = get_folders(folder_path)

all_tables = []
error_messages = []
kobert_result = []
for folder in folder_list:
    
    num = os.path.basename(folder).split("_")[0]
    if '스타킹' in folder:
        all_tables, error_messages = validate_all_docs(folder, 1)
    elif '벨트형' in folder:
        all_tables, error_messages = validate_all_docs(folder, 2)
    elif '점착형' in folder:
        all_tables, error_messages = validate_all_docs(folder, 3)
    else:
        pass
    
    error_result = []
    for errors in error_messages:
        if errors != None and type(errors) == list:
            for row in errors:
                if row != None:
                    error_result.append(row)
        else: error_result.append(errors)
    save_filepath = folder + fr"/report{num}.hwp"
    save_list_to_hwp(save_filepath, error_result)
