import os

def save_error_to_file(error_message, pdf_file_path, append_mode=True):
    """
    에러 메시지를 PDF 파일 경로를 기반으로 한 폴더에 저장.
    중복된 파일 생성을 방지하며, 파일이 이미 존재하면 추가로 기록.
    :param error_message: 저장할 에러 메시지
    :param pdf_file_path: PDF 파일 경로
    :param append_mode: 기존 파일에 추가로 기록 여부 (기본값: True)
    """
    # PDF 파일 이름 가져오기
    pdf_file_name = os.path.splitext(os.path.basename(pdf_file_path))[0]

    # PDF 파일 경로에서 디렉토리 추출
    folder_path = os.path.dirname(pdf_file_path)

    # 디렉토리가 없으면 생성
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"폴더 생성됨: {folder_path}")

    # 에러 로그 파일명 생성 (PDF 파일 이름 포함)
    log_file_name = f"error_log_{pdf_file_name}.txt"
    log_file_path = os.path.join(folder_path, log_file_name)

    # 에러 메시지 저장
    try:
        with open(log_file_path, "a" if append_mode else "w", encoding="utf-8") as file:
            file.write(f"{error_message}\n")
        print(f"에러 메시지가 다음 경로에 저장되었습니다: {log_file_path}")
    except Exception as e:
        print(f"에러 메시지를 파일에 저장하는 중 문제가 발생했습니다: {e}")
