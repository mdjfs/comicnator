class Config(object):
    SECRET_KEY = "my_secret_key"


class DevelopmentConfig(Config):
    DEBUG = True
    address = "postgresql://marcos:Golf45@localhost:5432/ComicNator"
    SQLALCHEMY_DATABASE_URI = address
    SQLALCHEMY_TRACK_MODIFICATIONS = False
