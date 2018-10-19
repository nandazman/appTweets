from flask import Flask, jsonify, Blueprint, request
from flask_restful import Resource, Api, reqparse, inputs, abort
from datetime import datetime
import json

with open('C:/Users/NFA\Desktop/python/Latian REST API/TweetApp/users.json') as data_file:
    users = json.load(data_file)
    data_file.close()
with open('C:/Users/NFA\Desktop/python/Latian REST API/TweetApp/tweets.json') as data_file:
    tweets = json.load(data_file)
    data_file.close()

def updateDataUser(users):
    with open('users.json','w') as file:
            file.write(json.dumps(users))
            file.close()

def updateDataTweet(tweets):
    with open('tweets.json','w') as file:
            file.write(json.dumps(tweets))
            file.close()
    return
# users = [{
#     "username": "John",
#     "email": "john@haha.com",
#     "password": "Hahaha123",
#     "fullname": "John rukmana"
# },
# {
#     "username": "jeff",
#     "email": "jeff@haha.com",
#     "password": "Hahaha123",
#     "fullname": "John rukmana"
# }]

# tweets = [{
#     "email": "john@haha.com",
#     "tweet": "Ini bukan facebook"
# },
# {
#     "email": "jeff@haha.com",
#     "tweet": "Ini adalah tweet"
# }]



class data(Resource):
    def get(self):
        return users

class LogIn(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            "email",
            help = "Masukan email anda",
            required = True,
            location = ['json']
        )
        self.reqparse.add_argument(
            "password",
            help = "Masukan password anda",
            required = True,
            location = ['json']
        )
    
    def post(self):
        req = request.json
        args = self.reqparse.parse_args()
        for user in users:
            if user['email'] == req['email'] and user['password'] == req['password']:
                return user
        
        return {'message': 'email dan password tidak cocok'}, 404

def nameOrEmailAlreadyExisted(name,email):
    for user in users:
        if user['username'] == name or user['email'] == email:
            abort(400, message = "username atau email sudah dipakai")
    return name,email

class SignUp(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            "email",
            help = "Masukan email anda",
            required = True,
            location = ['json']
        )
        self.reqparse.add_argument(
            "password",
            help = "Masukan password anda",
            required = True,
            location = ['json']
        )
    
    def post(self):
        req = request.json
        args = self.reqparse.parse_args()
        nameOrEmailAlreadyExisted(req['username'],req['email'])
        users.append(req)
        updateDataUser(users)
        return req

def checkEmail(email):
    for user in users:
        if user['email'] == email:
            return email
    
    abort(400, message = "email tidak terdaftar")

def checkEmailInTweet(req):
    for alamat in tweets:
        if alamat['email'] == req['email']:
            alamat['tweet'].append(req['tweet'])
            alamat['date'].append(req['date'])
            return
    req['tweet'] = [req['tweet']]
    req['date'] = [req['date']]
    tweets.append(req)
    return 

def checkEmailandTweet(email,tweet):
    indexEmail = 0
    for akun in tweets:
        if akun['email'] == email:
            indeksTweet = 0
            for status in akun['tweet']:
                print(status,tweet,akun['tweet'])
                if status == tweet:
                    tweets[indexEmail]['tweet'].pop(indeksTweet)
                    tweets[indexEmail]['date'].pop(indeksTweet)
                    return indexEmail
                indeksTweet += 1
            abort(400, message = "tweet tidak ditemukan")

        indexEmail += 1

    abort(400, message = "email belum pernah ngetweet")

class TweetData(Resource):
    def get(self):
        return tweets

    def post(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            "email",
            help = "Masukan email anda",
            required = True,
            location = ['json']
        )
        self.reqparse.add_argument(
            "tweet",
            help = "Masukan tweet anda",
            required = True,
            location = ['json']
        )

        req = request.json
        date = datetime.now()
        req['date'] = str(date)
        args = self.reqparse.parse_args()
        checkEmail(req['email'])

        checkEmailInTweet(req)
        # tweets.append(req)
        updateDataTweet(tweets)
        return req

    def delete(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            "email",
            help = "Masukan email anda",
            required = True,
            location = ['json']
        )
        self.reqparse.add_argument(
            "tweet",
            help = "Masukan tweet anda",
            required = True,
            location = ['json']
        )

        req = request.json
        args = self.reqparse.parse_args()
        checkEmail(req['email'])
        checkEmailandTweet(req['email'],req['tweet'])
        updateDataTweet(tweets)
        return '', 200

        
    def put(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            "email",
            help = "Masukan email anda",
            required = True,
            location = ['json']
        )
        self.reqparse.add_argument(
            "tweet",
            help = "Masukan tweet yang ingin diubah",
            required = True,
            location = ['json']
        )
        self.reqparse.add_argument(
            "tweetBaru",
            help = "Masukan tweet baru",
            required = True,
            location = ['json']
        )

        req = request.json
        args = self.reqparse.parse_args()
        index = checkEmailandTweet(req['email'],req['tweet'])
        
        date = datetime.now()
        tweets[index]['tweet'].append(req['tweetBaru'])
        tweets[index]['date'].append(str(date))
        updateDataTweet(tweets)
        return tweets[index]


users_api = Blueprint('/resources/tweetUser',__name__)

api = Api(users_api)

api.add_resource(data, 'users')
api.add_resource(LogIn, 'login')
api.add_resource(SignUp, 'signup')
api.add_resource(TweetData, 'tweet')