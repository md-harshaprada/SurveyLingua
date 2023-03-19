from flask import Flask, render_template, session, redirect, request
from functools import wraps
import pymongo
import base64

app = Flask(__name__)
app.secret_key = b'\xcc^\x91\xea\x17-\xd0W\x03\xa7\xf8J0\xac8\xc5'

# Database
client = pymongo.MongoClient("mongodb+srv://mdharshaprada:MongoDB@cluster0.0hfnquj.mongodb.net/test")
db = client.get_database('surveyLingua')
collection = db["Responses"]
print(db)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/')
    return wrap

# Routes
from user import routes

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/dashboard/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/stats/')
def stats():
    cursor = collection.find()

    # concatenate the values of the column into a string
    column_data = ""
    for row in cursor:
        column_data += row["customer_experience_text"]
        column_data += " "
    
    # count the number of rows returned by the cursor
    num_rows = collection.count_documents({})
    print(num_rows)
    
    # pass the concatenated string and number of rows to the HTML template
    return render_template('stats.html', column_data=column_data, num_rows=num_rows)

@app.route('/resp/')
def resp():
    results = collection.find()    
    return render_template('stats1.html', results=results)
@app.route('/bar/')
def bar():
    results = collection.find()
    arr=[0,0,0,0,0]
    for row in results:
      if(row['culture_value_rating']==1):
        arr[0]+=1
      elif(row['culture_value_rating']==2):
        arr[1]+=1
      elif (row['culture_value_rating']==3):
        arr[2]+=1
      elif (row['culture_value_rating']==4):
        arr[3]+=1
      elif (row['culture_value_rating']==5):
        arr[4]+=1
    return render_template('bar.html', arr=arr)

if __name__ == "__main__":
    app.run(debug=True)
