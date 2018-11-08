from flask import Flask, request, json, render_template, make_response, session,redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_restful import marshal, fields
from flask_cors import CORS
from random import randint
import os
import jwt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Dewa626429@localhost:5432/Twitter'
app.config['SECRET_KEY'] = os.urandom(24)
CORS(app)
db = SQLAlchemy(app)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50))
    fullname = db.Column(db.String(200))
    email = db.Column(db.String())
    password = db.Column(db.String())
    bio = db.Column(db.String(100))
    photoprofile = db.Column(db.String())
    tweets = db.relationship('Tweets', backref='owner')


class Tweets(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(140))
    date = db.Column(db.DateTime(), default = datetime.datetime.utcnow)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    follow_person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    person = db.relationship("Person", foreign_keys=[person_id])
    follow_person = db.relationship("Person", foreign_keys=[follow_person_id])

@app.route('/signup', methods=['POST'])
def sign_up():
    if request.method == 'POST':

        request_data = request.get_json() # request yang masuk diubah jadi json
        # print(request_data)


        userDB = Person.query.filter_by(username=request_data.get('username')).first()
        if userDB is None:
            send_data = Person(
                username = request_data.get('username'),
                fullname = request_data.get('fullname'),
                email = request_data.get('email'),
                password = request_data.get('password'),
                bio = request_data.get('bio'),
                photoprofile = request_data.get('photoprofile')
            )

        
        # add request_data to db
            db.session.add(send_data)
            db.session.commit()

            respons = {
                'sukses': True,
                'message': 'Account has been created'
            }
            respons = json.dumps(respons)
            return respons, 200
        
        else:
            respons = {
                'sukses': False,
                'message': 'Username already exist'
            }
            respons = json.dumps(respons)
            return respons, 400
    else: # kalo method bukan post
        respons = {
                'sukses': False,
                'message': 'Method Not Allowed'
            }
        respons = json.dumps(respons)
        return respons, 405


@app.route('/login', methods = ['POST'])
def login():
    if request.method == 'POST':
        request_data = request.get_json()
        print(request_data)
        # check if username is exist in db
        req_username = request_data.get('username')
        req_password = request_data.get('password')
        userDB = Person.query.filter_by(username=req_username, password=req_password).first()
        print(userDB)
        
        if userDB is not None:  
            payload = {
                'username': userDB.username,
                'rahasia': 'secret'
            }        
            # print(payload)  
            encoded = jwt.encode(payload, 'lalala', algorithm='HS256')

            return encoded, 200
        else:
            respons = {
                'sukses': False,
                'message': 'Username and password did not match'
            }
            respons = json.dumps(respons)
            return respons, 404

    else:
        respons = {
                'sukses': False,
                'message': 'Method Not Allowed'
            }
        respons = json.dumps(respons)
        return respons, 405



# tweet routing
@app.route('/addTweet', methods = ['POST'])
def add_tweet():
    try:
        decoded = jwt.decode(request.headers["Authorization"], 'lalala', algorithms=['HS256'])
        if decoded['rahasia'] != 'secret':
            respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
            respons = json.dumps(respons)
            return respons, 400
    except jwt.exceptions.DecodeError:
        respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
        respons = json.dumps(respons)
        return respons, 400

    if request.method == 'POST':
        
        request_data = request.get_json()
        req_tweet = request_data.get('tweet')

        userDB = Person.query.filter_by(username = decoded['username']).first()

        if userDB is not None:
            tweet = Tweets(
                content = req_tweet,
                owner = userDB
            )
            db.session.add(tweet)
            db.session.flush()
            db.session.refresh(tweet)
            # print(tweet.id)
            db.session.commit()
            
            json_format = {
                'id' : tweet.id,
                'content': tweet.content,
                'date': tweet.date,
                'username' : userDB.username,
                'fullname' : userDB.fullname,
                'photoprofile': userDB.photoprofile
            }
            respons = {
                'sukses': True,
                'message': 'Tweet added',
                'data': json_format
            }
            respons = json.dumps(respons)
            
            return respons, 201
        else:
            respons = {
                'sukses': False,
                'message': 'You have to logged in',
            }
            respons = json.dumps(respons)
            return respons, 400

    else:
        respons = {
                'sukses': False,
                'message': 'Method Not Allowed',
            }
        respons = json.dumps(respons)
        return respons, 405


# get tweet routing
@app.route('/getTweet', methods = ['GET','POST'])
def get_tweet():

    try:
        decoded = jwt.decode(request.headers["Authorization"], 'lalala', algorithms=['HS256'])
        if decoded['rahasia'] != 'secret':
            respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
            respons = json.dumps(respons)
            return respons, 400
    except jwt.exceptions.DecodeError:
        respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
        respons = json.dumps(respons)
        return respons, 400
#     select follow.person_id as follower_person_id, follow.follow_person_id as following_person_id,
# person.username as following_username, person.fullname as following_username, person.photoprofile as following_profile,
# tweets.id as tweet_id, tweets.content as tweet_content, tweets.date as tweet_data
# from follow inner join person on person.id = follow.follow_person_id 
# inner join tweets on tweets.person_id = follow.follow_person_id 
# where follow.person_id = 10

    userDB = Tweets.query.join(Person, Person.id == Tweets.person_id).add_columns(Tweets.id, Tweets.content, Tweets.date, Person.username, Person.fullname, Person.photoprofile, Person.id).order_by(Tweets.date)
    # users.query.join(friendships, users.id==friendships.user_id).add_columns(users.userId, users.name, users.email, friends.userId, friendId)
    user_tweets = []

    for data in userDB:
        test = {
            'id': data[1],
            'content': data[2],
            'date': data[3],
            'username': data[4],
            'fullname': data[5],
            'photoprofile': data[6],
            'personId': data[7]
            }
        user_tweets.append(test)
        # print(data.id)
    # conver to JSON
    # print(user_tweets)
    json_format = {
        'id' : fields.Integer,
        'content': fields.String,
        'date': fields.DateTime,
        'username' : fields.String,
        'fullname' : fields.String,
        'photoprofile': fields.String,
        'personId' : fields.Integer
    }
    
    tweet_json = marshal(user_tweets, json_format)

    respons = {
        'sukses': False,
        'message': 'You have to logged in',
        'data': tweet_json
    }
    respons = json.dumps(respons)
    
    # print(tweet_json)
    return respons, 200



@app.route('/user', methods = ['GET', 'POST'])
def show_user():
    try:
        decoded = jwt.decode(request.headers["Authorization"], 'lalala', algorithms=['HS256'])
        if decoded['rahasia'] != 'secret':
            respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
            respons = json.dumps(respons)
            return respons, 400
    except jwt.exceptions.DecodeError:
        respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
        respons = json.dumps(respons)
        return respons, 400
    req_data = request.get_json()
    id = req_data.get('id')
    print(id)
    user = Person.query.filter_by(id = id).first()
    # print(user.tweets)
    
    # print(user_tweets)
    # tweet = Tweets.query.join(Person, Tweets.person_id == id).add_columns(Tweets.id, Tweets.content, Tweets.date, Person.username, Person.fullname, Person.photoprofile).order_by(Tweets.date)
    if request.method == 'POST':
        user_tweets = []
        for data in user.tweets:
            json_format = {
                'id' : data.id,
                'content': data.content,
                'date': data.date,
                'username': user.username,
                'fullname': user.fullname,
                'photoprofile' : user.photoprofile
            }
            user_tweets.append(json_format)


        # conver to JSON
        respons = {
                'sukses': True,
                'message': 'Here your tweets',
                'data': user_tweets
            }
        respons = json.dumps(respons)
        
        return respons, 200
    else:
        respons = {
                'sukses': False,
                'message': 'Method not allowed'
            }
        respons = json.dumps(respons)
        return respons, 400

# get accoun data for edit route
@app.route('/getdata', methods = ['GET', 'POST'])
def get_account_data():
    # request_data = request.get_json()
    # username = request_data.get('username')
    try:
        decoded = jwt.decode(request.headers["Authorization"], 'lalala', algorithms=['HS256'])
        if decoded['rahasia'] != 'secret':
            respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
            respons = json.dumps(respons)
            return respons, 400
    except jwt.exceptions.DecodeError:
        respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
        respons = json.dumps(respons)
        return respons, 400
    userDB = Person.query.filter_by(username = decoded['username']).first()
    json_format = {
        'id' : fields.Integer,
        'username': fields.String,
        'fullname' : fields.String,
        'email' : fields.String,
        'bio' : fields.String,
        'photoprofile' : fields.String
    }
    user_json = marshal(userDB, json_format)

    respons = {
            'sukses': True,
            'message': 'Succes',
            'data': user_json
        }
    respons = json.dumps(respons)
    return respons, 200


# editig route
@app.route('/editprofile', methods = ['PUT'])
def edit_profile():
    request_data = request.get_json()
    # print(request_data)
    # req_username = request_data.get('username')
    try:
        decoded = jwt.decode(request.headers["Authorization"], 'lalala', algorithms=['HS256'])
        if decoded['rahasia'] != 'secret':
            respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
            respons = json.dumps(respons)
            return respons, 400
    except jwt.exceptions.DecodeError:
        respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
        respons = json.dumps(respons)
        return respons, 400
    # new data
    username = request_data.get('username')
    fullname = request_data.get('fullname')
    email = request_data.get('email')
    bio = request_data.get('bio')
    photoprofile = request_data.get('photoURL')
    # userDB = Person.query.filter_by(username = req_username).first()
    # print(username,fullname)
    # print(type(userDB))
    # return 'ok', 200

    if request.method == 'PUT':
        userDB = Person.query.filter_by(username = username).first()
        # print(userDB.username)
        userDB.username = username
        userDB.fullname = fullname
        userDB.email = email
        userDB.bio = bio
        userDB.photoprofile = photoprofile
        
        db.session.commit()
        respons = {
                'sukses': True,
                'message': 'Data has been edited'
            }
        respons = json.dumps(respons)
        return respons, 200
    else:
        respons = {
                'sukses': False,
                'message': 'Method not Allowed'
            }
        respons = json.dumps(respons)
        return respons, 400

# password change route
@app.route('/passchange', methods = ['PUT'])
def change_pass():
    try:
        decoded = jwt.decode(request.headers["Authorization"], 'lalala', algorithms=['HS256'])
        if decoded['rahasia'] != 'secret':
            respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
            respons = json.dumps(respons)
            return respons, 400
    except jwt.exceptions.DecodeError:
        respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
        respons = json.dumps(respons)
        return respons, 400
    request_data = request.get_json()
    req_username = decoded['username']
    req_password = request_data.get('password')

    # new data
    new_password = request_data.get('newPassword')
    verify_new_password = request_data.get('rePassword')
    print(req_password, new_password, verify_new_password)
    if new_password == req_password or req_password == verify_new_password:
        respons = {
                'sukses': False,
                'message': 'Password must be diffrent from previous'
            }
        respons = json.dumps(respons)
        return respons, 400

    if request.method == 'PUT':
        userDB = Person.query.filter_by(username=req_username, password=req_password).first()
        if userDB is not None and new_password == verify_new_password:
            userDB.password = new_password
        else:
            respons = {
                'sukses': False,
                'message': 'Wrong password'
            }
            respons = json.dumps(respons)
            return respons, 404
        
        db.session.commit()
        respons = {
            'sukses': True,
            'message': 'Data has been edited'
        }
        respons = json.dumps(respons)
        return respons, 200
    else:
        respons = {
            'sukses': False,
            'message': 'Method not Allowed'
        }
        respons = json.dumps(respons)
        return respons, 400

# Delete tweet routing
@app.route('/deleteTweet', methods = ['DELETE'])
def delete_tweet():
    try:
        decoded = jwt.decode(request.headers["Authorization"], 'lalala', algorithms=['HS256'])
        if decoded['rahasia'] != 'secret':
            respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
            respons = json.dumps(respons)
            return respons, 400
    except jwt.exceptions.DecodeError:
        respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
        respons = json.dumps(respons)
        return respons, 400

    currentUser = Person.query.filter_by(username = decoded['username']).first()
    request_data = request.get_json()
    # print(request_data)
    tweet_id = request_data.get('tweet_id')
    tweet = Tweets.query.filter_by(id = tweet_id).first()
    if currentUser.id != tweet.person_id:
        return 'You cant delete this tweet', 400
    # print(tweet_id)
    if request.method == 'DELETE':
        # tweet = Tweets.query.filter_by(id= tweet_id).first()
        db.session.delete(tweet)
        db.session.commit()

        id = "tweet"+str(tweet_id)
        respons = {
                'sukses': True,
                'message': 'Tweet Deleted',
                'data': id
            }
        respons = json.dumps(respons)
        return respons, 201

# display who to follow route
@app.route('/showsuggestion', methods = ['GET', 'POST'])
def show_suggestion():
    try:
        decoded = jwt.decode(request.headers["Authorization"], 'lalala', algorithms=['HS256'])
        if decoded['rahasia'] != 'secret':
            respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
            respons = json.dumps(respons)
            return respons, 400
    except jwt.exceptions.DecodeError:
        respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
        respons = json.dumps(respons)
        return respons, 400
    # request_data = request.get_json()
    # print(request_data)
    # username = request_data.get('username')
    # print(username)
    userDB = Person.query.filter(Person.username != decoded['username']).all()
    # print(userDB)
    current = []
    suggestion = []
    i = 0
    if request.method == 'POST':
        while i < 3:
            index = randint(0, (len(userDB)-1))
            if index in current:
                continue
            # print(index)
            current.append(index)
            suggestion.append(userDB[index])
            i += 1
        # print(suggestion)
        json_format = {
                'id' : fields.Integer,
                'username': fields.String,
                'fullname' : fields.String,
                'photoprofile' : fields.String
            }
        
        user_json = marshal(suggestion, json_format)
        # print(user_json)
        respons = {
                'sukses': True,
                'message': 'Succes',
                'data' : user_json
            }
        respons = json.dumps(respons)
        return respons, 200   
    else:
        respons = {
                'sukses': False,
                'message': 'Method not Allowed'
            }
        respons = json.dumps(respons)
        return respons , 400



# follow other user route
@app.route('/follow', methods = ['PUT'])
def follow():
    try:
        decoded = jwt.decode(request.headers["Authorization"], 'lalala', algorithms=['HS256'])
        if decoded['rahasia'] != 'secret':
            respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
            respons = json.dumps(respons)
            return respons, 400
    except jwt.exceptions.DecodeError:
        respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
        respons = json.dumps(respons)
        return respons, 400
    request_data = request.get_json()
    

    user = Person.query.filter_by(username = decoded['username']).first()
    userID = user.id

    followID = request_data.get('followID')
    if request.method == 'PUT':
        followDB = Follow.query.filter_by(person_id = userID, follow_person_id = followID).first()

        if followDB is None:
            send_data = Follow(
                person_id = userID,
                follow_person_id = followID
            )
    
            # add request_data to db
            db.session.add(send_data)
            db.session.commit()
            respons = {
                    'sukses': True,
                    'message': 'Success'
                }
            respons = json.dumps(respons)
            return respons, 200
        
        else:
            respons = {
                    'sukses': False,
                    'message': 'Bad Request'
                }
            respons = json.dumps(respons)
            return respons, 400
    else:
        respons = {
                'sukses': False,
                'message': 'Method not Allowed'
            }
        respons = json.dumps(respons)
        return respons, 400


# show status user route
@app.route('/showstats', methods = ['GET','POST'])
def show_status():
    try:
        decoded = jwt.decode(request.headers["Authorization"], 'lalala', algorithms=['HS256'])
        if decoded['rahasia'] != 'secret':
            respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
            respons = json.dumps(respons)
            return respons, 400
    except jwt.exceptions.DecodeError:
        respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
        respons = json.dumps(respons)
        return respons, 400

    user = Person.query.filter_by(username = decoded['username']).first()
    following = Follow.query.filter_by(person_id = user.id).count()
    followers = Follow.query.filter_by(follow_person_id = user.id).count()
    tweets = Tweets.query.filter_by(person_id = user.id).count()
    if request.method == 'POST':
        json_format = {
            'id' : user.id,
            'fullname' : user.fullname,
            'username' : user.username,
            'photoprofile': user.photoprofile,
            'tweets' : tweets,
            'following': following,
            'followers' : followers,
            'bio' : user.bio
        }

        respons = {
                'sukses': True,
                'message': 'Succes',
                'data': json_format
            }
        respons = json.dumps(respons)
        print(respons)
        return respons, 200
    else:
        respons = {
                'sukses': False,
                'message': 'method not allowed'
            }
        respons = json.dumps(respons)
        return respons , 400


# show trending tweets route
@app.route('/trending', methods = ['GET','POST'])
def show_trending():
    try:
        decoded = jwt.decode(request.headers["Authorization"], 'lalala', algorithms=['HS256'])
        if decoded['rahasia'] != 'secret':
            respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
            respons = json.dumps(respons)
            return respons, 400
    except jwt.exceptions.DecodeError:
        respons = {
                'sukses': False,
                'message': 'You have to logged in'
            }
        respons = json.dumps(respons)
        return respons, 400
    
    tweet = Tweets.query.all()
    content = ""
    for data in tweet:
        content += " " + data.content
    content = content.split()
    trending = {}
    for data in content:
        if data in trending:
            trending[data] += 1
        else:
            trending[data] = 1
    ascending = []
    for data in trending:
        if ascending == []:
            ascending.append(data)
            continue
        if trending[data] > trending[ascending[0]]:
            ascending.insert(0,data)
        else:
            ascending.append(data)
        if len(ascending) > 10:
            ascending.pop()
    final = {}
    for data in ascending:
        final[data] = trending[data]
    
    # print(trending)
    respons = {
            'sukses': True,
            'message': 'Success',
            'data': final
        }
    respons = json.dumps(respons)
    # print(respons)
    return respons, 200

########################
###### SESSION##########
########################
# set session buat dapet session di browser
# @app.route('/setsession/<username>')
# def set_session(username):
#     session['username'] = username
#     print(session['username'])
#     return 'session has been set', 200

# @app.route('/readsession')
# def read_session():
#     if 'username' in session:
#         return 'Session ' + session['username'] + ' exist'
#     else:
#         return 'Session does not exist, Log in first'

# @app.route('/dropsession')
# def drop_session():
#     session.pop('username', None)
#     return 'Session has been dropped'




########################
####### COOKIE #########
########################
# @app.route('/setcookie')
# def set_cookie(username):
#     # username = 'abaddon'
#     resp = make_response('')
#     resp.set_cookie('username', username)
#     return resp

# @app.route('/readcookie')
# def read_cookie():
#     cookie = request.cookies.get('username')
#     return 'The cookie is' + cookie, 200


if __name__ == '__main__':
    app.run(debug=True)
