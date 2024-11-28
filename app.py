from scripts.validate.validate_mat import validate_mat
from scripts.validate.validate_size import validate_size
from scripts.validate.validate_shape import validate_shape
from scripts.models.predict_label import predict_label

def validate_all_docs():
    # 실제로는 서류 파일을 입력받아 사용해야할 데이터 형식에 맞게 전처리 후 함수 호출 필요
    # 서버 프로젝트 의존성에 파이썬 관련 패키지 추가 필요
    
    validate_mat()
    validate_shape()
    validate_size()

# spring boot 내부에서 ProcessBuilder를 통해 cmd처럼 커맨드를 실행해 app.py를 실행
# 서버 환경에 따라서 호출 방식과 환경변수 삽입 등이 달라질 수 있음
# 결과 변수를 직접 받는게 아니라, 결과를 출력하면 ProcessBuilder로 출력한 결과를 읽어오는 방식
validate_all_docs()

# 입력 문장에 대해 예측한 라벨을 출력하는 함수
# 입력 문장이 단순 string이 아닌 list나 dict형태가 될 경우 그에 맞게 predict_label 함수를 변경해줘야함
predict_label("Nylon 109%가나다 우아으이에 ㅇ오오아누니")

# 0:접수처리 / 1:모양 및 구조 - 작용원리 / 2:모양 및 구조 - 외형 / 3:모양 및 구조 - 치수
# 4:원재료 / 5:사용목적 / 6:사용방법 / 7:사용 시 주의사항