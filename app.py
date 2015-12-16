from flask import Flask
from flask.ext.runner import Runner

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
runner = Runner(app)

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)

if __name__=='__main__':
    runner.run()

