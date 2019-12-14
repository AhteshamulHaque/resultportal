#!/usr/bin/python3
from flask import ( jsonify, render_template, session, Flask,
                redirect, url_for, request, make_response, abort )
from app import create_app
from flask_restful import reqparse
from extensions import mysql, login_required
import time, copy
from pprint import pprint
from random import randint
from config import parse_roll
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

app = create_app()

sentry_sdk.init(
    dsn="https://d5c57da451664aa59065c03b4777909d@sentry.io/1471638",
    integrations=[FlaskIntegration()]
)

# @app.errorhandler(404)
# def redirect(error):
#     back = request.referrer
#     return render_template('error/notfound.html', title="HTTP Error | 404 Not Found", error=error, back=back)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        parser = reqparse.RequestParser()
        parser.add_argument('roll', location=['json', 'form'], required=True)

        session.clear()

        args = parser.parse_args()
        ROLL = args['roll'].upper()

        if not ROLL:
            return make_response(jsonify(message="Student does not exists"), 404)

            # this try except exists because if someone gave a roll which could not be split to year, roll, course, branch
            # like 'lsidufs laff';
        try:
            year, course, branch = parse_roll(ROLL)
        except:
            return make_response(jsonify(message="Student does not exists"), 404)


        conn = mysql.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT semesters FROM nilekrator$_{year}.CONF WHERE name='{course}_{branch}'".format(
                year=year,
                course=course,
                branch=branch
            ))

            semesters = cursor.fetchone()[0].split(',')

            #this is always the last semester given....used to show result prediction
            cursor.execute("SELECT name, cgpa, sgpa, image_id FROM nilekrator$_{year}.{course}_{branch}_{semester} INNER JOIN nilekrator$ADMIN.USERS USING(roll) WHERE roll='{roll}'".format(
            year=year, course=course,
            branch=branch, semester=semesters[-1],
            roll=ROLL
            ))
            name, cgpa, sgpa, image_id = cursor.fetchone()

        except:
            return make_response(jsonify(message="Student does not exists"), 404)

        session['roll'] = ROLL
        session['name'] = name
        session['semesters'] = semesters
        session['new_semester'] = semesters[-1]
        session['year'] = year
        session['course'] = course
        session['branch'] = branch
        session['cgpa'] = cgpa
        session['sgpa'] = sgpa
        session['image_id'] = image_id
        session['logged_in'] = True

        cursor.execute("INSERT IGNORE INTO nilekrator$ADMIN.IP_TABLE VALUES('{}', '{}')".format(ROLL, str(time.time()) ))

        conn.commit()
        conn.close()
        return jsonify(roll=session['roll'], name=session['name'], image_id=session['image_id'])

    else:
        return render_template('login.html', title="NIT JSR | Result Portal", random=randint(1, 100000000))

@app.route("/feedback")
def feedback():

    conn = mysql.connect()
    cursor = conn.cursor()

    regno = request.args.get('regno')
    query = request.args.get('query')

    regno = regno.replace("'", '"');
    query = query.replace("'", '"');

    try:
        cursor.execute("INSERT IGNORE INTO nilekrator$ADMIN.FEEDBACK VALUES('{}', '{}')".format(regno, query))
    except:
        abort(406) # Not acceptable
    finally:
        conn.commit()
        conn.close()

    return "Problem saved"


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect( url_for("login") )

if __name__ == '__main__':
    app.run(debug=False, port=80)
