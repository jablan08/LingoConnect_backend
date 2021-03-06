import json

from flask import jsonify, Blueprint, abort, make_response, session
from flask_bcrypt import check_password_hash, generate_password_hash

from flask_restful import (Resource, Api, reqparse,
                               inputs, fields, marshal,
                               marshal_with, url_for)

from flask_login import login_user, logout_user, login_required, current_user
import models

user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String
}


class UserList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'username',
            required=True,
            help='No username provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'email',
            required=True,
            help='No email provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'primaryLanguage',
            required=False,
            help='No primary language provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'password',
            required=True,
            help='No password provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'verify_password',
            required=True,
            help='No password verification provided',
            location=['form', 'json']
        )
        super().__init__()
    
    def get(self):
        users = [marshal(user, user_fields) for user in models.User.select()]
        
        return users

    def post(self):
        #registrations
        args = self.reqparse.parse_args()
        if args['password'] == args['verify_password']:
            
            user = models.User.create_user(**args)
            
            login_user(user)
            return make_response(
                json.dumps({
                    'user': marshal(user, user_fields),
                    'message': 'success',
                    'logged': True
                }), 200)
        return make_response(
            json.dumps({
                'error': 'Password and password verification do not match'
            }), 400)

class User(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'username',
            required=False,
            help='No username provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'email',
            required=False,
            help='No email provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'password',
            required=False,
            help='No password provided',
            location=['form', 'json']
        )
        
        super().__init__()
    
    
    def post(self):
        try:
            args = self.reqparse.parse_args()
            user = models.User.get(models.User.username==args["username"])
            if(user):
                if(check_password_hash(user.password, args["password"])):
                    login_user(user)
                    return make_response(
                        json.dumps({
                            'user': marshal(user, user_fields),
                            'message': 'success',
                            'logged': True
                        }), 200)
                else:
                    return make_response(
                        json.dumps({
                            'message':"Incorrect password"
                        }), 404)
        except models.User.DoesNotExist:
            return make_response(
                json.dumps({
                    'message':"Username does not exist"
                }), 404)

    @marshal_with(user_fields)
    def put(self, id):
        try:
            args = self.reqparse.parse_args()
            if (args['password']==''):
                self.reqparse.remove_argument('password')
                args = self.reqparse.parse_args()
            else:
                args['password'] = generate_password_hash(args["password"])
            query = models.User.update(**args).where(models.User.id==id)
            query.execute()
        except models.User.DoesNotExist:
            abort(404)
        else:
            return (models.User.get(models.User.id==id), 200)
    
    @marshal_with(user_fields)
    def get(self, id):
        try:
            user = models.User.get(models.User.id==id)
        except models.User.DoesNotExist:
            abort(404)
        else:
            return (user, 200)

    def delete(self, id):
        queryUser = models.User.delete().where(models.User.id == id)
        queryPhrase = models.Phrase.delete().where(models.Phrase.userId == id)
        queryUser.execute()
        queryPhrase.execute()
        return {"message": "resource deleted"}

class LogoutUser(Resource):
    def post(self):
        logout_user()
        return make_response(
            json.dumps({
                'message': 'Logged out',
                'logged': False
            }), 200)

users_api = Blueprint('resources.users', __name__)
api = Api(users_api)

api.add_resource(
    UserList,
    '/registration'
)
api.add_resource(
    User,
    '/login',
    '/<int:id>'
)

api.add_resource(
    LogoutUser,
    '/logout'
)
