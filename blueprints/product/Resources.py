import logging, json
import datetime
import math
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import *
from ..user import User
from ..offer import Offer

bp_product = Blueprint('product', __name__)
api = Api(bp_product)

class ProductResource(Resource):
    def __init__(self):
        pass
        # if User.query.first() is None:
        #     user = User(None, "trastanechora", "roadtoalterra", None, "maestro@alphatech.id", None, None, None, None, datetime.datetime.now(), None, None)
        #     db.session.add(user)
        #     db.session.commit()

    def get(self, id=None):
        parse = reqparse.RequestParser()
        parse.add_argument('p',type=int,location='args', default=1)
        parse.add_argument('rp',type=int,location='args', default=10)
        parse.add_argument('client_id',location='args')
        parse.add_argument('status',location='args')
        parse.add_argument('id', type=int, location="args")
        parse.add_argument('search', location="args")

        parse.add_argument('category', location='args', default='all')
        parse.add_argument('type', location='args', default='all')
                
        args = parse.parse_args()

        offset = args['p']*args['rp']-args['rp']

        qry = Product.query
        qry =qry.filter(Product.flag.like('Available'))

        if args['search'] is not None:
            qry = qry.filter(Product.name.like("%"+args['search']+"%"))
            if qry.first() is None:
                qry = Product.query.filter(Product.category.like("%"+args['search']+"%"))
                if qry.first() is None:
                    qry = Product.query.filter(Product.product_type.like("%"+args['search']+"%"))
                    if qry.first() is None:
                        qry = Product.query.filter(Product.location.like("%"+args['search']+"%"))
                        if qry.first() is None:
                            return {'status': 'Not Found', 'message': 'Item not found'}, 404, {'Content-Type': 'application/json'}

        if args['category'] != 'all':
            qry = qry.filter(Product.category.like("%"+args['category']+"%"))

        if args['type'] != 'all':
            qry = qry.filter(Product.product_type.like("%"+args['type']+"%"))

        product_list = []
        if args['id'] != None:
            temp = qry.filter_by(posted_by=args['id']).all()
            for product in temp:
                product_list.append(marshal(product, Product.response_field))
            return {
            'status': 'OK',
            'total_results': qry.count(),
            'page': args['p'],
            'total_page': math.ceil(qry.count() / args['rp']),
            'displaying': len(product_list),
            'category': args['category'],
            'type': args['type'],
            'data': product_list
                }, 200, {'Content-Type': 'application/json'}


        if id == None:
            for product in qry.limit(args['rp']).offset(offset).all():
                product_list.append(marshal(product, Product.response_field))
        else:
            product = Product.query.filter_by(id=id).first()
            product_list.append(marshal(product, Product.response_field))
            # temp = Product.query.filter_by(posted_by=id).all()
            # for product in temp:
            #     product_list.append(marshal(product, Product.response_field))
            # product_list.append(marshal(product, Product.response_field))

        # return product_list, 200, {'Content-Type': 'application/json'}
        return {
            'status': 'OK',
            'total_results': qry.count(),
            'page': args['p'],
            'total_page': math.ceil(qry.count() / args['rp']),
            'displaying': len(product_list),
            'category': args['category'],
            'type': args['type'],
            'data': product_list
        }, 200, {'Content-Type': 'application/json'}

    @jwt_required
    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument('name', location='json', required=True)
        parse.add_argument('product_type', location='json', required=True)
        parse.add_argument('category', location='json', required=True)
        parse.add_argument('description', location='json')
        parse.add_argument('amount', location='json', required=True)
        parse.add_argument('constanta', location='json', required=True)
        parse.add_argument('price', location='json', required=True)
        parse.add_argument('location', location='json', required=True)
        parse.add_argument('delivery_provided', location='json', required=True)
        args = parse.parse_args()

        user = get_jwt_identity()
        identity = marshal(user, User.response_field)

        product = Product(None, args['name'], args['product_type'], args['category'], args['description'], args['amount'], args['constanta'], args['price'], datetime.datetime.now(), identity['id'], args['location'], "OPEN", None, args['delivery_provided'], "Available")

        db.session.add(product)
        db.session.commit()

        # response.headers.add('Access-Control-Allow-Origin', '*')
        return marshal(product, Product.response_field), 200, {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
        # response.headers.add('Access-Control-Allow-Origin', '*')
        # return marshal(user, User.response_field), 200, {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}


    @jwt_required
    def put(self):
        parse = reqparse.RequestParser()
        parse.add_argument('product_id', type=int, location='json', required=True)
        args = parse.parse_args()

        user = get_jwt_identity()
        identity = marshal(user, User.response_field)

        offer = Offer.query.filter_by(product_id=args['product_id']).all()
        ofr = marshal(offer, Offer.response_field)
        dump = json.dumps(ofr)

        out = Product.query.filter_by(id=args['product_id']).first()

        out.offer = dump
        db.session.commit()


        temp = json.loads(out.offer)
        # return temp
        # return marshal(out, Product.response_field)

        temp2 = marshal(out, Product.response_field)
        temp2['offer'] = temp

        return temp2
    
    @jwt_required
    def delete(self, id):
        pass

class UserDeleteProduct(Resource):
    @jwt_required
    def put(self, id):
        qry = Product.query.filter_by(id=id).first()
        qry.flag = "Deleted"
        db.session.commit()


class AdminProduct(Resource):
    @jwt_required    
    def delete(self, id):
        qry = Product.query.filter_by(id=id).first()

        if qry is not None:
            db.session.delete(qry)
            db.session.commit()
            return "Data Deleted", 200, { 'Content-Type': 'application/json' }
        else :
            return "Data Not Found", 404, { 'Content-Type': 'application/json' }

api.add_resource(ProductResource,'/public/products', '/public/products/<int:id>')
api.add_resource(UserDeleteProduct, '/users/products/<int:id>')
api.add_resource(AdminProduct, '/admin/products/<int:id>')