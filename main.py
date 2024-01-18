from flask import Flask,request,render_template
import os
import glob
import csv
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from flask import Flask
import time
import datetime


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
    
    return render_template('upload.html')


#アップロードされた画像の保存とcsvファイルの作成
@app.route('/up',methods=['POST'])
def image_uplode():

    #.htmlから画像を取得
    file = request.files['upload_file']
    #image_fileに取得した画像を追加
    filename = os.path.join(app.config['UPLOAD_FOLDER'],file.filename)
    #保存
    file.save(filename)


    header = ['name', 'article']
    body = []

    #csvフィル作成
    with open('static/csv_file/sample.csv' ,'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(body)
        f.close()

    return render_template('upload.html')

@app.route('/contents')
def contents_page():
    lines = []
    #with openしてcsvファイルを読み込む
    with open('static/csv_file/20240118145159.csv',encoding='utf-8') as f:
        lines = f.readlines() #readlinesはリスト形式でcsvの内容を返す
        print(lines)
    return render_template('post.html',lines=lines)

@app.route('/result',methods=['POST'])
def result():
    #requestでarticleとnameの値を取得する
    article = request.form['article']
    name = request.form['name']
    #csvファイルに上書きモードで書き込む
    with open('static/csv_file/20240118145159.csv','a',encoding='utf-8') as f:
        f.write(name + ',' + article + '\n')
    #result.htmlに返す
    return render_template('result.html')

# if __name__ == '__main__':
#      app.run(debug=False) 
#DIR_WATCH内のファイルに何かあったときの処理
#現在はファイルが入ってきた時のみ。
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
