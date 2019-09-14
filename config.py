import re
import os

class Config(object):
    DEBUG = False
    TESTING = False
    MYSQL_DATABASE_HOST = os.environ['MYSQL_DATABASE_HOST']
    MYSQL_DATABASE_USER = os.environ['MYSQL_DATABASE_USER']
    MYSQL_DATABASE_PASSWORD = os.environ['MYSQL_DATABASE_PASSWORD']
    SECRET_KEY = os.environ['SECRET_KEY']

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

config = {
    "development": "config.DevelopmentConfig",
    "production": "config.ProductionConfig",
    "testing": "config.TestingConfig",
}


def parse_roll(roll):
    if 'TYC' in roll:
        year = '20'+roll[3:5]
        course = 'TYC'
        branch = re.sub(r'\d+', '',roll[5:]).upper()
        # roll = re.search(r'\d+$', roll[5:])
    else:
        year = roll[:4]
        course = roll[4:6]
        branch = re.sub(r'\d+$', '', roll[6:])
        # roll = re.search(r'\d+$', roll[6:])

    return year, course, branch