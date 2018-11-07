from flask import Flask, jsonify, request
from resources.tweetUser import users_api
from flask_cors import CORS
import os
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired
from flask_restful import marshal, fields
import json

POSTGRES = {
    'user': 'postgres',
    'pw': 'Dewa626429',
    'db': 'Twitter',
    'host': 'localhost',
    'port': '5432'
}

# print()
app = Flask(__name__)
CORS(app)
app.register_blueprint(users_api, url_prefix = '/api/')

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

app.config.update(dict(
    SECRET_KEY = 'bebas',
    WTF_CSRF_SECRET_KEY = 'apa aja'
))

db = SQLAlchemy(app)

# class untuk nge-Get
class Twitter(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String())
    fullname = db.Column(db.String())
    email = db.Column(db.String())
    pw = db.Column(db.String())
    tweet = db.Column(db.String())

    def __init__(self, username, fullname, email, pw, tweet):
        self.username = username
        self.fullname = fullname
        self.email = email
        self.pw = pw
        self.tweet = tweet

# class untuk nge-post
class PostForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    fullname = StringField('Fullname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    pw = StringField('pw', validators=[DataRequired()])
    tweet = StringField('Tweet', validators=[DataRequired()])


tweet_json = {
    'id' : fields.Integer,
    'username' : fields.String,
    'fullname' : fields.String,
    'email' : fields.String,
    'pw' : fields.String,
    'tweet' : fields.String
}

@app.route('/getTweet')
def get_tweet():
    tweet = Twitter.query.all()
    # print(json.dump(marshal(tweet, tweet_json)))
    # print(json.dumps(marshal(tweet, tweet_json)))
    return json.dumps(marshal(tweet, tweet_json)), 200

@app.route('/postTweet', methods = ['GET', 'POST'])
def post_tweet():
    addtweet = PostForm()
    if request.method == 'POST':
        at = Twitter(
            addtweet.username.data,
            addtweet.fullname.data,
            addtweet.email.data,
            addtweet.pw.data,
            addtweet.tweet.data
        )
        db.session.add(at)
        db.session.commit()
        print(request.get_json())
        return 'mantap', 200
    else:
        return 'ahahaha', 400

@app.route('/')
def test():
    cwd = os.getcwd()  # Get the current working directory (cwd)
    files = os.listdir(cwd)  # Get all the files in that directory
    print()
    return "Files in '%s': %s" % (cwd, files)

if __name__ == '__main__':    app.run(debug=True)