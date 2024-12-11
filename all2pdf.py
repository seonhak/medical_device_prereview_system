import os
import win32com.client
import pythoncom

# HWP 파일을 PDF로 변환
def convert_hwp_to_pdf_windows(hwp_file, output_pdf):
    print(f"Converting HWP file to PDF: {hwp_file} (Windows)")
    pythoncom.CoInitialize()  # 스레드에서 COM을 초기화합니다.
    try:
        hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
        hwp.RegisterModule("FilePathCheckDLL", "SecurityModuleHnc")
        hwp.Open(hwp_file, Format="HWP", arg="versionwarning:False")
        hwp.SaveAs(output_pdf, "PDF", "Download")
        hwp.Quit()
    except Exception as e:
        print(f"Failed to convert HWP to PDF: {hwp_file} due to {e}")
    finally:
        pythoncom.CoUninitialize()

# DOCX 파일을 PDF로 변환
def convert_docx_to_pdf_windows(docx_file, output_pdf):
    try:
        print(f"Converting DOCX file to PDF: {docx_file} (Windows)")
        word = win32com.client.Dispatch("Word.Application")
        doc = word.Documents.Open(docx_file)
        doc.SaveAs(output_pdf, FileFormat=17)
        doc.Close()
        word.Quit()
    except Exception as e:
        print(f"Failed to convert DOCX to PDF: {docx_file} due to {e}")

# PPTX 파일을 PDF로 변환
def convert_pptx_to_pdf_windows(pptx_file, output_pdf):
    try:
        print(f"Converting PPTX file to PDF: {pptx_file} (Windows)")
        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        ppt = powerpoint.Presentations.Open(pptx_file, WithWindow=False)
        ppt.SaveAs(output_pdf, 32)
        ppt.Close()
        powerpoint.Quit()
    except Exception as e:
        print(f"Failed to convert PPTX to PDF: {pptx_file} due to {e}")

# XLSX 파일을 PDF로 변환
def convert_xlsx_to_pdf_windows(xlsx_file, output_pdf):
    try:
        print(f"Converting XLSX file to PDF: {xlsx_file} (Windows)")
        excel = win32com.client.Dispatch("Excel.Application")
        workbook = excel.Workbooks.Open(xlsx_file)
        workbook.ExportAsFixedFormat(0, output_pdf)
        workbook.Close(False)
        excel.Quit()
    except Exception as e:
        print(f"Failed to convert XLSX to PDF: {xlsx_file} due to {e}")

# 폴더를 순회하며 파일을 PDF로 변환하고 저장
def traverse_and_convert_to_pdf(root_folder, output_root):
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            file_path = os.path.join(root, file)  # 현재 파일의 전체 경로
            output_pdf_path = os.path.join(output_root, os.path.relpath(root, start=root_folder))
            output_pdf_path = os.path.join(output_pdf_path, os.path.splitext(file)[0] + '.pdf')
            
            os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)  # 출력 폴더 생성
            
            print(f"Processing file: {file_path}")
            
            if file.endswith('.hwp'):
                convert_hwp_to_pdf_windows(file_path, output_pdf_path)
            elif file.endswith('.docx'):
                convert_docx_to_pdf_windows(file_path, output_pdf_path)
            elif file.endswith('.pptx'):
                convert_pptx_to_pdf_windows(file_path, output_pdf_path)
            elif file.endswith('.xlsx'):
                convert_xlsx_to_pdf_windows(file_path, output_pdf_path)
            elif file.endswith('.pdf'):
                # PDF 파일은 그대로 복사
                os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
                if not os.path.exists(output_pdf_path):
                    os.rename(file_path, output_pdf_path)
            else:
                print(f"Unsupported file format: {file_path}")

# 원본 폴더 경로와 출력 폴더 경로
# 원본 폴더 경로와 출력 폴더 경로
original_root = os.path.abspath(r"C:\Users\USER\Desktop\검증용자료 20개\변경후\44-50")  # 절대 경로로 변환
output_root = os.path.abspath(r"C:\Users\USER\Desktop\검증용자료 20개\변경후_pdf")  # 절대 경로로 변환

# 파일을 탐색하며 PDF로 변환하여 저장
print(f"Starting PDF conversion process for folder: {original_root}")
traverse_and_convert_to_pdf(original_root, output_root)
print(f"PDF conversion process completed. Files saved to: {output_root}")
