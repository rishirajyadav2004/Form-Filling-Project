from flask import Flask, render_template, request, redirect, flash, session
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash
from googletrans import Translator

# Flask app setup
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Translator for multilingual support
translator = Translator()

# Function to connect to the MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="insurancedb"
    )


# Home route
@app.route('/')
def home():
    return redirect('/signup')

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return submit_signup()
    return render_template('signup-btn.html')


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return submit_login()
    return render_template('login-btn.html')

# Signup submission route
@app.route('/submit_signup', methods=['POST'])
def submit_signup():
    try:
        first_name = request.form['firstName']
        middle_name = request.form.get('middleName', '')
        last_name = request.form['lastName']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        query = """
        INSERT INTO Users (firstName, middleName, lastName, email, password)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (first_name, middle_name, last_name, email, hashed_password)

        with get_db_connection() as db:
            with db.cursor() as cursor:
                cursor.execute(query, values)
                db.commit()

        flash("Signup successful! Please log in.", "success")
        return redirect('/login')
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash("There was an error during signup. Please try again.", "error")
        return redirect('/signup')
    except Exception as e:
        print(f"Unexpected Error: {e}")
        flash("An unexpected error occurred. Please try again later.", "error")
        return redirect('/signup')

# Login submission route
@app.route('/submit_login', methods=['POST'])
def submit_login():
    email = request.form['email']
    password = request.form['password']
    try:
        query = "SELECT * FROM Users WHERE email = %s"
        with get_db_connection() as db:
            with db.cursor(dictionary=True) as cursor:
                cursor.execute(query, (email,))
                user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['email'] = user['email']
            flash("Login successful!", "success")
            return redirect('/form-filling')
        else:
            flash("Invalid credentials. Please try again.", "error")
            return redirect('/login')
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash("There was an error during login. Please try again.", "error")
        return redirect('/login')
    except Exception as e:
        print(f"Unexpected Error: {e}")
        flash("An unexpected error occurred. Please try again later.", "error")
        return redirect('/login')


@app.route('/form-filling', methods=['GET', 'POST'])
def form_filling():
    if 'user_id' not in session:
        flash("Please log in to access the Medical Insurance Form.", "warning")
        return redirect('/login')

    if request.method == 'POST':
        return submit_form()  # Call the function to handle the form submission
    
    return render_template('index.html')  # Render the form-filling template



@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        # Retrieve and validate required fields
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        
        if not first_name or not last_name or not email:
            flash("Essential fields (First Name, Last Name, Email) are required.", "error")
            return redirect('/form-filling')

        # Validate and handle age
        age = request.form.get('age')
        if not age or not age.isdigit():
            flash("Please provide a valid age.", "error")
            return redirect('/form-filling')

        # Convert age to integer
        age = int(age)

        # Set default values for optional fields
        middle_name = request.form.get('middleName', '')
        gender = request.form.get('gender', '')
        status = request.form.get('status', '')
        dob = request.form.get('dob', None)
        street_address = request.form.get('streetAddress', '')
        city = request.form.get('city', '')
        state_province = request.form.get('stateProvince', '')
        zip_code = request.form.get('zipCode', '')
        phone_number = request.form.get('phoneNumber', '')
        applicant_type = request.form.get('applicantType', '')
        applicant_full_name = request.form.get('applicantFullName', '')
        applicant_gender = request.form.get('applicantGender', '')
        applicant_dob = request.form.get('applicantDob', None)
        digital_signature = request.form.get('digitalSignature', '')

        # Database insertion
        query = """
        INSERT INTO InsuranceForms (firstName, middleName, lastName, gender, age, status, dob, streetAddress, city, 
                                    stateProvince, zipCode, email, phoneNumber, applicantType, applicantFullName, 
                                    applicantGender, applicantDob, digitalSignature)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (first_name, middle_name, last_name, gender, age, status, dob, street_address, city, 
                  state_province, zip_code, email, phone_number, applicant_type, applicant_full_name, 
                  applicant_gender, applicant_dob, digital_signature)

        with get_db_connection() as db:
            with db.cursor() as cursor:
                cursor.execute(query, values)
                db.commit()

        flash("Form submitted successfully!", "success")
        return redirect('/form-filling')
    
    except Exception as e:
        print(f"Error: {e}")
        flash("An error occurred while submitting the form. Please try again.", "error")
        return redirect('/form-filling')


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
