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
      "websitename":request.form.get('webname')
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
      msg['Subject']="Chatbot as a Service"
      msg['From']=senderemail
      msg['To']=recemail
      message=f"Dear {user['name']}, \n\nWelcome to Chatbot as a service. Chatbot as a service - Your affordable solution to round-the-clock customer support. This site is to provide a platform to efficiently scale your customer support with the help of our chatbot-as-a-service solution. By using chatbot-as-a-service, businesses can save time and resources while improving customer satisfaction and increasing their revenue. Whether it's providing product information, handling transactions, or resolving customer queries, chatbot-as-a-service can help businesses stay ahead of the curve in today's fast-paced digital world."
      msg.set_content(message)
      server=smtplib.SMTP_SSL('smtp.googlemail.com',465)
      server.login(senderemail,password)
      print("LOgin success")
      server.send_message(msg=msg)
      print("email has been sent to", recemail)
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