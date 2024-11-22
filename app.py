from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# MySQL database connection
db = mysql.connector.connect(
    host="localhost",  # Change to your MySQL host
    user="root",       # Your MySQL username
    password="Rishiraj@123",  # Your MySQL password
    database="insurancedb"  # Name of the database
)

cursor = db.cursor()

# Route to render the form
@app.route('/')
def home():
    return render_template('index.html')  # Make sure your HTML file is named 'index.html'

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit_form():
    # Collecting data from the form
    first_name = request.form['firstName']
    middle_name = request.form['middleName']
    last_name = request.form['lastName']
    gender = request.form['gender']
    age = request.form['age']
    status = request.form['status']
    dob = request.form['dob']
    street_address = request.form['streetAddress']
    city = request.form['city']
    state_province = request.form['stateProvince']
    zip_code = request.form['zipCode']
    email = request.form['email']
    phone_number = request.form['phoneNumber']
    applicant_type = request.form['applicantType']
    applicant_full_name = request.form['applicantFullName']
    applicant_gender = request.form['applicantGender']
    applicant_dob = request.form['applicantDob']

    # Insert the data into MySQL database
    query = """
    INSERT INTO applicants (
        first_name, middle_name, last_name, gender, age, status, dob,
        street_address, city, state_province, zip_code, email, phone_number,
        applicant_type, applicant_full_name, applicant_gender, applicant_dob)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        first_name, middle_name, last_name, gender, age, status, dob,
        street_address, city, state_province, zip_code, email, phone_number,
        applicant_type, applicant_full_name, applicant_gender, applicant_dob
    )

    try:
        cursor.execute(query, values)
        db.commit()
        return redirect('/')  # After successful submission, redirect to the homepage
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        db.rollback()
        return "There was an error with the submission. Please try again."

if __name__ == '__main__':
    app.run(debug=True)
