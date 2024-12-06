from flask import Flask, flash, redirect, render_template, request, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
from MySQLdb import IntegrityError

app = Flask(__name__)
app.template_folder = 'templates'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'rithika_1609'
app.config['MYSQL_DB'] = 'eventmanagementdb'
mysql = MySQL(app)


@app.route('/', methods=['POST', 'GET'])
def main():
    if request.method == 'POST':
        value = request.form
        if "login" in value:
            return redirect('/login')
        elif "start" in value:
            return redirect('/events')
    return render_template('users.html')


@app.route('/events', methods=['GET'])
def events():
    cur = mysql.connection.cursor()
    # Get the current date and time
    current_datetime = datetime.now()
    # Fetch only future events
    cur.execute("SELECT * FROM eventmanagementdb.event WHERE event_date > %s", [current_datetime])
    events_data = cur.fetchall()
    cur.close()
    return render_template('events.html', events=events_data)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        eventtitle = request.form.get("searchbyname", "")
        eventtype = request.form.get("searchbytype", "")
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM event WHERE event_name = %s OR event_type = %s ORDER BY event_date',
                    (eventtitle, eventtype))
        events = cur.fetchall()
        cur.close()
        return render_template('search.html', events=events)
    return render_template('search.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        datau = request.form['username']
        datap = request.form['password']
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (datau, datap))
        s = cur.fetchall()
        cur.close()
        if len(s) == 0:
            flash("Login failed. Please try again.")
            return redirect('/login')
        else:
            return redirect('/menu')
    return render_template('login.html')


@app.route('/menu', methods=['POST', 'GET'])
def menu():
    if request.method == 'POST':
        value = request.form
        opr = str(value['option'])
        if opr == "List events":
            return redirect('/list')
        elif opr == "new event":
            return redirect('/insert')
        elif opr == "event cancellation":
            return redirect('/delete')
        elif opr == "change in event details":
            return redirect('/update')
        elif opr == "event details":
            return redirect('/select')
    return render_template('menu.html')


@app.route('/list', methods=['POST', 'GET'])
def list():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM eventmanagementdb.event")
    events = cur.fetchall()
    if len(events) == 0:
        events = ("---",)
    cur.close()
    return render_template('list.html', events=events)


@app.route('/insert', methods=['GET', 'POST'])
def insert():
    if request.method == 'POST':
        value = request.form
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO eventmanagementdb.event (event_id, event_name, performer, event_date, event_time, event_type, contact_no, email_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (value['event_id'], value['event_name'], value['performer_name'], value['event_date'], value['event_time'], value['event_type'], value['contact_no'], value['email_id'])
            )
            cur.execute(
                "INSERT INTO eventmanagementdb.performers (event_id, performer_name, about_performer) VALUES (%s,%s,%s)",
                (value['event_id'], value['performer_name'], value['about_performer'])
            )

            seat_data = [
                (value['event_id'], "platinum", 5000, "A1", 0),
                (value['event_id'], "platinum", 5000, "A2", 0),
                (value['event_id'], "platinum", 5000, "A3", 0),
                (value['event_id'], "platinum", 5000, "A4", 0),
                (value['event_id'], "gold", 3000, "B1", 0),
                (value['event_id'], "gold", 3000, "B2", 0),
                (value['event_id'], "gold", 3000, "B3", 0),
                (value['event_id'], "gold", 3000, "B4", 0),
                (value['event_id'], "silver", 1500, "C1", 0),
                (value['event_id'], "silver", 1500, "C2", 0),
                (value['event_id'], "silver", 1500, "C3", 0),
                (value['event_id'], "silver", 1500, "C4", 0),
            ]
            cur.executemany(
                "INSERT INTO eventmanagementdb.seats (event_id, seat_type, amount, seat_no, status) VALUES (%s,%s,%s,%s,%s)",
                seat_data
            )
            mysql.connection.commit()

            cur.close()

            return redirect('/list')

        except IntegrityError as e:
            mysql.connection.rollback()  # Rollback changes on error
            error_message = "An event is already registered at this date and time."
            cur.close()
            return render_template('insert.html', error=error_message)

    return render_template('insert.html')

@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("""UPDATE eventmanagementdb.event 
                       SET event_name=%s, performer=%s, event_date=%s, event_time=%s, event_type=%s, contact_no=%s, email_id=%s 
                       WHERE event_id=%s""",
                    (request.form['name'], request.form['performer'], request.form['date'], request.form['time'],
                     request.form['type'], request.form['contactno'], request.form['email'], request.form['change']))
        flash("UPDATED SUCCESSFULLY")
        mysql.connection.commit()
        cur.close()
        return redirect('/list')
    return render_template("update.html")


@app.route('/delete', methods=['POST', 'GET'])
def delete():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        cur.execute("DELETE FROM eventmanagementdb.event WHERE event_id=%s", (request.form['event_id'],))
        flash("DELETED SUCCESSFULLY")
        mysql.connection.commit()
        cur.close()
        return redirect('/list')
    return render_template("delete.html")


@app.route('/select', methods=['POST', 'GET'])
def select():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM eventmanagementdb.event where event_id=%s", (request.form['search'],))
        events = cur.fetchall()
        if len(events) == 0:
            events = ("-----",)
        cur.close()
        return render_template("list.html", events=events)
    return render_template("eventdetails.html")


@app.route('/seats', methods=['GET', 'POST'])
def seats():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("""SELECT * FROM eventmanagementdb.seats,eventmanagementdb.events 
                       WHERE eventmanagementdb.events.event_id=%s AND eventmanagementdb.events.event_id = seats.event_id 
                       ORDER BY eventmanagementdb.seats.amount DESC""",
                    [request.form["eventid"]])
        seats = cur.fetchall()
        cur.close()
        return render_template('seats.html', seats=seats, eventid=request.form["eventid"])
    return render_template('seats.html')


@app.route('/bookseat', methods=['GET', 'POST'])
def bookseat():
    if request.method == 'POST':
        eventid = request.form["eventid"]
        seatno = request.form["seatno"]

        if (seatno[0] == 'A'):
            seattype = "platinum"
        elif (seatno[0] == 'B'):
            seattype = "gold"
        else:
            seattype = "silver"

        cur = mysql.connection.cursor()
        cur.execute("SELECT status FROM eventmanagementdb.seats WHERE seat_no=%s AND event_id=%s", [seatno, eventid])
        state = cur.fetchall()

        if state[0][0] == 0:
            cur.execute(
                "INSERT INTO eventmanagementdb.guests (event_id, name, gender, dob, mobile, seat_type, seat_no) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                [eventid, request.form["name"], request.form["gender"], request.form["dob"], request.form["mobile"],
                 seattype, seatno])
            cur.execute("UPDATE eventmanagementdb.seats SET status = %s WHERE seat_no = %s AND event_id = %s",
                        [1, seatno, eventid])
            mysql.connection.commit()
            errorstatus = 0
        else:
            errorstatus = 1

        cur.close()
        return render_template('bookingdone.html', errorstatus=errorstatus)
    return render_template('bookseat.html')

@app.route('/performer', methods=['GET', 'POST'])
def performer():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM eventmanagementdb.performers WHERE event_id = %s", [request.form["eventid"]])
        performer = cur.fetchall()
        cur.close()
        return render_template('performer.html', performer=performer)
    return render_template('performer.html')


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)
