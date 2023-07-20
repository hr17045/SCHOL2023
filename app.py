from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace 'your_secret_key_here' with a secret key

# Configure the database URI for user and task data
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
    __bind_key__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    department = db.Column(db.String(120), nullable=False)

@app.route("/")
def calendar():
    selected_department = request.args.get('department', 'all')

    if selected_department == 'all':
        tasks = Task.query.all()
    else:
        tasks = Task.query.filter_by(department=selected_department).all()

    events = []
    for task in tasks:
        event = {
            'title': task.title,
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
    department = request.form['department']

    new_task = Task(title=title, start_date=start_date, end_date=end_date, department=department)
    db.session.add(new_task)
    db.session.commit()

    return redirect('/')

# Route for user login and authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve user credentials from the submitted form data
        email = request.form['email']
        password = request.form['password']
        password_h = hashlib.sha256(password.encode('utf-8')).hexdigest()
        
        # Check if a user with the provided email and password exists in the 'user' database
        user = User.query.filter_by(email=email, password=password_h).first()

        if user:
            # Store the user ID in the session to manage the user's login state
            session['user_id'] = user.id
            return redirect('/')  # Redirect the user to the main calendar page after successful login
        else:
            return 'Invalid email or password'  # Display an error message for invalid credentials
    
    return render_template('login.html')  # Render the login page template for GET requests

# Route for user signup and adding a new user to the 'user' database
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Retrieve user details from the submitted form data
        email = request.form['email']
        password = request.form['password']
        department = request.form['department']
        password_h = hashlib.sha256(password.encode('utf-8')).hexdigest()

        # Create a new user instance with the provided details
        new_user = User(email=email, password=password_h, department=department)

        # Add the new user to the 'user' database and commit the changes
        db.session.add(new_user)
        db.session.commit()

        return redirect('/')  # Redirect the user to the main calendar page after successful signup

    return render_template('signup.html')  # Render the signup page template for GET requests

# Route for user logout and clearing the session data
@app.route('/logout')
def logout():
    # Clear the session data to log out the user
    session.pop('user_id', None)

    return redirect('/login')  # Redirect the user back to the login page

# Start the Flask application in debug mode if this script is run as the main module
if __name__ == "__main__":
    app.run(debug=True)
