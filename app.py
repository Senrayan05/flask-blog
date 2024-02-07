from flask import Flask , render_template , request, session ,jsonify, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import math
import json
import os
from werkzeug.utils import secure_filename
#from flask_mail import Mail
from flask_migrate import Migrate
from sqlalchemy import DateTime
from PIL import Image
from flask import current_app
import traceback
from datetime import datetime, timezone

import logging
from flask import session, redirect, request


import os

# mysql_host = os.environ.get('MYSQL_HOST', 'localhost')
mysql_host = os.environ.get('MYSQL_HOST', 'localhost')
mysql_port = os.environ.get('MYSQL_PORT', '3306')
mysql_user = os.environ.get('MYSQL_ROOT_USER', 'senrayan')
mysql_password = os.environ.get('MYSQL_ROOT_PASSWORD', 'Pa$$w0rd')
mysql_db = 'react'




with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True

app = Flask(__name__)
app.secret_key = 'Karthiksenrayan'

def authenticate(token):
    # Perform authentication logic here
    # Validate the token against your database or authentication system
    if token == 'your_secret_token':
        return True
    return False



# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://senrayan:Pa$$w0rd@localhost/react'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}'




app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Set to False to suppress a SQLAlchemy warning
db = SQLAlchemy(app)




# app.config['UPLOAD_FOLDER'] = params.get('upload_location', 'C:\Users\Dell\Desktop\Blog Web Application\static\img')
app.config['UPLOAD_FOLDER'] = 'static/img'




class Contacts(db.Model):  #Write the table name as class name and the first letter in capital

   #1
    sno = db.Column(db.Integer, primary_key=True)
   #2
    name = db.Column(db.String(80), nullable=False)
   #3
    email = db.Column(db.String(90), nullable=False)
   #4
    ph_no = db.Column(db.String(15), nullable=False)
   #5
    msg = db.Column(db.String(500), nullable=False)
   #6 
    date = db.Column(db.String(12), nullable=True)



class Posts(db.Model):  #Write the table name as class name and the first letter in capital

   #1
    sno = db.Column(db.Integer, primary_key=True)
   #2
    title = db.Column(db.String(80), nullable=False)
   #3
    slug = db.Column(db.String(25), nullable=False)
   #3
    subtitle = db.Column(db.String(90), nullable=False)
   #4
    content = db.Column(db.String(120), nullable=False)
   #5
    img_file = db.Column(db.String(40), nullable=True)
   #6 
    date = db.Column(db.String(12), nullable=True)

@app.route("/")
def home():
     posts = Posts.query.order_by(Posts.sno).all()
     #[0:params['no_of_posts']]
     last=math.ceil(len(posts)/int(params['no_of_posts']))
 
     page=request.args.get('page')
     if(not str(page).isnumeric()):
         page=1
     page=int(page)    
     
     posts = posts[(page-1)*int(params['no_of_posts']): (page-1)*int(params['no_of_posts'])+int(params['no_of_posts']) ]
     #slicing of posts i.e from say x to y -- to here is :

     if(page==1):
         prev = "#"
         next = "/?page="+ str(page+1)
     elif(page==last):
         prev = "/?page="+ str(page-1)
         next = "#"
     else:
         prev = "/?page="+ str(page-1)
         next = "/?page="+ str(page+1)

     return render_template('index.html',params=params,posts=posts,prev=prev,next=next)

@app.route("/about")
def about():
     return render_template('about.html',params=params)

@app.route("/logout")
def logout():
    session.pop('user')
    return render_template('login.html',params=params)

@app.route("/delete/<string:sno>", methods=['GET','POST'])
def delete(sno):
     if('user' in session and session['user']==params['admin_user']):
            post = Posts.query.filter_by(sno=sno).first()
            db.session.delete(post)
            db.session.commit()
     return redirect('/admin')
     


@app.route("/admin")
def admin():
     return render_template('admin.html',params=params)

@app.route("/login", methods=['GET', 'POST'])

def login():
    if 'user' in session and session['user'] == params['admin_user']:
        posts = Posts.query.all()
        return render_template('admin.html', params=params, posts=posts)

    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')

        if username == params['admin_user'] and userpass == params['admin_password']:
            session['user'] = username
            posts = Posts.query.all()
            return render_template('admin.html', params=params, posts=posts)




@app.route("/uploader", methods=['GET', 'POST'])
def uploader():
    if request.method == 'GET':
        return render_template('upload.html', params=params)

    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            if 'file1' not in request.files:
                flash('No file part')
                return redirect(request.url)
            f = request.files['file1']
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],  filename))
            

            
            # Store the filename in the database
            new_post = Posts(
                title=request.form.get('title'),
                slug=request.form.get('Slug'),
                subtitle=request.form.get('subt'),
                content=request.form.get('Content'),
                img_file=filename,  # Save the filename in the img_file column
                date=datetime.now(timezone.utc)
                
            )

            db.session.add(new_post)
            db.session.commit()

            return "Uploaded file successfully"
    return "Unauthorized", 401


@app.route("/contact", methods = ['GET','POST'])
def contact():
     if(request.method=='POST'):
          #ENTRIES
         __table__='contacts'
         name = request.form.get('name')
         email = request.form.get('email')
         ph = request.form.get('ph')
         msg_in = request.form.get('msg')
         
         entry = Contacts(name = name, email = email, ph_no = ph, msg = msg_in, date= datetime.now())

         db.session.add(entry)
         db.session.commit()
         '''mail.send_message('New message from ' + name,
                          sender=email,
                          recipients = [params['gmail-user']],
                          body = msg_in + "\n" + ph
                          )'''

     return render_template('contact.html',params=params)

@app.route("/post/<string:post_slug>", methods=['GET'])
                                                  
def post_f(post_slug):                           
    post=Posts.query.filter_by(slug=post_slug).first()
    if post is None:
        # Handle the case where no post is found
        return render_template('post_not_found.html'), 404  
    return render_template('post.html', params=params, post=post)

# ... (previous code)

@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    # Check if the user is logged in as admin
    if 'user' in session and session['user'] == params['admin_user']:
        post = Posts.query.filter_by(sno=sno).first_or_404() if sno != '0' else None

        # Check if the request method is POST
        if request.method == 'POST':
            # Get the form data
            new_title = request.form.get('title')
            new_slug = request.form.get('Slug')
            new_subtitle = request.form.get('subt')
            new_content = request.form.get('Content')
            new_image = request.files['img_file'] if 'img_file' in request.files else None
            new_date = datetime.now(timezone.utc)
            
        if 'img_file' in request.files:
            image = request.files['img_file']
            if image.filename != '':
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                img_file = filename
            else:
                    img_file = post.img_file if post else None    
                

            # Check if it's a new post or an existing post
            if sno == '0':
                # Create a new post
                img_file = secure_filename(new_image.filename) if new_image else 'default_image.jpg'
                post = Posts(
                    title=new_title,
                    slug=new_slug,
                    subtitle=new_subtitle,
                    content=new_content,
                    img_file=img_file,
                    date=new_date
                )
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = new_title
                post.slug = new_slug
                post.subtitle = new_subtitle
                post.content = new_content

                # Set img_file to the filename if new_image is provided, otherwise keep the existing img_file
                if new_image:
                    post.img_file = secure_filename(new_image.filename)
                    
                post.date = new_date
                db.session.commit()

            # Redirect to the edited post
            return redirect('/edit/' + sno)

        # If the request method is GET, retrieve the post details and render the edit page
        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post, sno=sno)

    # If the user is not logged in as admin, redirect to the login page
    return redirect('/login')



if __name__ == "__main__":
    
    try:
        
        app.run(debug=True)
    except Exception as e:
        print("An error occurred:", str(e))
        traceback.print_exc()