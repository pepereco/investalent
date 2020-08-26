from decouple import config

class Config:
    SECRET_KEY='superyoyO1525'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:superyoyO1525@localhost/investalent2'
    SQLALCHEMY_TRACK_MODIFICATIONS= False

    MAIL_SERVER = 'smtp.googlemail.com'
    LOCAL_SERVER = 'http://127.0.0.1:5000'
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USERNAME= 'peperecolons0@gmail.com'
    MAIL_PASSWORD='1525superyoyO1525'#MAIL_PASSWORD #OS

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:superyoyO1525@localhost/test'
    SQLALCHEMY_TRACK_MODIFICATIONS= False
    TEST=True

config = {
    'developmement': DevelopmentConfig(),
    'default': DevelopmentConfig(),
    'test': TestConfig
}
