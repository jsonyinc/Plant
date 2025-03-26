import firebase_admin
from firebase_admin import credentials, firestore, auth
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# 환경변수 로드: .env 파일에서 설정값 가져오기
load_dotenv()
key_path = os.getenv("SERVICE_ACCOUNT_KEY_PATH")

# Flask 앱 초기화: 사서 창구를 여는 코드 (Flask는 API를 만드는 도구예요)
app = Flask(__name__)
CORS(app)  # React와 대화할 수 있게 허용 (CORS는 다른 앱과의 연결을 허용해줘요)

# Firebase Admin SDK 초기화: 도서관 문을 여는 코드
cred = credentials.Certificate(key_path)  # 도서관 열쇠 파일 경로
firebase_admin.initialize_app(cred)  # 도서관 문 열기
db = firestore.client()  # 도서관 안으로 들어가기

# 로컬호스트 루트주소 접속시 보여줄 메시지(API 구동여부 테스트 환경용)
@app.route('/')  # 루트 URL 추가
def home():
    return "Hello, Flask!"

# 사용자 생성 API: "/create_user"라는 창구를 만드는 코드
@app.route('/create_user', methods=['POST'])  # POST 요청만 받음 (새로운 데이터를 만들 때 사용)
def create_user():
    try:
        # 요청 데이터 받기: 사용자가 보낸 정보를 받아요
        data = request.json
        # 데이터 검증: 필수 정보가 있는지 확인해요
        if not data or 'email' not in data or 'password' not in data or 'nickname' not in data:
            return jsonify({"error": "이메일, 비밀번호, 닉네임은 필수입니다."}), 400  # 잘못된 요청 에러

        # Firebase Auth로 사용자 생성: 출입증 발급하기
        user = auth.create_user(
            email=data['email'],
            password=data['password']
        )

        # Firestore에 사용자 정보 저장: 도서관에 책 넣기
        db.collection('users').document(user.uid).set({
            'nickname': data['nickname'],  # 탐험가 이름
            'avatar': data.get('avatar', ''),  # 사진 URL, 없으면 빈 문자열
            'created_at': firestore.SERVER_TIMESTAMP  # 지금 시간 자동으로
        })

        # 성공 응답: "잘 됐어요!"라는 메시지와 사용자 ID를 돌려줘요
        return jsonify({"uid": user.uid, "message": "사용자 생성 성공"}), 201

    except auth.EmailAlreadyExistsError:
        # 이미 존재하는 이메일: 중복 에러
        return jsonify({"error": "이미 존재하는 이메일입니다."}), 409  # 충돌 에러
    except auth.InvalidPasswordError:
        # 비밀번호가 잘못됨: 인증 에러
        return jsonify({"error": "비밀번호는 6자 이상이어야 합니다."}), 401  # 인증 실패 에러
    except Exception as e:
        # 기타 에러: 서버에서 문제가 생겼을 때
        return jsonify({"error": f"서버 오류: {str(e)}"}), 500  # 서버 에러

# Flask 앱 실행: 사서 창구를 열고 대기하기
if __name__ == "__main__":
    app.run(debug=True)  # 디버그 모드로 실행 (에러 메시지를 자세히 보여줘요)
    
