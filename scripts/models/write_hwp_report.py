
import win32com.client
import os

def save_list_to_hwp(output_path, content_list):
    # 한글(HWP) 객체 생성
    hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
    hwp.RegisterModule("SecurityModuleHnc")  # 보안 모듈 설정
    # 새 문서 생성
    hwp.XHwpWindows.Item(0).InsertNewFile("")

    # 리스트 내용을 HWP 파일에 추가
    for content in content_list:
        hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
        hwp.HParameterSet.HInsertText.Text = content + "\n"  # 줄바꿈 포함
        hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)

    # 파일 저장
    try:
        hwp.SaveAs(output_path, "HWP")
        print(f"HWP 파일이 성공적으로 저장되었습니다: {output_path}")
    except Exception as e:
        print(f"HWP 파일 저장 중 오류가 발생했습니다: {e}")
    finally:
        hwp.Quit()

