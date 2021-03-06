import logging, json
import datetime
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from ..user import User
from flask_cors import CORS

from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims

bp_auth = Blueprint('auth', __name__)
CORS(bp_auth)
api = Api(bp_auth)

class CreateTokenResources(Resource):
    @jwt_required
    def get(self):
        user = get_jwt_identity()
        identity = marshal(user, User.response_field)
        return {
            'status': 'OK',
            'data': identity
        }, 200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        args = parser.parse_args()

        qry = User.query.filter_by(username = args['username']).filter_by(password = args['password']).first()

        if qry is not None:
            token = create_access_token(identity = marshal(qry, User.response_field))
        else:
            return {'status':'UNAUTORIZED', 'message':'invalid key or secret'}, 401, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        return {
            'status': 'OK',
            'logged_in_as': args['username'],
            'token': token
        }, 200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }

# class ShowUserProfile(Resource):
#     @jwt_required
#     def get(self):
#         user = get_jwt_identity()
#         identity = marshal(user, User.response_field)

#         return {
#             'status': 'OK',
#             'data': identity,
#             'valid_thru': datetime.now() + timedelta(hours=1)
#         }, 200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }


api.add_resource(CreateTokenResources, '/public/login')