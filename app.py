from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import calendar
from datetime import datetime
import hashlib

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Harvey/Desktop/SCHOL2023/instance/user.db'
app.config['SQLALCHEMY_BINDS'] = {
    'task': 'sqlite:///C:/Users/Harvey/Desktop/SCHOL2023/instance/task.db'
}
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(120), nullable=False)

class Task(db.Model):
    __bind_key__ = 'task'  # Specify the database binding
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)






@app.route("/")
def calendar():
    tasks = Task.query.all()
    events = []
    for task in tasks:
        event = {
            'title': task.title,  # Include the task title in the event object
            'start': task.start_date.strftime('%Y-%m-%d'),
            'end': task.end_date.strftime('%Y-%m-%d')
        }
        events.append(event)
    return render_template('calendar.html', events=events)

@app.route('/add_task', methods=['POST'])
def add_task():
    title = request.form['title']
    start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
    new_task = Task(title=title, start_date=start_date, end_date=end_date)
    db.session.add(new_task)
    db.session.commit()
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        #hashing passwords
        password_h = hashlib.sha256(password.encode('utf-8')).hexdigest()
        
        # Query the database for the submitted username and password
        user = User.query.filter_by(email=email, password=password_h).first()

        if user:
            return redirect('/')
        else:
            return 'Invalid email or password'
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        department = request.form['department']
       #hashing passwords
        password_h = hashlib.sha256(password.encode('utf-8')).hexdigest()

        # Create a new user object and add it to the database
        new_user = User(email=email, password=password_h, department=department)
        db.session.add(new_user)
        db.session.commit()

        # Display a success message
        return redirect('/') 

    return render_template('signup.html')

if __name__ == "__main__":
    app.run(debug=True)