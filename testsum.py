import os
from collections import defaultdict

def find_folders_with_numeric_files(root_folder, output_file):
    folder_files = defaultdict(list)  # 최상위 폴더별 파일 저장
    
    # 폴더와 하위 폴더 탐색
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            # 확장자를 제거하고 `_` 제거
            name_without_ext = os.path.splitext(filename)[0].replace('_', '')
            # 숫자로만 이루어진 파일인지 확인
            if name_without_ext.isdigit():
                # 최상위 폴더명 가져오기
                relative_path = os.path.relpath(os.path.join(dirpath, filename), root_folder)
                parts = relative_path.split(os.sep)
                if len(parts) >= 2:
                    top_folder = parts[0]
                    folder_files[top_folder].append(name_without_ext)  # 숫자로만 이루어진 파일 추가
    
    # 결과를 텍스트 파일로 저장 (숫자 파일이 2개 이상인 폴더만)
    with open(output_file, 'w', encoding='utf-8') as file:
        for folder, files in folder_files.items():
            if len(files) >= 2:  # 숫자로만 이루어진 파일이 2개 이상인 폴더만 출력
                file.write(f"{folder}\n")  # 폴더명만 출력
    print(f"결과가 {output_file} 파일에 저장되었습니다.")

# 폴더 경로 지정
root_folder = r"C:\Users\USER\Desktop\박창선업무\식약처AI\data7_1_3"  # 최상위 폴더 경로 입력
output_file = r"C:\Users\USER\Desktop\박창선업무\식약처AI\data7_1_3\output_folders.txt"  # 결과를 저장할 파일 경로 입력

# 함수 실행
find_folders_with_numeric_files(root_folder, output_file)
