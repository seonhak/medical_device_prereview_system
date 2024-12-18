import win32com.client

def save_list_to_hwp(output_path, content_list):
    # HWP 객체 생성
    hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
    # hwp1 = win32com.client.Dispatch("HwpCtrl.HwpObject")
    # 새 문서 생성
    hwp.HAction.GetDefault("NewFile", hwp.HParameterSet.HFileOpenSave.HSet)
    hwp.HAction.Execute("NewFile", hwp.HParameterSet.HFileOpenSave.HSet)

    # 리스트 내용을 HWP 파일에 추가
    if content_list:
        for content in content_list:
            if type(content) == list:
                for item in content:
                    hwp.Run("MoveDocEnd")  # 문서 끝으로 이동
                    hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
                    hwp.HParameterSet.HInsertText.Text = '\r\n'+ item + '\r\n'
                    hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)    
            else:
                hwp.Run("MoveDocEnd")  # 문서 끝으로 이동
                hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
                hwp.HParameterSet.HInsertText.Text = '\r\n' + content + '\r\n'
                hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
    else:
        hwp.Run("MoveDocEnd")  # 문서 끝으로 이동
        hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
        hwp.HParameterSet.HInsertText.Text = '검토필요사항을 발견하지 못했습니다.' + '\r\n'
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

# 실행

# content_list = ["첫 번째 줄", "두 번째 줄"]
# save_list_to_hwp(output_path, content_list)

# try:
#     hwp = win32com.client.Dispatch("HwpCtrl.HwpObject")
#     print("HwpCtrl.HwpObject로 객체 생성 성공")
# except Exception as e1:
#     print(f"HwpCtrl.HwpObject 실패: {e1}")
#     try:
#         hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
#         print("HWPFrame.HwpObject로 객체 생성 성공")
#     except Exception as e2:
#         print(f"HWPFrame.HwpObject 실패: {e2}")