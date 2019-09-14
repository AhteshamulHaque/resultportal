import pymysql as mysql
from urllib.request import urlopen
import time, json
import logging

DATABASE_HOST = "nilekrator.mysql.pythonanywhere-services.com"
DATABASE_USER = "nilekrator"
DATABASE_PASSWD = "Haque8900@"

UG_courses = ["CS", "EC", "EE", "MM", "ME", "CE", "PI"]

PG_courses = [
                "CACA", "CHCH", "MHMH", "PHPH", "MMFT",
                "MMMT", "CSCS", "CAIS", "METE", "MEES",
                "MECI", "MFMS", "CHSS", "CESE", "CEGE",
                "CEWR", "EEPE", "EEPS", "ECEM", "ECCO",
            ]

TYC_courses = [ "MME" ]

DOMAIN_NAME = 'https://nilekrator.pythonanywhere.com/'

def create_database_schema():

    initial = time.time()

    conn = mysql.connect(DATABASE_HOST, DATABASE_USER, DATABASE_PASSWD)
    cursor = conn.cursor()

    # Try to create admin database
    cursor.execute("CREATE DATABASE IF NOT EXISTS nilekrator$ADMIN")

    cursor.execute("CREATE TABLE IF NOT EXISTS nilekrator$ADMIN.FEEDBACK(roll varchar(30), problem text)")
    cursor.execute("CREATE TABLE IF NOT EXISTS nilekrator$ADMIN.IP_TABLE(roll varchar(30), ipaddr varchar(50) PRIMARY KEY)")
    # Try to create admin.download table
    cursor.execute('''CREATE TABLE IF NOT EXISTS nilekrator$ADMIN.DOWNLOADS (
          name varchar(15) PRIMARY KEY,
          percent int(3) DEFAULT 0,
          completed int(1) DEFAULT 0,
          count int(3) DEFAULT 0,
          downloaded text
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS nilekrator$ADMIN.USERS (
          roll varchar(20) PRIMARY KEY,
          name varchar(70),
          image_id varchar(50) DEFAULT '/static/images/placeholder.png',
          rank int DEFAULT 0
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS nilekrator$ADMIN.SUBJECTS (
          subject_code varchar(20) PRIMARY KEY,
          subject_name text
    )''')

    cursor.execute("CREATE DATABASE IF NOT EXISTS nilekrator$CREDITS")

    ##################################### Loggers ########################################################
    logger = logging.getLogger()

    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    streamHandler.setFormatter( logging.Formatter('%(levelname)s : %(lineno)d : %(message)s') )

    logger.addHandler(streamHandler)
    # Get roll which has been already downloaded ...ignore them

    # Create conf and semester table of UG and PG courses
    for year in range(2015, 2019):

        fileHandler = logging.FileHandler(str(year)+'.log', 'w')
        fileHandler.setLevel(logging.WARNING)
        fileHandler.setFormatter( logging.Formatter('%(levelname)s : %(lineno)d : %(message)s') )
        logger.addHandler(fileHandler)

        logger.warning("\nYEAR :"+str(year)+"\n")

        year = str(year)

        cursor.execute("CREATE DATABASE IF NOT EXISTS nilekrator$_"+year)

        # CONF table creation
        cursor.execute("CREATE TABLE IF NOT EXISTS nilekrator$_"+year+".CONF"+ '''(
              name varchar(20) PRIMARY KEY,
              session varchar(15),
              publish_date varchar(10),
              semesters varchar(10),
              scheme varchar(10),
              degree varchar(15)
        )''')

        # schema of table for UG and PG courses
        for course, branches in [ ("UG", UG_courses), ("PG", PG_courses) ,("TYC", TYC_courses)]:
            for branch in branches:

                for retry in range(1, 6):      # retry 5 times for any hit

                    # request is made for determining the new semesters
                    try: # try inserted because error 404 halts all further requests for /schema endpoint, which stops the database creation
                        if course == "UG":    # because ug roll has three letters      #turn out 2017UGME001
                            stu = year+course+branch+"00"+str(retry)

                        elif course == "TYC":
                            stu =course+year[2:]+branch+"0"+str(retry)

                        else:   # because pg rolls have two letters (less student) # turn out 2016PGCACA02
                            stu = year+course+branch+"0"+str(retry)

                        logger.warning("Trying student "+stu)
                        req = urlopen(DOMAIN_NAME+'student/'+stu)

                        if req.code == 400:
                            raise ValueError("404 Not Found")

                    except Exception as e:
                        logger.warning("Can't download "+stu)
                        logger.warning("Reason : "+e.__str__())
                        continue

                    if int(req.code) == 200:    #may happen first roll is not present, hence the if statement

                        ############################################### UPDATE CONF TABLE FOR NEW SEMESTERS ###################################
                        # Get the semesters for which table to be created
                        result = json.loads( req.read().decode('utf-8') )
                        semesters = result['all_semester']

                        cursor.execute("SELECT semesters FROM nilekrator$_{year}.CONF WHERE name='{course}_{branch}'".format(
                          year=year,
                          course=course,
                          branch=branch
                        ))

                        res = cursor.fetchone()

                        if res:
                          logger.warning("Entry in nilekrator$_{}.CONF found for {}_{}".format(year, course, branch))
                          prev_sems = res[0].split(',') # prev semesters stored in a table

                          logger.warning("Sems scraped: "+str(semesters))
                          logger.warning("Previous Sems: "+str(prev_sems))

                          updated_sems = list(set(prev_sems).union(set(semesters))) # union of both the sems this will be inserted back in database
                          updated_sems.sort()

                          logger.warning("Updated Sems: "+ str(updated_sems))
                          semesters = list(set(semesters)-set(prev_sems)) # these are left out semesters whose schema is to be defined

                          logger.warning("Sems to be requested: "+str(semesters))
                          # update conf table with UG_CS for  extraction of semester for further easy processing (used for without user interaction)
                          try:
                            cursor.execute("UPDATE nilekrator$_{year}.CONF SET semesters='{semesters}', degree='{degree}' WHERE name='{course}_{branch}'".format(
                              year=year,
                              semesters=",".join(updated_sems),
                              course=course,
                              degree=result['degree'],
                              branch=branch
                            ))
                          except Exception as e:
                            logger.warning( 'Update in nilekrator$_{}.CONF failed for {}_{}'.format(year,course,branch) )
                            logger.warning('Reason: '+e.__str__())

                        else:
                          logger.warning("No entry found in nilekrator$_{}.CONF table for {}_{}".format(year, course, branch))
                          logger.warning("Inserting new one..")
                          try:
                            cursor.execute("INSERT INTO nilekrator$_"+year+".CONF VALUES('{course}_{branch}', NULL, NULL,'{semesters}', NULL, '{degree}')".format(
                                course=course,
                                branch=branch,
                                semesters=",".join(semesters),
                                degree=result['degree']
                            ))
                          except Exception as e:
                            logger.warning( 'Insert failed for nilekrator$_{}.{}_{}'.format(year,course,branch) )
                            logger.warning("REASON:", e.__str__())


                        ############################################### UPDATE CONF TABLE FOR NEW SEMESTERS ###################################
                        # Now create table eg: UG_CS_*, PG_PHPH_* in the _year named database
                        for semester in semesters:
                            # this code inserts the name of every branch in the admin table for downloading from the scraper Page

                                                                                            # turns to _2016$UG_CS_3
                          logger.warning("Inserting data "+year+"$"+course+"_"+branch+"_"+semester+" in DOWNLOADS")
                          cursor.execute( "INSERT IGNORE INTO nilekrator$ADMIN.DOWNLOADS(name) VALUES('"+year+"$"+course+"_"+branch+"_"+semester+"')" )

                          # student table for                                 truns out _2016.UG_CS_3
                          logger.warning("Creating table nilekrator$_"+year+"."+course+"_"+branch+"_"+semester)
                          cursor.execute("CREATE TABLE IF NOT EXISTS nilekrator$_"+year+"."+course+"_"+branch+"_"+semester+'''(
                                roll varchar(20) PRIMARY KEY,
                                cgpa float(5, 2),
                                sgpa float(5, 2),
                                result_status enum('PASS', 'FAIL')
                          )''')
                          #table holding result of students of above table        turns out RESULT_UG_CS_2
                          logger.warning("Creating table  nilekrator$_"+year+".RESULT_"+course+"_"+branch+"_"+semester)
                          cursor.execute('''CREATE TABLE IF NOT EXISTS nilekrator$_{year}.RESULT_{course}_{branch}_{semester} (
                            roll varchar(20),
                            subject_code varchar(10),
                            end_sem float(5, 2),
                            test_1 float(5, 2),
                            test_2 float(5, 2),
                            grade varchar(7),
                            total float(5, 2),
                            assignment float(5, 2),
                            quiz_avg float(5, 2),             -- truns out _2016.UG_CS_2
                            FOREIGN KEY (roll) REFERENCES nilekrator$_{year}.{course}_{branch}_{semester}(roll) ON DELETE CASCADE
                          )'''.format(year=year, course=course, branch=branch, semester=semester))

                        # break       # break if any try succeeds

                        logger.warning('All required table for {course}_{branch} with {semesters} created'.format(
                          course=course,branch=branch,semesters=str(semesters)
                        ))
                    cursor.execute('''CREATE TABLE IF NOT EXISTS nilekrator$CREDITS.{}_{} (
                          subject_code varchar(10),
                          credits int(1)
                        )'''.format(course,branch))

        logger.removeHandler(fileHandler)

    final = time.time()
    # also include here credits manually
    conn.commit()
    conn.close()
    print("Database initialised successfully. Took "+str((final-initial)/60)+" mins")

if __name__ == '__main__':
    create_database_schema()