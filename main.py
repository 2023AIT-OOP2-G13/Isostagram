# -*- coding: utf-8 -*-
from flask import Flask,request,render_template
import os
import glob
import csv


app = Flask(__name__)

#ディレクトリ指定
UPLOAD_FOLDER = 'static/image_file' 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#トップページのルティング
@app.route('/')
def top_page():
    #staticからファイルを取得
    files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*'))
    #uploaded_imagesにファイルを格納
    uploaded_images = [os.path.basename(file) for file in files]
    

    return render_template('top_page.html',uploaded_images = uploaded_images)



#アップロードページへのルーティング
@app.route('/upload')
def upload_page():
    
    return render_template('upload_page.html')


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

    return render_template('upload_page.html')
    


@app.route('/contents')
def contents_page():
    lines = []
    #with openしてcsvファイルを読み込む
    with open('static/csv_file/sample.csv',encoding='utf-8') as f:
        lines = f.readlines() #readlinesはリスト形式でcsvの内容を返す
    return render_template('contents_page.html',lines=lines)

@app.route('/result',methods=['POST'])
def result():
    #requestでarticleとnameの値を取得する
    article = request.form['article']
    name = request.form['name']
    #csvファイルに上書きモードで書き込む
    with open('static/csv_file/sample.csv','a',encoding='utf-8') as f:
        f.write(name + ',' + article + '\n')
    #result.htmlに返す
    return render_template('result.html')

if __name__ == '__main__':
    app.run(debug=False) 
