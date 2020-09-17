import os,db
from resources.store import Store, StoreList
from resources.user import User, UserList, UserRegister, UserExt, UserLogin
from resources.product import Product, ProductList
from flask import Flask, request
# from flask_jwt import JWT, jwt_required
from flask_jwt_extended import JWTManager
from flask_restful import Resource, Api, reqparse

"""

    Flask is the main framework for the project
    flask_jwt is used for authentication via tokens
    flask_restful makes working with flask alot easier
    Flask SQLAlchemy is used to easily store data to a relational database
"""

#export PATH="$PATH:/home/vcode/.local/bin"
#runner : reset && python app.py

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = "vcode" #always remember to get the apps's secret key, also this key should be hidden from the public.
api = Api(app=app)

@app.before_first_request
def create_tables():
    db.create_all()

# jwt = JWT(app, authenticate, identity) #creates a new end point called */auth*
jwt = JWTManager(app) #This doesn't create the auth endpoint

#User
api.add_resource(UserRegister, "/register") #https://mistore.com/register
api.add_resource(User, '/user/<string:username>') #https://mistore.com/gbenga
api.add_resource(UserExt, '/users/<int:user_id>')
# api.add_resource(Users, '/user/<string:name>?<string:password>') #https://mistore.com/gbenga
api.add_resource(UserList , "/users") #https://mistore.com//student

#store
api.add_resource(Store, "/store/<string:storename>") #https://maistore.com/store/shoprite
api.add_resource(StoreList, "/stores") #https://maistore.com/store

#product
api.add_resource(ProductList, "/products") #https://mistore.com/product
api.add_resource(Product, '/product/<string:productname>') #https://mistore.com/product/bags

if __name__ == "__main__":
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)