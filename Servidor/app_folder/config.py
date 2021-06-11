##################################################################################################################################

"""
Archivo que guarda variables de configuración de la aplicación.
"""

class Config(object):

    DEBUG = False
    TESTING = False
    SECRET_KEY = "OCML3BRawWEUeaxcuKHLpw"
    MONGO_SERVICE = "local"
    DB_NAME = "production-db"
    DB_USERNAME = "root"
    DB_PASSWORD = "example"
    CONNECT: False
    
    MAX_CONTENT_LENGTH = 15000000

    SESSION_COOKIE_SECURE = True
    ALLOWED_FILE_EXTENSIONS = ["CSV","TXT","XLSX","VCF"]
    CLIENT_FILES = "/mnt/c/wsl/server/app_folder/app/client/"
    SERVER_FILES = "/mnt/c/wsl/server/app_folder/app/static/server/"
    LOG_FILES = "/mnt/c/wsl/server/app_folder/app/logs/"
    PICKLE_FILES = "/mnt/c/wsl/server/app_folder/app/pickles/"

    TMP_FILES = "/mnt/c/wsl/server/app_folder/app/static/tmp/"
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CORS_HEADERS = 'Content-Type'
    ADMIN_EMAIL = "admin@snptool.es"
    LOCALHOST = False

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

    DB_NAME = "development-db"
    DB_USERNAME = "root"
    DB_PASSWORD = "example"

    #SESSION_COOKIE_SECURE = False

class TestingConfig(Config):
    TESTING = True

    DB_NAME = "development-db"
    DB_USERNAME = "root"
    DB_PASSWORD = "example"

    #SESSION_COOKIE_SECURE = False

##################################################################################################################################
