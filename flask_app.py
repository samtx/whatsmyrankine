from flask import Flask
from flask.ext.runner import Runner
import os
from app import app

#app.config.from_object(os.environ['APP_SETTINGS'])
runner = Runner(app)

#print(os.environ['APP_SETTINGS'])

if __name__=='__main__':
    runner.run()

