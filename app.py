from flask import Flask, render_template, request , session, redirect, url_for, jsonify, send_file
from flask import flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import session
from flask_mail import Mail, Message
from sqlalchemy.exc import IntegrityError
import socket
import json
import os
from flask_mysqldb import MySQL
import secrets
import os
from random import randint
import random
import pymysql
pymysql.install_as_MySQLdb()


local_server = os.environ.get('IS_PRODUCTION') != '1'

                         
socket.getaddrinfo('localhost', 8080)

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
)

mail = Mail(app)
local_server = True

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

local_server = False

db = SQLAlchemy(app)

class Contacts(db.Model):
    '''
      sno, name phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=True)
    date = db.Column(db.String(), nullable=True)
    email = db.Column(db.String(50), nullable=True)
    umail = db.Column(db.String(50), nullable=True)

class Projects(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    pro_link = db.Column(db.String(300), nullable=False)
    date = db.Column(db.String(), nullable=True)
    img_file = db.Column(db.String(50), nullable=True)


class Expes(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    join_date = db.Column(db.String, nullable=False)
    title = db.Column(db.String(30), nullable=False)
    company_name = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(240), nullable=False)
    com_add = db.Column(db.String(30), nullable=False)
    res_date = db.Column(db.String(), nullable=True)
    post_date = db.Column(db.String(), nullable=True)

class Edcs(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    cor_duration = db.Column(db.String(20), nullable=False)
    clg_name = db.Column(db.String(50), nullable=False)
    clg_add = db.Column(db.String(50), nullable=False)
    cor_name = db.Column(db.String(25), nullable=False)
    cor_work = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(120), nullable=True)
    post_date = db.Column(db.String(), nullable=True)


@app.route('/',methods=['GET','POST'])
def home():
    expe = Expes.query.all()
    edc = Edcs.query.all()
    return render_template('index.html', params=params, expes=expe, edcs=edc)

@app.route('/resume', methods=['GET'])
def resume_route():
    expe = Expes.query.all()
    edc = Edcs.query.all()
    return render_template('resume.html', params=params, expes=expe, edcs=edc)

@app.route('/project', methods=['GET'])
def project_route():
    project = Projects.query.all()
    return render_template('project.html', params=params, projects=project)

@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get("name")
        message = request.form.get("message")
        email = request.form.get("email")
        phone = request.form.get("phone")
        umail = session.get("umail")

        entry = Contacts(name=name, msg=message, phone_num=phone, email=email,  umail=umail, date=datetime.now())

        flash("Your form submitted successfully.", "succsess")
        #email html page
        rendered_body= render_template('email.html', params=params)
        mail.send_message(subject="New message from " + name,
                          sender=email,  # Changed to a string
                          recipients=[params['gmail-user']],  # Ensure this is a list
                          body=message +"\n" + phone +"\n"+ "user login mail:-"+umail
                          )
        mail.send_message(subject="JIGNESH SATHAVARA",
                          sender=params['gmail-user'],
                          recipients = [email],
                          html=rendered_body
                          )
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html', params=params)

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if "admin" in session and session['admin']==params['admin_user']:
        project = Projects.query.all()
        expe = Expes.query.all()
        edc = Edcs.query.all()
        return render_template("dashboard.html", params=params, projects=project, expes=expe, edcs=edc)

    if request.method=="POST":
        username = request.form.get("uname")
        userpass = request.form.get("upass")
        if username==params['admin_user'] and userpass==params['admin_password']:
            # set the session variable
            session['admin']=username
            project = Projects. query.all()
            expe = Expes.query.all()
            edc = Edcs.query.all()
            return render_template("dashboard.html", params=params, projects=project, expes=expe, edcs=edc)
    else:
        flash("check email, password and try again. ","danger")
        return render_template("login1.html", params=params)
    
    return render_template("login1.html", params=params)

@app.route('/edit/<string:sno>', methods=['GET','POST'])
def edit(sno):
    if "admin" in session and session['admin']==params['admin_user']:
        if request.method=='POST':
            box_title = request.form.get('title')
            content = request.form.get('content')
            pro_link = request.form.get('pro_link')
            img_file = request.form.get('img_file')
            date=datetime.now()
            
            if sno == '0':
                project=Projects(title=box_title, content=content, pro_link=pro_link, img_file=img_file, date=date)
                db.session.add(project)
                db.session.commit()
            else:
                project=Projects.query.filter_by(sno=sno).first()
                project.title = box_title
                project.content = content
                project.pro_link = pro_link
                project.img_file = img_file
                project.date = date
                db.session.commit()
                return redirect('/edit/'+sno)
            
        project=Projects.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, project=project, sno=sno)


@app.route('/editexp/<string:sno>', methods=['GET','POST'])
def editexp(sno):
    if "admin" in session and session['admin']==params['admin_user']:
        if request.method=='POST':
            join_date = request.form.get('join_date')
            title = request.form.get('title')
            company_name = request.form.get('company_name')
            content = request.form.get('content')
            com_add = request.form.get('com_add')
            res_date = request.form.get('res_date')
            post_date=datetime.now()
            
            if sno == '0':
                expe=Expes(join_date=join_date, title=title, company_name=company_name, content=content, com_add=com_add, res_date=res_date, post_date=post_date)
                db.session.add(expe)
                db.session.commit()
            else:
                expe=Expes.query.filter_by(sno=sno).first()
                expe.join_date = join_date
                expe.title = title
                expe.company_name = company_name
                expe.content = content
                expe.com_add = com_add
                expe.res_date = res_date
                expe.post_date = post_date
                db.session.commit()
                return redirect('/editexp/'+sno)
            
        expe=Expes.query.filter_by(sno=sno).first()
        return render_template('editexp.html', params=params, expe=expe, sno=sno)


@app.route('/edc/<string:sno>', methods=['GET','POST'])
def edc(sno):
    if "admin" in session and session['admin']==params['admin_user']:
        if request.method=='POST':
            cor_duration = request.form.get('cor_duration')
            clg_name = request.form.get('clg_name')
            clg_add = request.form.get('clg_add')
            cor_name = request.form.get('cor_name')
            cor_work = request.form.get('cor_work')
            content = request.form.get('content')
            post_date=datetime.now()
            
            if sno == '0':
                edc=Edcs(cor_duration=cor_duration, clg_name=clg_name, clg_add=clg_add, cor_name=cor_name, cor_work=cor_work, content=content, post_date=post_date)
                db.session.add(edc)
                db.session.commit()
            else:
                edc=Edcs.query.filter_by(sno=sno).first()
                edc.cor_duration = cor_duration
                edc.clg_name = clg_name
                edc.clg_add = clg_add
                edc.cor_name = cor_name
                edc.cor_work = cor_work
                edc.content = content
                post_date = datetime.now()
                db.session.commit()
                return redirect('/edc/'+sno)

        edc=Edcs.query.filter_by(sno=sno).first()
        return render_template('edc.html', params=params, edc=edc, sno=sno)

@app.route("/deletepr/<string:sno>" , methods=['GET', 'POST'])
def deletepr(sno):
    if "admin" in session and session['admin']==params['admin_user']:
        project = Projects.query.filter_by(sno=sno).first()
        db.session.delete(project)
        db.session.commit()
    return redirect("/dashboard")

@app.route("/deleteex/<string:sno>" , methods=['GET', 'POST'])
def deleteex(sno):
    if "admin" in session and session['admin']==params['admin_user']:
        expe = Expes.query.filter_by(sno=sno).first()
        db.session.delete(expe)
        db.session.commit()
    return redirect("/dashboard")

@app.route("/deleteed/<string:sno>" , methods=['GET', 'POST'])
def deleteed(sno):
    if "admin" in session and session['admin']==params['admin_user']:
        edc = Edcs.query.filter_by(sno=sno).first()
        db.session.delete(edc)
        db.session.commit()
    return redirect("/dashboard")

@app.route("/customer")
def customer():
    contact = Contacts.query.all()
    return render_template('customer.html', params=params, contacts=contact)

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.pop('admin')
    return redirect("/dashboard")

if __name__ == '__main__':
    app.run(debug=True)
