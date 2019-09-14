#!/usr/bin/python3.5
from flask import render_template, url_for, Blueprint, session, request, redirect, jsonify, make_response
from extensions import mysql, login_required
from collections import OrderedDict
from scraper.config import BRANCH_NAME, ROMAN_MAP
import os
from student.studentrank import StudentRank
from random import randint

student = Blueprint('student', __name__)


##################### Exception handling for compare page problem in 2016UGCS093 with others ###################
def custom_key_filter(others, i, j, me):
    try:
        return others[i*len(me)+j][4]
    except Exception as e:
        return 0

############################################ profile ######################################################
@student.route("/profile")
@login_required
def profile():
    conn = mysql.connect()
    cursor = conn.cursor()
    result = OrderedDict()

    sorted_sems  = sorted(session['semesters'], reverse=True)
    fail_flag = False

    for semester in sorted_sems:
        # this try-except because some has more result than the others like one has 3, 4 semesters other
        # may have 2, 3, 4 semester

        try:
            cursor.execute('''SELECT roll, subject_code, subject_name, end_sem, test_1, test_2, grade, total, assignment, quiz_avg
                FROM nilekrator$_{year}.RESULT_{course}_{branch}_{semester} INNER JOIN nilekrator$ADMIN.SUBJECTS USING(subject_code)
                WHERE roll='{roll}' '''.format(
                year=session['year'],
                course=session['course'],
                branch=session['branch'],
                semester=semester,
                roll=session['roll']
            ))

            result[semester] = OrderedDict()

            for i in range(cursor.rowcount):
                roll, code, subject_name, end_sem, test_1, test_2, grade, total, assignment, quiz_avg = cursor.fetchone()
                result[semester][code] = {
                    'subject_name': subject_name,
                    'test_1': test_1,
                    'test_2': test_2,
                    'grade': grade,
                    'total': total,
                    'end_sem': end_sem,
                    'assignment': assignment,
                    'quiz_avg': quiz_avg
                }

            cursor.execute("SELECT cgpa, sgpa, result_status FROM nilekrator$_{year}.{course}_{branch}_{semester} WHERE roll='{roll}'".format(
                year=session['year'],
                course=session['course'],
                branch=session['branch'],
                semester=semester,
                roll=session['roll']
            ))

            cgpa, sgpa, result_status = cursor.fetchone()

            if cgpa == 0:
                fail_flag = True

            cursor.execute("SELECT publish_date FROM nilekrator$_{year}.CONF WHERE name='{course}_{branch}_{semester}'".format(
                course=session['course'],
                year=session['year'],
                branch=session['branch'],
                semester=semester
            ))
            publish_date = cursor.fetchone()[0]

            result[semester]['cgpa'] = cgpa
            result[semester]['sgpa'] = sgpa
            result[semester]['result_status'] = result_status
            result[semester]['publish_date'] = publish_date
        except Exception as e:
            del result[semester]

    cursor.execute("SELECT rank FROM nilekrator$ADMIN.USERS WHERE roll='{}'".format(session['roll']))
    rank = cursor.fetchone()[0]

    conn.close()
    return render_template('student/profile.html', title="Profile", result=result, BRANCH_NAME=BRANCH_NAME,isinstance=isinstance, ROMAN_MAP=ROMAN_MAP, rank=rank, random=randint(1, 1000000), fail_flag=fail_flag)

############################################## compare ##############################################3
@student.route("/compare", methods=["GET", "POST"])
@login_required
def compare():

    if request.method == "GET":
        conn = mysql.connect()
        cursor = conn.cursor()

        semester = request.args.get('semester')

        if semester == None or semester not in session['semesters']:
            semester = session['new_semester']

        cursor.execute("SELECT name, e.roll, image_id FROM nilekrator$_{year}.{course}_{branch}_{semester} e INNER JOIN nilekrator$ADMIN.USERS d on e.roll = d.roll".format(
            year=session['year'],
            course=session['course'],
            branch=session['branch'],
            semester=semester
        ))

        conn.close()
        return render_template('student/show_to_compare.html', title="Choose to Compare", ROMAN_MAP=ROMAN_MAP, students=cursor.fetchall(), active_semester=semester)

    # here rolls are passed from post request for actual generation of comparision table
    elif request.method == "POST":

        semester = request.form['semester']
        rolls = [ '\''+r+'\'' for r in request.form if r != "semester" and r.strip() != '' ]

        if rolls == []:
            return redirect(url_for('student.compare'))

        conn = mysql.connect()
        cursor = conn.cursor()

        subject_map = {}
        # your result
        # user data is selected from four tables users, UG_CS(for cgpa, sgpa), RESULT_UG_CS, subjects(for subject name)
        cursor.execute('''SELECT roll, name, subject_name, subject_code, total, cgpa, sgpa from nilekrator$_{year}.{course}_{branch}_{semester}
            INNER JOIN (SELECT * FROM nilekrator$ADMIN.SUBJECTS INNER JOIN (SELECT *  FROM nilekrator$_{year}.RESULT_{course}_{branch}_{semester}
            INNER JOIN nilekrator$ADMIN.USERS USING(roll) WHERE roll='{roll}') s USING(subject_code)) d using(roll)'''.format(
            year=session['year'],
            course=session['course'],
            branch=session['branch'],
            semester=semester,
            roll=session['roll']
        ))

        me = cursor.fetchall()

        # making subject map for line chart
        for stu in me:
            subject_map[stu[3]] = stu[2]

        cursor.execute('''SELECT roll, name, subject_name, subject_code, total, cgpa, sgpa from nilekrator$_{year}.{course}_{branch}_{semester}
            INNER JOIN (SELECT * FROM nilekrator$ADMIN.SUBJECTS INNER JOIN (SELECT *  FROM nilekrator$_{year}.RESULT_{course}_{branch}_{semester}
            INNER JOIN nilekrator$ADMIN.USERS USING(roll) WHERE roll in ({roll}) ) s USING(subject_code)) d using(roll)'''.format(
            year=session['year'],
            course=session['course'],
            branch=session['branch'],
            semester=semester,
            roll=",".join(rolls)
        ))

        others = cursor.fetchall()

        cursor.execute("SELECT publish_date FROM nilekrator$_{year}.CONF WHERE name='{course}_{branch}_{semester}'".format(
            course=session['course'],
            year=session['year'],
            branch=session['branch'],
            semester=semester
        ))

        publish_date = cursor.fetchone()[0]

        conn.close()

        return render_template("student/compare_result.html", title="Compare Result",
            me=me, others=others, total_rolls=len(rolls),semester=semester, publish_date=publish_date,
            custom_key_filter=custom_key_filter, ROMAN_MAP=ROMAN_MAP, subject_map=subject_map)

########################################## stats ##################################################
@student.route("/statistics")
@login_required
def stats():
    conn = mysql.connect()
    cursor = conn.cursor()

    cgp_sgp = {}

    for semester in session['semesters']:
        cursor.execute("SELECT cgpa, sgpa FROM nilekrator$_{year}.{course}_{branch}_{semester} WHERE roll='{roll}'".format(
            year=session['year'],
            course=session['course'],
            branch=session['branch'],
            semester=semester,
            roll=session['roll']
        ))

        cgp_sgp[semester] = cursor.fetchone()

    conn.close()
    return render_template('student/statistics.html', ROMAN_MAP=ROMAN_MAP, title="Statistics", cgp_sgp=cgp_sgp)


############################################# rank page ##############################################
@student.route("/rank")
@login_required
def rank():

    method = request.args.get('method','cgpa')
    semester = request.args.get('semester', session['new_semester'])

    if method not in ['sgpa', 'cgpa']:
        method = 'cgpa'

    if semester not in [str(i) for i in range(1, 9)]:
        semester = session['new_semester']

    #actually all results are ranked and then limit records are rendered...fix this
    limit = request.args.get('limit', 130)

    Stu = StudentRank(method, session['year'], session['course'], session['branch'], semester)
    Stu.get_raw_rank()

    return render_template(
        'student/rank.html', title = "Rank",
        failed=request.args.get('failed'), failed_list=Stu.get_failed_once(),
        pass_ranklist=Stu.get_original_rank( int(limit) ),
        semester=semester, method=method, ROMAN_MAP=ROMAN_MAP, random=randint(1, 1000000)
    )

############################################# updaterank ##################################
@student.route("/updaterank")
@login_required
def updaterank():

    conn = mysql.connect()
    cursor = conn.cursor()

    semester = session['new_semester']

    S = StudentRank('cgpa', session['year'], session['course'], session['branch'], semester)

    result = S.get_failed_once()

    for stu in result:
        cursor.execute("UPDATE nilekrator$ADMIN.USERS SET rank=0 WHERE roll='{}'".format(stu[0]))

    S.get_raw_rank()

    for stu in S.get_original_rank(200):
        cursor.execute( "UPDATE nilekrator$ADMIN.USERS SET rank={} WHERE roll='{}'".format( stu[-1], stu[0]) )

    conn.close()
    return make_response(jsonify(message="Update Successfull"), 200)

########################################### test ######################################################
@student.route("/test")
def test():

    return render_template('student/test.html', title = "Test", images=os.listdir('static/images'))