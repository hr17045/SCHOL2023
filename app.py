# Import necessary modules
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib
from datetime import timedelta

# Create a Flask web application
app = Flask(__name__, static_url_path='/static')

# Set the secret key for session management 
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Configure the database URIs for user and task data
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Harvey/Desktop/SCHOL2023/instance/user.db'
app.config['SQLALCHEMY_BINDS'] = {
    'task': 'sqlite:///C:/Users/Harvey/Desktop/SCHOL2023/instance/task.db'
}

# Initialize the database
db = SQLAlchemy(app)

# Define the User table in the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(120), nullable=False)

# Define the Task table in the 'task' database
class Task(db.Model):
    __bind_key__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    department = db.Column(db.String(120), nullable=False)

# Route for the main calendar page
@app.route("/")
def calendar():
    # Get the selected department from the request arguments (default to 'all')
    selected_department = request.args.get('department', 'all')

    # Fetch tasks based on the selected department
    if selected_department == 'all':
        tasks = Task.query.all()
    else:
        tasks = Task.query.filter_by(department=selected_department).all()

    # Prepare the events to display on the calendar
    events = []
    for task in tasks:
        event = {
            'title': task.title,
            'start': task.start_date.strftime('%Y-%m-%d'),
            'end': task.end_date.strftime('%Y-%m-%d'),
            'id': task.id,
            'department': task.department
        }
        events.append(event)

    # Render the calendar template with the events
    return render_template('calendar.html', events=events)

# Route for adding a new task
@app.route('/add_task', methods=['POST'])
def add_task():
    # Get task details from the submitted form data
    title = request.form['title']
    start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
    department = request.form['department']

    # Create a new Task instance with the provided details
    new_task = Task(title=title, start_date=start_date, end_date=end_date, department=department)

    # Add the new task to the database and commit the changes
    db.session.add(new_task)
    db.session.commit()

    # Redirect back to the main calendar page
    return redirect('/')

# Route for updating task dates
@app.route('/update_task_dates', methods=['POST'])
def update_task_dates():
    # Get task ID and new dates from the form data
    task_id = request.form['id']
    new_start = datetime.strptime(request.form['start'], '%Y-%m-%d')
    new_end = datetime.strptime(request.form['end'], '%Y-%m-%d')

    # Adjust the new_start and new_end dates by adding one day
    new_start += timedelta(days=1)
    new_end += timedelta(days=1)

    # Get the task from the database using the provided ID
    task = Task.query.get(task_id)
    if task:
        # Update the task's start_date and end_date with the adjusted datetime objects
        task.start_date = new_start
        task.end_date = new_end
        db.session.commit()

    return 'Success'  # Respond with a success message

# Route for user login and authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve user credentials from the submitted form data
        email = request.form['email']
        password = request.form['password']

        # Hash the provided password using SHA-256
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        
        # Check if a user with the provided email and password exists in the 'user' database
        user = User.query.filter_by(email=email, password=password_hash).first()

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

        # Hash the provided password using SHA-256
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

        # Create a new user instance with the provided details
        new_user = User(email=email, password=password_hash, department=department)

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
