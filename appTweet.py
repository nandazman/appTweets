from flask import Flask
from resources.tweetUser import users_api
# print()
app = Flask(__name__)
app.register_blueprint(users_api, url_prefix = '/api/')


@app.route('/')
def test():
    return "<h1>MANTAP</h1><h2>port: 5000 </h2>"

if __name__ == '__main__':
    app.run(debug=True)