import win32com.client
import re

def save_list_to_hwp(output_path, content_list):
    # HWP 객체 생성
    hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
    # hwp1 = win32com.client.Dispatch("HwpCtrl.HwpObject")
    # 새 문서 생성
    hwp.HAction.GetDefault("NewFile", hwp.HParameterSet.HFileOpenSave.HSet)
    hwp.HAction.Execute("NewFile", hwp.HParameterSet.HFileOpenSave.HSet)
    
    # 리스트 내용을 HWP 파일에 추가
    if content_list:
        hwp.Run("MoveDocEnd")  # 문서 끝으로 이동
        hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
        hwp.HParameterSet.HInsertText.Text = f"신고서류 사전검토에 대한 보완 안내\r\n\r\n"
        hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
        for content in content_list:
            hwp.Run("MoveDocEnd")  # 문서 끝으로 이동
            hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
            # 변환된 텍스트 사용
            converted_content = convert_number_to_circle(content)
            hwp.HParameterSet.HInsertText.Text = converted_content + '\r\n'
            hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
    else:
        hwp.Run("MoveDocEnd")  # 문서 끝으로 이동
        hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
        hwp.HParameterSet.HInsertText.Text = '검토필요사항을 발견하지 못했습니다.'
        hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
        
    # 파일 저장
    try:
        hwp.HAction.GetDefault("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)  # 파일 저장 액션의 파라미터를
        hwp.HParameterSet.HFileOpenSave.filename = output_path
        hwp.HParameterSet.HFileOpenSave.Format = "HWP"
        hwp.HAction.Execute("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
        print(f"HWP 파일이 성공적으로 저장되었습니다: {output_path}")
    except Exception as e:
        print(f"HWP 파일 저장 중 오류가 발생했습니다: {e}")
    finally:
        hwp.Quit()

def convert_number_to_circle(text):
    # 입력값이 문자열이 아닌 경우 문자열로 변환
    if not isinstance(text, str):
        text = str(text)
    
    # 1-20까지의 원형 숫자 매핑
    circle_numbers = {
        str(i): chr(0x2460 + i - 1) for i in range(1, 21)
    }
    
    # "숫자." 패턴 찾기
    pattern = r'^\d+\.'
    
    match = re.match(pattern, text[:2])
    
    if match:
        num = match.group().rstrip('.')  # 숫자만 추출
        if num in circle_numbers:
            # 원형 숫자로 변환하고 나머지 텍스트 유지
            return circle_numbers[num] + text[len(match.group()):]
    return text