from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
# client = MongoClient('mongodb://test:test@localhost', 27017)
db = client.dbsparta

from datetime import datetime

@app.route('/')
def home():
   return render_template('index.html')

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
		extension = file.filename.split('.')[-1] #.점을 기준으로 파일 확장자명을 가져온다.
		
		today = datetime.now()
		mytime = today.strftime('%Y-%m-%d-%H-%M-%S') #날짜시간을 가져옴
		filename = f'file-{mytime}' #날짜시간을 가져와서 파일명을 만들어준다.
		
		save_to = f'static/save_images/{filename}.{extension}' #경로와, 저장할이름을 만들어 변수에 할당
		file.save(save_to) #최종적으로 파일을 저장합니다.
		doc = {
				'id':today.strftime('%m%d%H%M%S'),
        'comment': comment_receive,
        'star': star_receive,
        'file': f'{filename}.{extension}', #위에서 만든 파일명 추가합니다.
        'time': today.strftime('%Y.%m.%d')
    }
		db.food.insert_one(doc) #DB에 저장합니다.
		return jsonify({'msg': '저장 완료!'})

if __name__ == '__main__':  
   app.run('0.0.0.0',port=5000,debug=True)