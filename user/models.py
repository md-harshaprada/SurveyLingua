from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
from app import db
import uuid
import smtplib
from email.message import EmailMessage

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