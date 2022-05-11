from pymongo import MongoClient
import certifi
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)

SECRET_KEY = 'SPARTA'

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.3rrj5.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login_page.html', msg=msg)


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인 버튼 클릭 시
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    # id중복확인
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/sign_up/save', methods=['POST'])
# 회원가입 서버
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/main')
def home():
    return render_template('main.html')


@app.route('/post_wirite')
def post_wirite():
    return render_template('post_wirite.html')


@app.route('/api/posts', methods=['GET'])
def show_posts():
    diaries = list(db.food.find({}, {'_id': False}))
    return jsonify({'all_food': diaries})


@app.route('/api/posts', methods=['POST'])
def save_posts():
    comment_receive = request.form['comment']
    star_receive = request.form['star']
    file = request.files["file"]
    extension = file.filename.split('.')[-1]  # .점을 기준으로 파일 확장자명을 가져온다.

    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')  # 날짜시간을 가져옴
    filename = f'file-{mytime}'  # 날짜시간을 가져와서 파일명을 만들어준다.

    save_to = f'static/save_images/{filename}.{extension}'  # 경로와, 저장할이름을 만들어 변수에 할당
    file.save(save_to)  # 최종적으로 파일을 저장합니다.
    doc = {
        'id': today.strftime('%m%d%H%M%S'),
        'comment': comment_receive,
        'star': star_receive,
        'file': f'{filename}.{extension}',  # 위에서 만든 파일명 추가합니다.
        'time': today.strftime('%Y.%m.%d')
    }
    db.food.insert_one(doc)  # DB에 저장합니다.
    return jsonify({'msg': '저장 완료!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)