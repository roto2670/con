class Config(object):
    SECRET_KEY = 'key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FIREBASE_API_KEY = 'AIzaSyANO3vuNoPC1eQjqsIJeZzGZhl1gWAPbro'
    FIREBASE_PROJECT_ID = 'console-4196c'
    FIREBASE_AUTH_SIGN_IN_OPTIONS = 'email,google'
    LOG_PATH = '/tmp/console.log'
    LOG_BACKUP_COUNT = 10
    LOG_MAX_BYTES = 10485760

class ProductionConfig(Config):
    DEBUG = False


class DebugConfig(Config):
    DEBUG = True
