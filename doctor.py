import replicate
from flask import Flask, render_template, redirect, session, url_for, request, flash, jsonify
import psycopg2
import random
import os
import pandas as pd

app = Flask(__name__)
mydb = psycopg2.connect(
    host='dpg-d23i2j15pdvs739vngog-a',
    user='sri_xavk_user',
    password='XUK27FvluX87Uyc61e7XTg9vssScXCdK',
    database='sri_xavk'
)
mycursor = mydb.cursor()
app.secret_key = 'sri@vatsav*40'


def create_table():
    try:
        mycursor.execute("CREATE TABLE IF NOT EXISTS userlogin (userid VARCHAR(20), password VARCHAR(20))")
    except mysql.connector.Error as err:
        return f"Failed to create table: {err}"


def create_table2():
    try:
        mycursor.execute(
            "CREATE TABLE IF NOT EXISTS appointment (id VARCHAR(20) PRIMARY KEY, name VARCHAR(20), age VARCHAR(5), gender VARCHAR(20), mobile VARCHAR(15), doctor VARCHAR(20), datetime VARCHAR(20), username VARCHAR(20))"
        )
    except mysql.connector.Error as err:
        return f"Failed to create table: {err}"


csv_file = "https://raw.githubusercontent.com/srivatsav840/healthtap/refs/heads/main/Medicine_Details.csv"
df = pd.read_csv(csv_file)
symptoms_data = df['Uses'].unique()


def create_table3():
    try:
        mycursor.execute(
            "CREATE TABLE IF NOT EXISTS doctoravail (doctor_name varchar(20),doctor_id varchar(20),doctor_specialization varchar(20) ,monday varchar(20),tuesday varchar(20),wednesday varchar(20),thursday varchar(20),friday varchar(20),saturday varchar(20),sunday varchar(20) )"
        )
    except mysql.connector.Error as err:
        return f"Failed to create table: {err}"


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    return render_template('admin.html')


@app.route('/user', methods=['POST', 'GET'])
def user():
    return render_template('user.html')


@app.route('/signin', methods=["POST", "GET"])
def signin():
    return render_template('signin.html')


@app.route('/signup', methods=["POST", "GET"])
def signup():
    return render_template('signup.html')


@app.route('/userhome', methods=["POST", "GET"])
def userhome():
    return render_template('userhome.html')


@app.route('/signin_submit', methods=['POST', 'GET'])
def signin_submit():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        session['username'] = username
        create_table()
        mycursor.execute("SELECT * FROM userlogin WHERE userid = %s AND password = %s", (username, password))
        row = mycursor.fetchone()
        if row is None:
            re = "username or password did not match please try again!!"
            return render_template('signin.html', re=re)
        else:
            return redirect(url_for('userhome'))


@app.route('/signup_submit', methods=["POST", "GET"])
def signup_submit():
    if request.method == "POST":
        user = request.form['username']
        pswd = request.form['password']
        create_table()
        mycursor.execute("SELECT userid FROM userlogin WHERE userid = %s", (user,))
        row = mycursor.fetchall()
        if not row:
            sql = "INSERT INTO userlogin (userid, password) VALUES (%s, %s)"
            values = (user, pswd)
            mycursor.execute(sql, values)
            mydb.commit()
            re = "Account successfully created. You can login now."
            return render_template('signup.html', re=re)
        else:
            ss = "Username already exists. Use a different username."
            return render_template('signup.html', ss=ss)

    return render_template('signup.html')


@app.route('/gosignin', methods=["POST", "GET"])
def gosignin():
    return redirect(url_for('signin'))


@app.route('/gosignup', methods=["POST", "GET"])
def gosignup():
    return redirect(url_for('signup'))


@app.route('/appointmentbook', methods=["POST", "GET"])
def appointmentbook():
    return render_template('appointment.html')


@app.route('/medical', methods=["POST", "GET"])
def medico():
    return render_template('hzero.html')


@app.route("/medico", methods=["POST", "GET"])
def meddes():
    detailed_results = []

    if request.method == 'POST':
        selected_disease = request.form['disease_select']

        if selected_disease:
            result = df[df['Uses'].str.contains(selected_disease, case=False, na=False)]

            if not result.empty:
                # Prepare a list of dictionaries for each medicine
                detailed_results = [
                    {
                        'medicine_name': row['Medicine Name'],
                        'composition': row['Composition'],
                        'uses': row['Uses'],
                        'side_effects': row['Side_effects'],
                        'image_url': row['Image URL'],
                        'manufacturer': row['Manufacturer'],
                        'excellent_review': row['Excellent Review %'],
                        'average_review': row['Average Review %'],
                        'poor_review': row['Poor Review %']
                    }
                    for index, row in result.iterrows()
                ]

                return render_template('med.html', results=detailed_results)
            else:
                not_found_message = (
                    f"Oops! No information found for '{selected_disease}'."
                    "Why don't you ask the AI doctor?"
                )
                return render_template('med.html', error=not_found_message)

    unique_diseases = sorted(df['Uses'].unique())
    return render_template('med.html', unique_diseases=unique_diseases, results=None)


@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    query = request.args.get('query', '')

    if query:
        matches = df[df['Uses'].str.contains(query, case=False, na=False)]['Uses'].unique()
    else:
        matches = df['Uses'].unique()

    return jsonify(matches.tolist())


os.environ["REPLICATE_API_TOKEN"] = "r8_Ilv08PRu9QLAUlCwoWJPIofqABWM4Nu3K1m1D"


@app.route("/aidoctor", methods=["POST", "GET"])
def aidoc():
    if request.method == 'POST':
        try:
            inputai = request.form.get("inputai")
            if not inputai:
                raise ValueError("Invalid input")

            # Define prompts and parameters
            pre_prompt = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
            model_prompt = f"Can you provide detailed medical information about {inputai} in exactly 200 words, presented as 10 concise points?"

            # Call Replicate API
            output = replicate.run(
                'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5',
                input={"prompt": model_prompt, "temperature": 0.1, "top_p": 0.9, "max_length": 500,
                       "repetition_penalty": 1}
            )
            full_response = "".join(output)

            return render_template('aidoc.html', full_response=full_response)
        except Exception as e:
            # Log the error for debugging
            print(f"Error: {str(e)}")
            return render_template('aidoc.html', error_message="An error occurred.")
    else:
        return render_template('aidoc.html')


@app.route('/bookappointment', methods=["POST", "GET"])
def bookappointment():
    if request.method == "POST":
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        mobile = request.form['mobile']
        datetime = request.form['datetime']
        doctor = request.form['doctor']
        username = session.get('username', None)
        create_table2()
        mycursor.execute("SELECT datetime FROM appointment WHERE datetime = %s", (datetime,))
        row = mycursor.fetchone()
        if row:
            flash("No slot is available at the selected time. Please choose a different time.", "error")
            return redirect(url_for('bookappointment'))
        else:
            id = ''.join(random.choices('0123456789', k=10))
            sql = "INSERT INTO appointment (id, name, age, gender, mobile, doctor, datetime, username) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            values = (id, name, age, gender, mobile, doctor, datetime, username)
            mycursor.execute(sql, values)
            mydb.commit()
            flash(f"Your appointment has been successfully booked. Your ID is {id}. Be there before time.", "success")
            return redirect(url_for('bookappointment'))

    return render_template('appointment.html')


@app.route('/cancel')
def cancel():
    try:
        username = session.get('username', None)
        if username:
            search_query = request.args.get('search', '').lower()
            if search_query:
                query = "SELECT id, name, age, datetime, doctor ,mobile FROM appointment WHERE username = %s AND LOWER(name) LIKE %s"
                mycursor.execute(query, (username, f"%{search_query}%"))
            else:
                query = "SELECT id, name, age, datetime, doctor,mobile  FROM appointment WHERE username = %s"
                mycursor.execute(query, (username,))
            data = mycursor.fetchall()
            return render_template('cancel.html', data=data)
        else:
            return render_template('cancel.html', ss="No username in session.")
    except Exception as e:
        return render_template('cancel.html', ss="Error while fetching: " + str(e))


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == "POST":
        oldname = request.form['name']
        oldage = request.form['age']
        oldgender = request.form['gender']
        oldcontact = request.form['mobile']
        olddoctor = request.form['doctor']
        olddate = request.form['datetime']
        username = session.get('username', None)
        appointment_id = request.args.get('id')

        mycursor.execute(
            "UPDATE appointment SET name=%s, age=%s, gender=%s, mobile=%s, doctor=%s, datetime=%s WHERE id=%s AND username=%s",
            (oldname, oldage, oldgender, oldcontact, olddoctor, olddate, appointment_id, username)
        )
        mydb.commit()
        flash("Appointment successfully updated!", "success")
        return redirect(url_for('cancel'))
    else:
        appointment_id = request.args.get('id')
        username = session.get('username', None)

        mycursor.execute(
            "SELECT name, age, gender, mobile, doctor, datetime FROM appointment WHERE id=%s AND username=%s",
            (appointment_id, username)
        )
        appointment = mycursor.fetchone()

        if appointment:
            oldname, oldage, oldgender, oldcontact, olddoctor, olddate = appointment
            return render_template('edit.html', oldname=oldname, oldage=oldage, oldgender=oldgender,
                                   oldcontact=oldcontact, olddoctor=olddoctor, olddate=olddate, id=appointment_id)
        else:
            flash("Appointment not found.", "error")
            return redirect(url_for('cancel'))


@app.route('/cancelappointment', methods=['POST', 'GET'])
def cancelappointment():
    username = session.get('username', None)

    if request.method == "POST":
        id = request.form.get('task')

        # Delete the appointment
        query_delete = "DELETE FROM appointment WHERE id = %s AND username = %s"
        mycursor.execute(query_delete, (id, username))
        mydb.commit()

        flash("Appointment successfully canceled.", "success")

    # This part handles both GET requests and the refreshed page after cancellation
    query_select = "SELECT id, name, age, datetime, doctor, mobile FROM appointment WHERE username = %s"
    mycursor.execute(query_select, (username,))
    data = mycursor.fetchall()

    return render_template('cancel.html', data=data)




@app.route('/confirmcancel', methods=['POST'])
def confirmcancel():
    if request.method == "POST":
        id = request.form.get('task')
        username = session.get('username', None)
        query_delete = "DELETE FROM appointment WHERE id = %s AND username = %s"
        mycursor.execute(query_delete, (id, username))
        mydb.commit()

        flash("Appointment successfully canceled.", "success")
        return redirect(url_for('cancelappointment'))

    else:
        flash("Invalid request.", "error")
    return redirect(url_for('cancel'))


@app.route('/adminenter', methods=['POST', 'GET'])
def adminentry():
    if request.method == "POST":
        key = request.form['key']
        if key == "1234567890":
            return render_template('doctors_show.html')
        else:
            re = "Key not matched enter a valid key"
            return render_template('admin.html', re=re)
    return render_template('admin.html')


@app.route('/show_doctors', methods=["POST","GET"])
def show_doctors():
    try:
        mycursor.execute("""
            SELECT doctor_name, doctor_id, doctor_specialization, 
                   monday, tuesday, wednesday, thursday, 
                   friday, saturday, sunday 
            FROM doctoravail
        """)
        data = mycursor.fetchall()

        if not data:
            data = "No doctor is appointed yet!"

        return render_template('doctors_show.html', data=data)

    except Exception as e:

        return render_template('doctors_show.html', dat="An error occurred: " + str(e))


@app.route('/edit_doctor', methods=['GET', 'POST'])
def edit_doctor():
    if request.method == 'POST':
        # Retrieve data from the form
        doctor_id = request.form.get('doctor_id')
        doctorname = request.form.get('doctorname')
        doctor_specialization = request.form.get('doctor_specialization')
        monday = request.form.get('monday')
        tuesday = request.form.get('tuesday')
        wednesday = request.form.get('wednesday')
        thursday = request.form.get('thursday')
        friday = request.form.get('friday')
        saturday = request.form.get('saturday')
        sunday = request.form.get('sunday')

        try:
            # Update the doctor's details in the database
            query = """
                UPDATE doctoravail
                SET doctor_name = %s, doctor_specialization = %s, 
                    monday = %s, tuesday = %s, wednesday = %s, thursday = %s,
                    friday = %s, saturday = %s, sunday = %s
                WHERE doctor_id = %s
            """
            values = (doctorname, doctor_specialization, monday, tuesday, wednesday, thursday, friday, saturday, sunday, doctor_id)
            mycursor.execute(query, values)
            mydb.commit()

            flash("Doctor details successfully updated!", "success")

            # Redirect back to the doctor list
            return redirect(url_for('show_doctors'))

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('edit_doctor', doctor_id=doctor_id))

    else:
        # Handle the GET request
        doctor_id = request.args.get('doctor_id')

        try:
            # Fetch the doctor's details using the doctor_id
            query = "SELECT doctor_name, doctor_id, doctor_specialization, monday, tuesday, wednesday, thursday, friday, saturday, sunday FROM doctoravail WHERE doctor_id = %s"
            mycursor.execute(query, (doctor_id,))
            doctor = mycursor.fetchone()

            if not doctor:
                flash("Doctor not found.", "error")
                return redirect(url_for('show_doctors'))

            # Render the update form with the doctor's current details
            return render_template('edit_doctor.html', doctor=doctor)

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('show_doctors'))


@app.route('/remove_doctor', methods=['POST'])
def remove_doctor():
    doctor_id = request.form.get('doctor_id')

    try:
        # Delete the doctor from the database
        query = "DELETE FROM doctoravail WHERE doctor_id = %s"
        mycursor.execute(query, (doctor_id,))
        mydb.commit()

        flash("Doctor successfully removed!", "success")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")

    # Redirect back to the show doctors page
    return redirect(url_for('show_doctors'))


@app.route('/adminpage')
def new_entry():
    return render_template('adminpage.html')



@app.route('/add', methods=['POST', 'GET'])
def doctor_details_add():
    if request.method == "POST":
        doctorid = request.form['doctor_id']
        doctorname = request.form['doctorname']
        doctor = request.form['doctor']
        monday = request.form['monday']
        tuesday = request.form['tuesday']
        wednesday = request.form['wednesday']
        thursday = request.form['thursday']
        friday = request.form['friday']
        saturday = request.form['saturday']
        sunday = request.form['sunday']

        try:
            create_table3()
            query = "INSERT INTO doctoravail(doctor_name,doctor_id, doctor_specialization, monday, tuesday, wednesday, thursday, friday, saturday, sunday) VALUES (%s,%s,%s, %s, %s, %s, %s, %s, %s, %s)"
            values = (doctorname, doctorid, doctor, monday, tuesday, wednesday, thursday, friday, saturday, sunday)
            mycursor.execute(query, values)
            mydb.commit()
            re = "Data successfully added"
        except Exception as e:
            re = f"Something went wrong: {str(e)}"

        return render_template('adminpage.html', re=re)


@app.route('/doctor_availability', methods=['POST', 'GET'])
def doctor_availability():
    return render_template('/doctor_availability.html')


@app.route('/doctoravailability', methods=['POST', 'GET'])
def doctoravailability():
    if request.method == "POST":
        doctor_specialization = request.form['doctor']
        mycursor.execute("SELECT * FROM doctoravail WHERE doctor_specialization=%s", (doctor_specialization,))
        data = mycursor.fetchall()
        print("Fetched Data:", data)
        if not data:
            data = "No doctor appointed for your necessity"
        return render_template('doctor_availability.html', data=data)
    return render_template('doctor_availability.html', data=None)


if __name__ == "__main__":
    print("Starting Flask app...")
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

