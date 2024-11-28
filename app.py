from scripts.validate.mat_utils import validate_mat, extract_mat
from scripts.validate.size_utils import validate_size, extract_size
from scripts.validate.shape_utils import validate_shape, extract_shape
from scripts.models.predict_label import predict_label

def validate_all_docs(docs):
    # 실제로는 서류 파일을 입력받아 사용해야할 데이터 형식에 맞게 전처리 후 함수 호출 필요
    # 서버 프로젝트 의존성에 파이썬 관련 패키지 추가 필요
    
    # mat file : docs에서 mat에 해당하는 파일
    validate_mat("mat file")
    # shape file : docs에서 shape에 해당하는 파일
    validate_shape("shape file")
    # size file : docs에서 size에 해당하는 파일
    validate_size("size file")
    return


def extract_all_docs(docs):
    mat = extract_mat("mat file")
    shape = extract_shape("shape file")
    size = extract_size("size file")
    
    return [mat, shape, size]

# spring boot 내부에서 ProcessBuilder를 통해 cmd처럼 커맨드를 실행해 app.py를 실행
# 서버 환경에 따라서 호출 방식과 환경변수 삽입 등이 달라질 수 있음
# 결과 변수를 직접 받는게 아니라, 결과를 출력하면 ProcessBuilder로 출력한 결과를 읽어오는 방식
validate_all_docs("이 위치에서 모든 신고서류를 넘겨주면 될 것 같습니다.")
text_list_in_docs = extract_all_docs("이 위치에서 모든 신고서류를 넘겨주면 될 것 같습니다")

mat_result = text_list_in_docs[0]
shape_result = text_list_in_docs[1]
size_result = text_list_in_docs[2]

print(mat_result)
print(shape_result)
print(size_result)

# 입력 문장에 대해 예측한 라벨을 출력하는 함수
# 입력 문장이 단순 string이 아닌 list나 dict형태가 될 경우 그에 맞게 predict_label 함수를 변경해줘야함
predict_label(mat_result)
predict_label(shape_result)
predict_label(size_result)

# 0:접수처리 / 1:모양 및 구조 - 작용원리 / 2:모양 및 구조 - 외형 / 3:모양 및 구조 - 치수
# 4:원재료 / 5:사용목적 / 6:사용방법 / 7:사용 시 주의사항