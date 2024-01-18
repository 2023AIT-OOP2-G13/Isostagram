import os
import time
import datetime
import csv
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from flask import Flask

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
        with open('static/csv_file/'+upload_time+'.csv', 'w') as f:
            writer = csv.writer(f)

        #画像ファイルのリネーム
        oldpath = filepath
        newpath = 'static/image_file/'+upload_time+'.jpg'
        os.rename(oldpath, newpath)
        
        
app = Flask(__name__)
def csv_comment_view():
    filename = 'static/csv_file/sample.csv'
    with open(filename) as f:
        csvreader = csv.reader(f)
        for row in csvreader:
            print(row)

if __name__ == "__main__":
    #監視するファイルの指定
    DIR_WATCH = 'static/image_file'
    # ファイルのパターンを指定（画像ファイルのみ）
    PATTERNS = ["*.jpg","*.png"] 

    event_handler = MyFileWatchHandler(patterns=PATTERNS)
    observer = Observer()
    observer.schedule(event_handler, DIR_WATCH, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
    csv_comment_view()
