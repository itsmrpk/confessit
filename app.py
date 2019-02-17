from flask import Response,Flask,render_template,redirect,logging,flash,session,url_for,request
from flask_sqlalchemy import SQLAlchemy
#from flask_mail import Mail
from datetime import datetime
from werkzeug import secure_filename
import os
import json
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://sql10279318:DlfMJcXbd3@sql10.freemysqlhosting.net/sql10279318' 
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/confessit'
db = SQLAlchemy(app)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = '.\\static'

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=False)
    image=db.Column(db.String(120), unique=False, nullable=False)
    messages=db.relationship('Messages', backref="owner")
    traits=db.relationship('Traits', backref="owner")

class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text_msg = db.Column(db.String(250), nullable=True)
    time =db.Column(db.String(12), nullable=True)
    status = db.Column(db.String(80), unique=False, nullable=False)
    user_id =db.Column(db.String(12),db.ForeignKey(Users.id),nullable=False)

class Traits(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    likeness = db.Column(db.Integer,nullable=True)
    honest = db.Column(db.Integer,nullable=True)
    intelligent = db.Column(db.Integer,nullable=True)
    beautiful = db.Column(db.Integer,nullable=True)
    user_id =db.Column(db.String(12),db.ForeignKey(Users.id),nullable=False)
    
@app.route('/')
def home():
    #length=Logs.query.filter_by(check_out=None).count()
    if 'email' in session:
        return redirect('/dashboard')
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/<string:username>',methods=['GET','POST'])
def anonymous(username):
    if request.method=='POST':
        user=Users.query.filter_by(username=username).first()
        message=Messages(text_msg=request.form.get('text_msg'),time=datetime.now(),status='unseen',owner=user)
        likeness=request.form.get('likeness')
        honest=request.form.get('honest')
        intelligent=request.form.get('intelligent')
        beautiful=request.form.get('beautiful')
        db.session.add(message)
        db.session.commit()
        trait=Traits(likeness=likeness,honest=honest,beautiful=beautiful,intelligent=intelligent,owner=user)
        db.session.add(trait)
        db.session.commit()
        return render_template('home.html',message="Submitted Successfully")
    user=Users.query.filter_by(username=username).first()
    if user==None:
        return "Wrong Link"
    return render_template('anonymous.html',user=user)

@app.route('/register',methods = ['GET', 'POST'])
def register():
    if(request.method=='POST'):
        #push data in data base
        name = request.form.get('name')
        email = request.form.get('email')
        username= request.form.get('username')
        password = request.form.get('password')
        user=Users.query.filter_by(email=email).first()
        if user!=None:
            return render_template('register.html',success="Email already exists")
        user=Users.query.filter_by(username=username).first()
        if user!=None:
            return render_template('register.html',success="Username already exists")
        f= request.files['image']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename) ))
        entry = Users(name=name, email = email,username=username,password=password ,image=secure_filename(f.filename))
        db.session.add(entry)
        db.session.commit()
        return render_template('login.html',success="OK")
    return render_template('register.html')
@app.route('/login',methods =['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user=Users.query.filter_by(email=email).first()
        if user==None:
            return render_template('login.html',message="No User Found")
        if user.password==password:
            session['email'] = email
            return redirect('/dashboard')
            return render_template('login.html',message="SUCCESS")
        else:
            return render_template('login.html',message="Wrong Password")
    return render_template('login.html')

@app.route('/dashboard',methods =['GET'])
def dashboard():
    if 'email' in session:
        user=Users.query.filter_by(email=session['email']).first()
        message=Messages.query.filter_by(owner=user).order_by(Messages.time.desc())
        return render_template('dashboard.html',user=user,messages=message)
    else:
        return redirect('/login')

@app.route('/message/<string:id>')
def message(id):
    if 'email' in session:
        message=Messages.query.filter_by(id=int(id)).first()
        message.status='seen'
        db.session.commit()
        return render_template('message.html',message=message)
    else:
        return redirect('/login') 

@app.route('/profile')
def profile():
    if 'email' in session:
        user=Users.query.filter_by(email=session['email']).first()
        #message=Messages.query.filter_by(owner=user)
        #trait=Traits.query.filter_by(owner=user)
        c=Traits.query.filter_by(owner=user).count()
        trt={}
        if c>=1:
            trt['likeness']= db.session.query(db.func.sum(Traits.likeness)).scalar()//c
            trt['honest']= db.session.query(db.func.sum(Traits.honest)).scalar()//c
            trt['beautiful']= db.session.query(db.func.sum(Traits.beautiful)).scalar()//c
            trt['intelligent']= db.session.query(db.func.sum(Traits.intelligent)).scalar()//c
        else:
            trt['likeness']=0
            trt['honest']=0
            trt['beautiful']=0
            trt['intelligent']=0
        return render_template('profile.html',user=user,trt=trt,c=c)
    else:
        return redirect('/login') 


@app.route("/logout")
def logout():
    session.pop('email')
    return redirect('/')
if __name__=='__main__':
    app.run(debug=True)
