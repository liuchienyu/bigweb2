from flask import Flask, render_template, redirect, url_for, render_template, request, session, g
from flask_login import login_required
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from flask_sqlalchemy import SQLAlchemy
import os
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import User
import pymongo
from pymongo import MongoClient


app = Flask(__name__)
app.secret_key = "#230dec61-fee8-4ef2-a791-36f9e680c9fc"
app.permanent_session_lifetime = timedelta(minutes=5)
UPLOAD_FOLDER = './static/images'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

db = SQLAlchemy()
#datebase
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
BASE_DIR=os.path.dirname(os.path.realpath(__file__))
connection_string = "sqlite:///"+os.path.join(BASE_DIR,'site.db')
engine=create_engine(connection_string,echo=True,connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)
db_session = Session()

users=db_session.query(User.username,User.id_name,User.id_sex,User.id_birth,User.id_phone,User.id_email,User.username,User.password).all()

#datebase2
CONNECTION_STRING ="mongodb+srv://dandy40605:1234@cluster0.qqbqe.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
client = MongoClient(CONNECTION_STRING,tls=True, tlsAllowInvalidCertificates=True,tz_aware=True )#tls=True, tlsAllowInvalidCertificates=True為解決無法連線問題


@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x[0] == session['user_id']][0]
        g.user = user

def login_required(a):
    @wraps(a)
    def wrap(*args,**kwargs):
        if not g.user:
            return redirect('/login')
        else:
            return a(*args,**kwargs)
            
    return wrap

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username_r = request.form['username']
        password_r = request.form['password']
        
        user1 = db_session.query(User.username).filter(User.username == username_r).first()
        user2 = db_session.query(User.password).filter(User.password == password_r ).first()
        if  user1 != None and user2 != None :
            session['user_id'] = username_r
            return redirect(url_for('home'))

        return redirect(url_for('login'))

    return render_template('login-a.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route("/")
@login_required
def homepage():
    return render_template("home.html")

@app.route("/home")
@login_required
def home():
    return render_template("home.html")

@app.route("/ClockIn")
@login_required
def ClockIn():
    return render_template("ClockIn.html")

@app.route("/go_to_work")
@login_required
def go_to_work():
    return render_template("alert_gtw.html")


@app.route("/finance")
@login_required
def finance():
    return render_template("finance.html")


@app.route("/Leave")
@login_required
def Leave():
    return render_template("Leave.html")


@app.route("/overtime")
@login_required
def overtime():
    return render_template("overtime.html")


@app.route("/paper_number")
@login_required
def paper_number():
    return render_template("paper_number.html")

@app.route("/papernumber_show")
@login_required
def papernumber_show():
    db = client.systemdata
    base_info = db.document_code_data
    code_results = base_info.find({'category':'文號申請'})
    code_results.sort("make_time",pymongo.DESCENDING)#按照時間降序排列
    code_results.limit(10)#限制數量
    return render_template("papernumber_show.html",code_results=code_results)

if __name__ == "__main__":
    app.run(debug=True)
