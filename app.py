from flask import Flask, render_template, request, redirect, flash, session
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Function to connect to the MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="insurancedb"
    )

# Home route - redirects to signup
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

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Insert user data into the database
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
        print(f"Error: {err}")
        flash("There was an error during signup. Please try again.", "error")
        return redirect('/signup')

# Login submission route
@app.route('/submit_login', methods=['POST'])
def submit_login():
    email = request.form['email']
    password = request.form['password']

    try:
        # Fetch the user from the database
        query = "SELECT * FROM Users WHERE email = %s"
        with get_db_connection() as db:
            with db.cursor(dictionary=True) as cursor:
                cursor.execute(query, (email,))
                user = cursor.fetchone()

        if user:
            print(f"User found: {user}")
            stored_hashed_password = user['password']
            print(f"Stored hashed password: {stored_hashed_password}")

            # Verify the password
            if check_password_hash(stored_hashed_password, password):
                session['user_id'] = user['id']
                session['email'] = user['email']
                flash("Login successful!", "success")
                return redirect('/form-filling')
            else:
                print("Invalid credentials - Email or password mismatch")
                flash("Invalid credentials. Please try again.", "error")
                return redirect('/login')
        else:
            print("No user found with this email")
            flash("Invalid credentials. Please try again.", "error")
            return redirect('/login')

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash("There was an error during login. Please try again.", "error")
        return redirect('/login')

# Form filling route
@app.route('/form-filling', methods=['GET', 'POST'])
def form_filling():
    if 'user_id' not in session:
        flash("Please log in to access the Medical Insurance Form.", "warning")
        return redirect('/login')

    if request.method == 'POST':
        try:
            # Collect form data
            first_name = request.form['firstName']
            middle_name = request.form.get('middleName', '')
            last_name = request.form['lastName']
            gender = request.form['gender']
            age = int(request.form['age'])
            status = request.form['status']
            dob = request.form['dob']
            street_address = request.form['streetAddress']
            city = request.form['city']
            state_province = request.form['stateProvince']
            zip_code = request.form['zipCode']
            email = request.form['email']
            phone_number = request.form['phoneNumber']
            applicant_type = request.form['applicantType']
            applicant_full_name = request.form.get('applicantFullName', '')
            applicant_gender = request.form.get('applicantGender', '')
            applicant_dob = request.form.get('applicantDob', None)
            digital_signature = request.form['digitalSignature']

            # Insert data into the InsuranceForms table
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

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            flash("There was an error while submitting the form. Please try again.", "error")
            return redirect('/form-filling')

    return render_template('index.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
