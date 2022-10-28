
from datetime import datetime, date, timedelta
from flask import Flask, jsonify,render_template,flash,redirect, template_rendered,url_for,session,logging,request
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from data import Mothers
from birthpredictionDays import predDays
from birthpredictionmodel import timePred
from functools import wraps

#instantiate Flask class 
app=Flask(__name__)

#configure database (MYSQL)
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='Dim)YxKK(ahtr2R'
app.config['MYSQL_DB']='iaca'
app.config['MYSQL_CURSORCLASS']='DictCursor'

#initialize mysql
mysql=MySQL(app)

#get mothers
Mothers=Mothers()


#create index page route
@app.route('/')
def index():
    return render_template('home.html')


    

#getting single mother
@app.route('/mother/<string:id>/')
def mother(id):
     #create cursor
    cur=mysql.connection.cursor()
    res=cur.execute("SELECT * FROM mothers WHERE id=%s",[id])
    mother=cur.fetchone()
    
    
    return render_template('mother.html',mother=mother)

class RegisterForm(Form):
    employeename=StringField('Name',[validators.Length(min=4,max=100)])
    hospital=StringField('Hospital',[validators.Length(min=4,max=100)])
    department=StringField('Department',[validators.Length(min=1,max=100)])
    position=StringField('Position',[validators.Length(min=3,max=100)])
    team=StringField('Team',[validators.Length(min=1,max=100)])
    phone_number=StringField('Phone Number',[validators.Length(min=9,max=10)])
    email=StringField('Email ',[validators.Length(min=12,max=100)])
    password=PasswordField(
        'Password',[
            validators.DataRequired(),
            validators.EqualTo('confirm',message='Passwords mismatched')
        ]
    )
    confirm=PasswordField('Confirm Password')


    
@app.route('/register',methods=['GET','POST'])
def registerOfficial():
    form=RegisterForm(request.form)
    if request.method=='POST' and form.validate():
        empname=form.employeename.data
        pemail=form.email.data
        pnum=form.phone_number.data
        hosp=form.hospital.data
        dept=form.department.data
        post=form.position.data
        tm=form.team.data
        fpass=sha256_crypt.encrypt(str(form.password.data))
        
        #create cursor
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO healthuser(ename, department, hospital, position, team, pnumber, email, upassword) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(empname,dept,hosp,post,tm,pnum,pemail,fpass))
        
        #commit to the Database the Script
        mysql.connection.commit()
        #close the connection
        cur.close()
        flash('Congratulations, you are now a member of staff.')
        
        
        return redirect(url_for('login'))
    return render_template('register.html',form=form)

#user login route page
@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method=='POST':
     uname=request.form['username']
     upass=request.form['password']
     hospital=request.form['hospital']
     #create cursor
     cur=mysql.connection.cursor()
     result=cur.execute("SELECT * FROM healthuser WHERE ename= %s",[uname])
     
     if result>0:
         data=cur.fetchone()
         dbpass=data['upassword']
         dbhospital=data['hospital']
         #compare passwords
         if sha256_crypt.verify(upass,dbpass):
             #pass in and create sessions
            session['logged_in']=True
            session['username']=uname
            session['hospital']=hospital
            
            flash('Welcome back to the platform','success')
            return redirect(url_for('dashboard'))
     else:
         error='Please try retyping your password.'
         return render_template('login.html',error=error)
     #close connection
     cur.close()
    else:
         error='Sorry, this user doesn\'t exist or nothing has been typed yet'
         return render_template('login.html',error=error)
         
  
    return render_template('login.html')
#check if user is logged_in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('You are supposed to be logged in','error')
            return redirect(url_for('login'))
    return wrap
#log out
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You have closed your space. Thank you for your time, come back soon','success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    #create cursor
    cur=mysql.connection.cursor()
    
    res=cur.execute("SELECT * FROM mothers")
    
    mothers=cur.fetchall()
    
    if res>0:
        return render_template('dashboard.html',mothers=mothers)
    else:
        msg='No mother was found in here'
        return render_template('dashboard.html',msg=msg)
    
    cur.close()
    
#get single mom



class RegisterFormPatients(Form):
    name=StringField('Name',[validators.Length(min=4,max=100)])
    address=StringField('Address',[validators.Length(min=4,max=150)])
    pregDate=StringField('Date (mm-dd-yyyy)',[validators.Length(min=10,max=10)])
    bpr=StringField('Blood Pressure',[validators.Length(min=6,max=8)])
    number=StringField('Phone Number',[validators.Length(min=9,max=9)])
    weight=StringField('Weight',[validators.Length(min=2,max=10)])
    bmi=StringField('BMI',[validators.Length(min=2,max=10)])
    

@app.route('/add',methods=['GET','POST'])
@is_logged_in
def addmom():
    form=RegisterFormPatients(request.form)
    if request.method=='POST' and form.validate():
        momName=form.name.data
        predDate=form.pregDate.data
        bmi=form.bmi.data
        bmi_int=float(bmi)
        wgt=form.weight.data
        wgt_int=float(wgt)
        bpr=form.bpr.data
        addr=form.address.data
        phone=form.number.data
        brttime=timePred(bmi_int,wgt_int)
        gestdays=predDays(bmi_int,wgt_int)
        
        #create date object
        predDt=datetime.strptime(predDate, '%m-%d-%Y')
        dur=timedelta(days=gestdays)
        finaldate=predDt+dur
     
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO mothers(motherName,pregDate,dys,bmi,mweight,bpr,addr,phone,birthTime,birthDate) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(momName,predDate,gestdays,bmi,wgt,bpr,addr,phone,brttime,finaldate))
        
        mysql.connection.commit()
        
        cur.close()
        
        flash(momName+' has been added to the database.','success')
        
        return redirect(url_for('dashboard'))
    return render_template('add.html',form=form)
    

#daily records page
@app.route('/daily')

@is_logged_in
def daily():
    #create cursor
    cur=mysql.connection.cursor()
    now = datetime.now()

    current_time = now.strftime("%m-%d-%Y")
    strval=str(current_time)
    
    res=cur.execute("SELECT * FROM mothers WHERE birthDate=%s",[strval])
    
    mothers=cur.fetchall()
    
    if res>0:
        return render_template('daily.html',mothers=mothers)
    else:
        msg='No mother was found in here'
        return render_template('daily.html',msg=msg)
    
    cur.close()

if __name__=='__main__':
    app.secret_key='keyD9090#'
    app.run(debug=True)
