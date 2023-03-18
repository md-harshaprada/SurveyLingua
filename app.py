#from flask_ngrok import run_with_ngrok #for vm local hos
from flask import Flask, render_template, session, redirect, request,jsonify
from functools import wraps
import pymongo
from passlib.hash import pbkdf2_sha256
import uuid
from email.message import EmailMessage
from bson.binary import Binary
import openai
import os
import whisper
import smtplib
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
# model=whisper.load_model('large')

app = Flask(__name__)
app.secret_key = b'\xcc^\x91\xea\x17-\xd0W\x03\xa7\xf8J0\xac8\xc5'
#run_with_ngrok(app)
tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

client=pymongo.MongoClient("mongodb+srv://mdharshaprada:MongoDB@cluster0.0hfnquj.mongodb.net/test")
db=client.get_database('surveyLingua')
collection = db["Register"]
print(db)
API_KEY = "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"
openai.api_key=("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")
model_id = 'whisper-1'

def login_required(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs)
    else:
      return redirect('/')
  
  return wrap

@app.route("/")    
def home():
    return render_template("index.html")  

@app.route("/about")
def about():
    return render_template("aboutus.html")
@app.route('/upload', methods=['POST'])
def upload():
    text_input = request.form['name']
    rating = request.form['gender']
    e = request.form['email']
    performance = request.form['performance']
    ratings = request.form['ratings']
    satisfaction = request.form['satisfaction']
    tokens = tokenizer.encode(satisfaction, return_tensors='pt')
    result = model(tokens)
    model_rating=int(torch.argmax(result.logits))+1
    print(model_rating)
    print(text_input)
    print(e, satisfaction, ratings, performance, sep=' ')
    file_bytes = []
    text_audios = []
    audio_files=[]
    for i in range(1, 3):
        file = request.files.get('audio' + str(i))
        if file:
            filename = text_input + str(i) + '.webm'
            file.save(filename)
            audio_files.append(file)
            with open(filename, 'rb') as f:
                 file_bytes.append(f.read())
            media_file_path=filename
            media_file = open(media_file_path, 'rb')
            # text_audios.append(model.transcribe(filename, fp16=False, task='translate')["text"])
            response = openai.Audio.translate(api_key=API_KEY,model=model_id,file=media_file,prompt='')
            text_audios.append(response['text'])
            # text_audios.append(model.transcribe(filename, fp16=False, task='translate')["text"])
            print(response['text'])
    db.Responses.insert_one({
        "name": text_input,
        "gender": rating,
        "email": e,
        "ratings": ratings,
        "performance": performance,
        "satisfaction": satisfaction,
        "customer_experience_audio": Binary(file_bytes[0]),
        "customer_experience_text":text_audios[0],
        "overall_feedback_audio":Binary(file_bytes[1]),
        "overall_feedback_text":text_audios[1],
        "culture_value_rating":model_rating
    }) 
    return 'Upload successful'


@app.route("/register")
def register():
    return render_template("register.html")

@app.route('/dashboard/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route("/admin/")
def admin():
    return render_template("admin.html")


class User:

  def start_session(self, user):
    del user['password']
    session['logged_in'] = True
    session['user'] = user
    return jsonify(user), 200

  def signup(self):
    print(request.form)

    # Create the user object
    user = {
      "_id": uuid.uuid4().hex,
      "name": request.form.get('name'),
      "email": request.form.get('email'),
      "password": request.form.get('password'),
    }

    # Encrypt the password
    user['password'] = pbkdf2_sha256.encrypt(user['password'])

    # Check for existing email address
    if db.Register.find_one({ "email": user['email'] }):
      return jsonify({ "error": "Email address already in use" }), 400

    if db.Register.insert_one(user):
      senderemail="menthealthnd@gmail.com"
      recemail=user["email"]
      password='fjazggpptivmfvll'
      msg=EmailMessage()
      msg['Subject']="Survey Lingua"
      msg['From']=senderemail
      msg['To']=recemail
      message=f"Dear {user['name']}, \n\nWelcome to Survey Lingua. Survey Lingua is a platform designed to help businesses and organizations create multilingual surveys to collect feedback from a diverse group of respondents. The platform provides a user-friendly interface that allows users to easily create and customize surveys in multiple languages."
      msg.set_content(message)
      server=smtplib.SMTP_SSL('smtp.googlemail.com',465)
      server.login(senderemail,password)
      print("Login success")
      server.send_message(msg=msg)
      print("Email has been sent to", recemail)
      return self.start_session(user)

    return jsonify({ "error": "Signup failed" }), 400
  
  def signout(self):
    session.clear()
    return redirect('/')
  
  def login(self):

    user = db.Register.find_one({
      "email": request.form.get('email')
    })

    if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
      return self.start_session(user)
    
    return jsonify({ "error": "Invalid login credentials" }), 401

@app.route('/user/signup', methods=['POST'])
def signup():
  return User().signup()

@app.route('/user/signout')
def signout():
  return User().signout()

@app.route('/user/login', methods=['POST'])
def login():
  return User().login()

app.run()