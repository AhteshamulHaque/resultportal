from flask import Blueprint, request, make_response, render_template
from scraper.config import BRANCH_NAME
from extensions import mysql
from random import randint

scraper = Blueprint('scraper', __name__)

DOMAIN_NAME = 'https://nilekrator.pythonanywhere.com/'

def auth_required(f):
    def decorated(*args, **kwargs):
        auth = request.authorization

        if auth and auth.username == 'nile' and auth.password == "krator":
          return f(*args, *kwargs)
        return make_response("Could not verify admin", 401, {"WWW-Authenticate": 'Basic realm="Admin Login Required"'})
    return decorated


# renders the download page....actual download is at endpoint /download/<year>/<batch>
@scraper.route("/downloader")
@auth_required
def downloader():
    conn = mysql.connect()
    cursor = conn.cursor()

    # info of downloaded and not downloaded semesters and their student results
    cursor.execute("SELECT * FROM nilekrator$ADMIN.DOWNLOADS")

    download_info = cursor.fetchall()

    return render_template("scraper/scraper.html", title="Web Scraper", branch_name_map=BRANCH_NAME, download_info=download_info, random=randint(1, 10000000))
