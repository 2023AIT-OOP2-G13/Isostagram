from flask import Flask,request,render_template, jsonify
import os
import glob
import csv
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import time
import datetime

iine_rank = []
day_rank = []

app = Flask(__name__)

#ディレクトリ指定
UPLOAD_FOLDER = 'static/image_file' 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#トップページのルティング
@app.route('/')
def top_page():
    # #staticからファイルを取得
    # files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*'))
    # #uploaded_imagesにファイルを格納
    # uploaded_images = [os.path.basename(file) for file in files]

    image_data = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.endswith(('.jpg', '.png', '.jpeg','.JPG')):
            name = filename.split('.')[0]  # 拡張子を除いたファイル名を取得
            image_data.append({'name': name, 'filename': filename})
    print(image_data)

    return render_template('top_page.html',image_data = image_data)



#アップロードページへのルーティング
@app.route('/upload')
def upload_page():
    
    return render_template('upload.html',initial_count=count_manager.initial_count)


#アップロードされた画像の保存とcsvファイルの作成
@app.route('/up',methods=['POST'])
def image_uplode():

    #.htmlから画像を取得
    file = request.files['upload_file']
    if not file :
        errormessage = ('画像が添付されていません')
        return render_template('upload.html')

    #image_fileに取得した画像を追加
    filename = os.path.join(app.config['UPLOAD_FOLDER'],file.filename)
    #保存
    file.save(filename)


    #アップロード時のコメント保存
    text = request.form.get('text_input', None)
    header = ['ユーザー名', '投稿内容','0']
    if text != None :
        header.append(text)
    else :
        header.append("")

    #csvフィル作成
    with open('static/csv_file/sample.csv' ,'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        f.close()

    

    return render_template('upload.html')

@app.route('/get_image_name/<image_name>')
def contents_page(image_name):
    lines = []
    image=image_name+'.jpg'
    file_path = 'static/csv_file/'+image_name+'.csv'
    #with openしてcsvファイルを読み込む
    with open('static/csv_file/'+image_name+'.csv',encoding='utf-8') as f:
        lines = f.readlines() #readlinesはリスト形式でcsvの内容を返す

    count_manager.read_initial_count_from_csv(file_path)
    return render_template('post.html',lines=lines ,image_name=image_name,image=image)


@app.route('/result',methods=['POST'])
def result():
    #requestでarticleとnameの値を取得する
    article = request.form['article']
    name = request.form['name']
    image_name=request.form['image_name']
    upload_time = datetime.datetime.now().strftime('%Y %m/%d %H:%M:%S')
    #csvファイルに上書きモードで書き込む
    with open('static/csv_file/'+image_name+'.csv','a',encoding='utf-8') as f:
#     with open('static/csv_file/sample.csv','a',encoding='utf-8') as f:
        f.write(name + ',' + article + ','+upload_time+'\n')
    #result.htmlに返す
    return render_template('result.html',image_name=image_name)

@app.route('/get_image_name/<image_name>')
def get_image_name(image_name):

    return render_template('result.html')

class MyFileWatchHandler(PatternMatchingEventHandler):
    def on_created(self, event):
        filepath = event.src_path
        filename = os.path.basename(filepath)
        #ターミナルに表示されるログ
        print(f"{datetime.datetime.now()} {filename} created")
        #YYYYMMDDhhmmssにしてupload_timeに保存
        upload_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        #csvファイルの保存
        # with open('static/csv_file/'+upload_time+'.csv', 'w') as f:
        #     writer = csv.writer(f)
        #csvファイルのリネーム
        oldpath = 'static/csv_file/sample.csv'
        newpath = 'static/csv_file/'+upload_time+'.csv'
        os.rename(oldpath, newpath)
        #画像ファイルのリネーム
        oldpath = filepath
        newpath = 'static/image_file/'+upload_time+'.jpg'
        os.rename(oldpath, newpath)

class CountManager:
    def __init__(self):
        self.initial_count = 0
        self.file_path = None

    def read_initial_count_from_csv(self, file_path):
        self.file_path = file_path
        try:
            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                # CSVファイルからカウンターの初期値を読み取る
                for row in reader:
                    self.initial_count = int(row[2])
                    print(self.initial_count)
                    break  # 最初の行だけ読み取る
        except FileNotFoundError:
            # ファイルが見つからない場合などのエラー処理
            print("CSV file not found.")

    def update_count(self, new_count):
        self.initial_count = new_count
        if self.file_path is None:
            print("File path is not set.")
            return jsonify(success=False, error="File path is not set.")

        #print(self.file_path)
        try:
            # CSVファイルを読み取りモードで開く
            with open(self.file_path, 'r', newline='') as file:
                reader = csv.reader(file)
                data = list(reader)  # CSVの内容をリストとして取得
                new_count += int(data[0][2])
                data[0][2] = new_count

            # 変更したデータをCSVファイルに書き込み
            with open(self.file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(data)

            return jsonify(success=True)
        except FileNotFoundError:
            print("CSV file not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

# CountManagerのインスタンスを作成
count_manager = CountManager()

@app.route('/update_count', methods=['POST'])
def update_count():
    data = request.get_json()
    new_count = data.get('count', 0)

    # カウントを更新
    count_manager.update_count(new_count)

    return jsonify(success=True)


def csv_comment_view():
    filename = 'static/csv_file/sample.csv'
    with open(filename) as f:
        csvreader = csv.reader(f)
        for row in csvreader:
            print(row)   
#app = Flask(__name__)
# def csv_comment_view():
#     filename = 'static/csv_file/sample.csv'
#     with open(filename) as f:
#         csvreader = csv.reader(f)
#         for row in csvreader:
#             print(row)

if __name__ == "__main__":
    #監視するファイルの指定
    DIR_WATCH = 'static/image_file'
    # ファイルのパターンを指定（画像ファイルのみ）
    PATTERNS = ["*.jpg","*.png"] 

    event_handler = MyFileWatchHandler(patterns=PATTERNS)
    observer = Observer()
    observer.schedule(event_handler, DIR_WATCH, recursive=True)
    observer.start()
    app.run(debug=False)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

    #csv_comment_view()
