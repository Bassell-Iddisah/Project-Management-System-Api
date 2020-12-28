from datetime import timedelta


class Config:
    APP_NAME = 'Nifty Global Systems Apps'
    APP_LESS_NAME = 'ngsapps'
    DEBUG = True
    ENV = 'development'
    SECRET_KEY = 'a9a3c143b9dac091f39ce0d89ba0607ad31a64249582ec0ba0'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost/ngsapps'
    MAIL_SERVER = 'mail.hrm.portalsgh.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = '_mainaccount@hrm.portalsgh.com'
    MAIL_PASSWORD = 'apana1jude1'
    MAIL_DEFAULT_SENDER = 'noreply.portalsgh@portalsgh.com'
    PAGINATE_PAGE_SIZE = 10
    PAGINATE_RESOURCE_LINKS_ENABLED = True
    JWT_SECRET_KEY = 'a9a3c143b9dac091f39ce0d89ba0607ad31a64249582ec0ba'
    # JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=120)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=120)
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = False
    JWT_CSRF_CHECK_FORM = False


class DevelopmentConfig(Config):
    pass


class ProductionConfig(Config):
    JWT_COOKIE_SECURE = True
