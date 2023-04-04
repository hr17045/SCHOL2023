from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import calendar, datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Harvey/Desktop/SCHOL2023/instance/user.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(120), nullable=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        department = request.form['department']
        
        # Query the database for the submitted username and password
        user = User.query.filter_by(email=email, password=password, department=department).first()

        if user:
            return 'Login successful!'
        else:
            return 'Invalid email or password'
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        department = request.form['department']

        # Create a new user object and add it to the database
        new_user = User(email=email, password=password, department=department)
        db.session.add(new_user)
        db.session.commit()

        # Display a success message
        return 'Sign up successful!'

    return render_template('signup.html')

@app.route("/")
def index():
    # Get the current year and month
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month

    # Create a calendar object
    cal = calendar.monthcalendar(year, month)

    # Render the calendar template
    return render_template("calendar.html", cal=cal, year=year, month=month)

if __name__ == "__main__":
    app.run(debug=True)
