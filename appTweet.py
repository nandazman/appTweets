from flask import Flask
from resources.tweetUser import users_api
import os


# print()
app = Flask(__name__)
app.register_blueprint(users_api, url_prefix = '/api/')


@app.route('/')
def test():
    cwd = os.getcwd()  # Get the current working directory (cwd)
    files = os.listdir(cwd)  # Get all the files in that directory
    print()
    return "Files in '%s': %s" % (cwd, files)

if __name__ == '__main__':    app.run(debug=True)