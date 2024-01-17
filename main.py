from flask import Flask
import csv

app = Flask(__name__)
def csv_comment_view():
    filename = 'static/csv_file/sample.csv'
    with open(filename) as f:
        csvreader = csv.reader(f)
        for row in csvreader:
            print(row)
    


    





if __name__ == '__main__':
    csv_comment_view()