import logging, json
import datetime
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import *

bp_user = Blueprint('user', __name__)
api = Api(bp_user)

class UserResource(Resource):
    def __init__(self):
        if User.query.first() is None:
            user = User(None, "trastanechora", "roadtoalterra", None, "maestro@alphatech.id", None, None, None, None, datetime.datetime.now(), None, None, None)
            db.session.add(user)
            db.session.commit()

    # def crossdomain(origin=None, methods=None, headers=None,
    #                 max_age=21600, attach_to_all=True,
    #                 automatic_options=True):
    #     if methods is not None:
    #         methods = ', '.join(sorted(x.upper() for x in methods))
    #     if headers is not None and not isinstance(headers, basestring):
    #         headers = ', '.join(x.upper() for x in headers)
    #     if not isinstance(origin, basestring):
    #         origin = ', '.join(origin)
    #     if isinstance(max_age, timedelta):
    #         max_age = max_age.total_seconds()

    #     def get_methods():
    #         if methods is not None:
    #             return methods

    #         options_resp = current_app.make_default_options_response()
    #         return options_resp.headers['allow']

    #     def decorator(f):
    #         def wrapped_function(*args, **kwargs):
    #             if automatic_options and request.method == 'OPTIONS':
    #                 resp = current_app.make_default_options_response()
    #             else:
    #                 resp = make_response(f(*args, **kwargs))
    #             if not attach_to_all and request.method != 'OPTIONS':
    #                 return resp

    #             h = resp.headers

    #             h['Access-Control-Allow-Origin'] = origin
    #             h['Access-Control-Allow-Methods'] = get_methods()
    #             h['Access-Control-Max-Age'] = str(max_age)
    #             if headers is not None:
    #                 h['Access-Control-Allow-Headers'] = headers
    #             return resp

    #         f.provide_automatic_options = False
    #         return update_wrapper(wrapped_function, f)
    #     return decorator

    # @bp_user.route('/public/register', methods=['POST', 'OPTIONS'])
    # @crossdomain(origin='*')
    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument('username', location='json', required=True)
        parse.add_argument('password', location='json', required=True)
        parse.add_argument('email', location='json', required=True)
        args = parse.parse_args()

        user = User(None, args['username'], args['password'], None, args['email'], None, None, None, None, datetime.datetime.now(), None, None, None)

        db.session.add(user)
        db.session.commit()

        # response.headers.add('Access-Control-Allow-Origin', '*')
        return marshal(user, User.response_field), 200, {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

class AdminResource(Resource):
    def get(self, id=None):
        parse = reqparse.RequestParser()
        parse.add_argument('p',type=int,location='args',default=1)
        parse.add_argument('rp',type=int,location='args',default=5)
        parse.add_argument('client_id',location='args')
        parse.add_argument('status',location='args')
        
        args = parse.parse_args()

        offset = args['p']*args['rp']-args['rp']

        qry = User.query
        user_list = []

        if id is None:
            for user in qry.limit(args['rp']).offset(offset).all():
                user_list.append(marshal(user, User.response_field))
        else:
            user = User.query.filter_by(id=id).first()
            user_list.append(marshal(user, User.response_field))

        return user_list, 200, {'Content-Type': 'application/json'}

    @jwt_required    
    def delete(self, id):
        # return id
        qry = User.query.filter_by(id=id).first()
        # return marshal(qry, User.response_field)

        # user = get_jwt_identity()
        # identity = marshal(user, User.response_field)

        if qry is not None:
            db.session.delete(qry)
            db.session.commit()
            return "Data Deleted", 200, { 'Content-Type': 'application/json' }
        else :
            return "Data Not Found", 404, { 'Content-Type': 'application/json' }
        

api.add_resource(UserResource,'/public/register')
api.add_resource(AdminResource, '/admin/users', '/admin/users/<int:id>')