import os

class Config:
    PROJECT_ID = os.getenv('PROJECT_ID', '183061022621')
    SECRET_MANAGER_PROJECT_ID = os.getenv('SECRET_MANAGER_PROJECT_ID', PROJECT_ID)

config = Config()
