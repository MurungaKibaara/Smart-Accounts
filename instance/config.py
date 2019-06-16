'''App Configurations'''
import os

class Config(object):
    """Main Configurations"""
    DEBUG = False
    SECRET_KEY = '\xd8$\x12\xe2@\xf5\x04' #Generated using os.urandom(24)

class DevelopmentConfig(Config):
    """Development Configurations"""
    DEBUG = True
    DATABASE_NAME = "smartaccounts"
    DATABASE_URL = os.getenv("DATABASE")

class ProductionConfig(Config):
    """Production Configurations"""
    DEBUG = False
    TESTING = False


APP_CONFIG = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
