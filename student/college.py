#!/usr/bin/python3.5
from flask import render_template, Blueprint
from extensions import mysql, login_required
from scraper.config import BRANCH_NAME, ROMAN_MAP
from student.studentrank import StudentRank

college = Blueprint('college', __name__, url_prefix='/college/')

## add the information of which year it is in / route 1st year, 2nd year, ...
########################################### College Home ##############################################

@college.route("/")
@login_required
def college_home():
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SHOW DATABASES")

    result = cursor.fetchall()
    batch = []

    for res in result:
    	if res[0].startswith('nilekrator$_2'):
    		batch.append(res[0][12:])

    conn.close()
    return render_template('college/collegehome.html', title="College | TOPPERS", batch=batch, ROMAN_MAP=ROMAN_MAP)


@college.route("/<year>")
@login_required
def year(year):
	conn = mysql.connect()
	cursor = conn.cursor()

	cursor.execute("SELECT name, degree FROM nilekrator$_{year}.CONF WHERE session IS NULL AND scheme IS NULL ORDER BY degree".format(
			year=year
	))

	DEGREE = set()

	result = cursor.fetchall()

	for branch, degree in result:
		DEGREE.add(degree)

	conn.close()
	return render_template('college/batch.html', title = year+" | TOPPERS", DEGREE=DEGREE, result=result, year=year, ROMAN_MAP=ROMAN_MAP, BRANCH_NAME=BRANCH_NAME)

@college.route("/<year>/<course>/<branch>")
@login_required
def collegerank(year, course, branch):
	#actually all results are ranked and then limit records are rendered...fix this


	conn = mysql.connect()
	cursor = conn.cursor()

	cursor.execute("SELECT SUBSTRING_INDEX(semesters,',',-1) FROM nilekrator$_{year}.CONF WHERE name='{course}_{branch}'".format(
		year=year,
		course=course,
		branch=branch
	))

	semester = cursor.fetchone()[0]

	conn.close()

	S = StudentRank('cgpa', year, course, branch, semester)
	S.get_raw_rank()

	return render_template('college/rank.html', title = year+" | "+BRANCH_NAME[branch]+" | TOPPERS",
	            year=year, course=course, branch=branch, BRANCH_NAME=BRANCH_NAME,
	            ranklist=S.get_original_rank( 200 ), ROMAN_MAP= ROMAN_MAP
	            )