from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__, static_url_path='/static')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Harvey/Desktop/SCHOL2023/instance/user.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Harvey/Desktop/SCHOL2023/instance/task.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(120), nullable=False)

class Task(db.Model):
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

if __name__ == "__main__":
    app.run(debug=True)
