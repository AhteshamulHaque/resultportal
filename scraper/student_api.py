from flask_restful import Api, Resource, reqparse
from flask import Blueprint
from urllib import request, parse
import random, re
from bs4 import BeautifulSoup
from extensions import mysql
from collections import OrderedDict
from config import parse_roll


api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# /student/<roll> gives the student result
# /student/<roll>?semester=2&save=true saves the result in the database and show the result
# /student/<roll>?semester=2&complete=true updates the db for the branch as complete

parser = reqparse.RequestParser()
parser.add_argument('semester', choices=[str(i) for i in range(1, 10)], help='Semester must be an integer (required field)')
parser.add_argument('key',help='A key is needed')
parser.add_argument('complete',action='store_true', help='Indicates the completion of downloading of a branch') # send by ajax request on five unsuccessful attempts
parser.add_argument('save',action='store_true', help='Shows if the result will be saved in database or not')

######################################## User ################################################
#valid routes of the student api
@api.resource("/student/<roll>")
class User(Resource):

  def get(self, roll):
    STUDENT = None
    args = parser.parse_args()
    if args.semester:
        STUDENT = Student(roll, args.semester)
    else:
        STUDENT = Student(roll)

    semesters, next_request_post_data, status_code = STUDENT.first_call_response()

    if status_code == 404:
        #the whole class is downloaded so update ADMIN.DOWNLOADS to completed = 1
      if args.complete and args.semester:
          conn = mysql.connect()
          cursor = conn.cursor()

          year, course, branch = parse_roll(roll)

          cursor.execute("UPDATE nilekrator$ADMIN.DOWNLOADS SET completed=1 WHERE name='"+year+"$"+course+"_"+branch+"_"+args.semester+"'")
          conn.commit()
          conn.close()
          return { "message": "Database download for "+year+"$"+course+"_"+branch+"_"+args.semester+" is completed" }

      print( roll+" failed "+"for semester "+str(args.semester) )
      return {"error":{ "message":  "Student doesn't exists or result not yet published" }}, 404

    elif status_code == 503:
      print( roll+" failed "+"for semester "+str(args.semester) + " due to networking error")
      return {"error": {"message": "Connection not found"}}, 503


    result = STUDENT.second_call_response(next_request_post_data)

    if result == False:
      print( roll+" failed "+"for semester "+str(args.semester) +" in second post call")
      return {"error":{ "message":  "Student doesn't exists or result not yet published" }}, 404
    else:
        if args.save:
            return save_to_db(result, args.semester or STUDENT.semester)
        else:
            result['database_save'] = False
            return result

# this function save the result to the proper table...returns its own json message
def save_to_db(result, sem):

    if result['given_roll'] != result['roll']:  #it shows branch transition in some semester
        print( result['roll']+" failed "+"for semester "+ sem +" branch transition")
        return {"message": "Student doesn't exists or result not yes published" }, 404

    conn = mysql.connect()
    cursor = conn.cursor()

    roll = result['roll']

    year, course, branch = parse_roll(roll)

    # update conf table (must be ignored beacause it will execute for every student of the same branch)

    #insert student in UG_CS_3
    cursor.execute("INSERT IGNORE INTO nilekrator$_"+year+".CONF VALUES("+'''
        "'''+course+"_"+branch+'_'+result['semester']+'''",
        "'''+result['session']+'''",
        "'''+result['publish_date']+'''",
        "'''+result['semester']+'''",
        "'''+result['scheme']+'''",
        "'''+result['degree']+'''"
    )''')

    cursor.execute("INSERT IGNORE INTO nilekrator$ADMIN.USERS VALUES('{roll}', '{name}', '{image}.jpg', 0)".format(
      roll=result['roll'],
      name=result['name'],
      image=result['image_id']
    ))

    cursor.execute("DELETE FROM nilekrator$_"+year+"."+course+"_"+branch+"_"+result['semester']+" WHERE roll='"+result['roll']+"'")

    cursor.execute("INSERT INTO nilekrator$_"+year+"."+course+"_"+branch+"_"+result['semester']+'''(roll, cgpa, sgpa, result_status) VALUES(
        "'''+result['roll']+'''",
        '''+result['cgpa']+''',
        '''+result['sgpa']+''',
        "'''+result['result_status']+'''"
    )''')

    #insert student in RESULT_UG_CS_2
    for subject_code in result['result']:
        cursor.execute("INSERT INTO nilekrator${table} VALUES('{roll}', '{code}', {end_sem}, {test_1:.2f}, {test_2:.2f}, '{grade}', {total}, {assignment}, {quiz_avg} )".format(
            table="_"+year+"."+"RESULT_"+course+"_"+branch+"_"+result['semester'],
            roll=result['roll'],
            code=subject_code,
            end_sem=return_zero_if_empty( result['result'][subject_code]['end_sem'] ),
            test_1=return_zero_if_empty( result['result'][subject_code]['test_1'] ),
            test_2=return_zero_if_empty( result['result'][subject_code]['test_2'] ),
            grade=result['result'][subject_code]['grade'],
            total=return_zero_if_empty( result['result'][subject_code]['total'] ),
            assignment=return_zero_if_empty( result['result'][subject_code]['assignment'] ),
            quiz_avg=return_zero_if_empty( result['result'][subject_code]['quiz_avg'] ),
        ))

        cursor.execute("INSERT IGNORE INTO nilekrator$ADMIN.SUBJECTS VALUES('{code}','{name}')".format(
          code=subject_code,
          name=result['result'][subject_code]['subject']
        ))
    #insert student in DOWNLOADS -> 2017$UG_CS_2
    cursor.execute('''UPDATE nilekrator$ADMIN.DOWNLOADS SET count = CASE
                        WHEN INSTR(downloaded, "{download_name}") = 0 OR INSTR(downloaded, "{download_name}") IS NULL THEN count+1
                        ELSE count END,
                    percent=CASE
                        WHEN percent < 100 AND (INSTR(downloaded, "{download_name}") = 0 OR INSTR(downloaded, "{download_name}") IS NULL) THEN percent+1
                        ELSE percent END,
                    downloaded=CASE
                        WHEN downloaded IS NULL THEN "{download_name}"
                        WHEN INSTR(downloaded, "{download_name}") = 0 THEN CONCAT(downloaded,",{download_name}")
                        ELSE downloaded END
                    WHERE name="{year_and_roll}"'''.format(
            download_name=result['roll']+"@"+result['name'],
            year_and_roll=year+"$"+course+"_"+branch+"_"+result['semester']
        ))

    conn.commit()
    conn.close()
    result['database_save'] = True

    return result, 200

def return_zero_if_empty(string):
    if not string:
        return 0
    else:
        try:    # person may be absent so it is found that the table cell is filled with ABS references 2017ugpi042
            return float(string)
        except ValueError:
            return 0



################################################################## result fetcher ####################################################3
class Student:

  def __init__(self, roll, semester=None):
    self.roll = roll.upper()
    self.semester = semester
    self.url = 'http://14.139.205.172/web_new/Default.aspx'


  def parse_result_table(self,result_table):
    trs = result_table.find_all("table")[0].find_all("tr", recursive=False)[1:]

    result = OrderedDict()
    headers = ['', 'subject', 'test_1', 'test_2','assignment', 'quiz_avg', 'end_sem', 'total', 'grade']
    code = ''

    for tr in trs:
      tds = tr.find_all("td", recursive=False)
      for i,td in enumerate(tds):
        if i == 0:
          code = td.text.strip()
          result[code] = dict()
        else:
          result[code][headers[i]] = td.text.strip()

    return result

  def first_call_response(self):
    '''Returns an array of [ all semesters, next form data to post, status code ]'''

    post_data = {
      "ToolkitScriptManager1_HiddenField" :"",
      "__EVENTTARGET": "",
      "__EVENTARGUMENT": "",
      "__VIEWSTATE": "/wEPDwULLTE5MTk3NDAxNjkPZBYCAgMPZBYEAgMPFCsAAmQQFgAWABYAZAIqD2QWBAISDxQrAAJkZGQCFA9kFgICAw8UKwACZGRkGAMFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYEBQpidG5pbWdTaG93BRBidG5pbWdTaG93UmVzdWx0BQtidG5JbWdQcmludAUMYnRuaW1nQ2FuY2VsBQlsdkJhY2tsb2cPZ2QFEGx2U3ViamVjdERldGFpbHMPZ2RRUBQxFvIgVfx50k5f51Z0VJON3rlAmXJvDT2YJxv0oA==",
      "__VIEWSTATEGENERATOR" :"011071C8",
      "txtRegno": "{}".format(self.roll),
      "btnimgShow.x": str(random.randint(1, 99)),
      "btnimgShow.y": str(random.randint(1, 99)),
      "ddlSemester": "0",
      "hfldno": "",
      "hdfidno": ""
    }

    #first call data that is required
    # self.semester = []
    # form_var = {}

    req = request.urlopen(self.url, parse.urlencode(post_data).encode('utf-8'))
    resp = req.read().decode('utf-8')

    if "alert('Student Not Available or Result Yet not Published.')" in resp:
        return "", "", 404  # 404 status code for no content

    soup = BeautifulSoup(resp, 'lxml')
    semesters = soup.find_all("option", attrs={"value": re.compile(r'[123456789]')})
    semesters = [ sem['value'] for sem in semesters ]

    form_vars = [ "ToolkitScriptManager1_HiddenField", "__EVENTTARGET", "__EVENTARGUMENT",
    "__VIEWSTATE", "__VIEWSTATEGENERATOR", "hfIdno", "hdfidno" ]

    form_data = OrderedDict()

    for var in form_vars:
        try:
            form_data[var] = soup.find("input", attrs={"id": var})['value']
        except:
            form_data[var] = ""

    form_data["txtRegno"] = str(self.roll)
    form_data["btnimgShowResult.x"] = str(random.randint(1,100))
    form_data["btnimgShowResult.y"] = str(random.randint(1,100))
    form_data["ddlSemester"] = semesters

    return semesters, form_data, 200

    #second resquest for result
  def second_call_response(self, post_data):

    save_semester = post_data['ddlSemester']

    if self.semester != None:
        if self.semester not in save_semester:            # entered semeter is greater than available semesters
            return False
        post_data['ddlSemester'] = self.semester
    else:
        self.semester = post_data['ddlSemester'][-1]
        post_data['ddlSemester'] = self.semester           #for grabbing latest semester result

    try:
      req = request.urlopen(self.url, parse.urlencode(post_data).encode('utf-8'))
      resp = req.read().decode('utf-8')

      soup = BeautifulSoup(resp, 'lxml')

      student = OrderedDict()

      student['roll'] = soup.find('span',attrs={'id':'lblRollNo'}).text
      student['session'] = soup.find("span", attrs={"id": "lblsession"}).text
      student['degree'] = soup.find("span", attrs={"id": "lblDegreeName"}).text
      student['scheme'] = soup.find("span", attrs={"id": "lblSchemetype"}).text

      student['name'] = soup.find("span", attrs={"id": "lblStudentName"}).text
      student['branch'] = soup.find("span", attrs={"id": "lblBranchName"}).text
      student['semester'] = post_data['ddlSemester']
      student['all_semester'] = save_semester

      student['result_status'] = soup.find("span", attrs={"id": "lblResult"}).text
      student['sgpa'] = soup.find("span", attrs={"id": "lblSPI"}).text
      student['cgpa'] = soup.find("span", attrs={"id": "lblCPI"}).text

      student['publish_date'] = soup.find("span", attrs={"id": "lblPublishDate"}).text
      student['image_id'] = soup.find("input", attrs={"id": "hfIdno"})['value']

      student['result'] = self.parse_result_table(soup.find("div",attrs={"id": "PnlShowResult"}).find_all("tr")[5])
      student['given_roll'] = self.roll

      return student
    except:
      return False