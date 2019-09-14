from config import config
from extensions import mysql
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object(config['production'])

    from scraper.student_api import api_bp
    from scraper.scrape import scraper
    from student.student import student
    from student.college import college
    
    app.register_blueprint(api_bp)
    app.register_blueprint(scraper)
    app.register_blueprint(student)
    app.register_blueprint(college)

    mysql.init_app(app)

    return app
