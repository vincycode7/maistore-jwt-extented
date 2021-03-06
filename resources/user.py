from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import create_access_token, create_refresh_token
from models.user import UserModel

#class to list all user
class UserList(Resource):
    @jwt_required()
    def get(self):        
        users = UserModel.find_all()
        if users: return {"users" : [ user.json() for user in users]},201
        return {"message" : 'Item not found'}, 400


#class to register user
class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(name="username", type=str, required=True, help="username cannot be blank",case_sensitive=False)
    parser.add_argument(name="password", type=str, required=True, help="password cannot be blank")
    parser.add_argument(name="email", type=str, required=True, help="email cannot be blank")

    def post(self):
        data = UserRegister.parser.parse_args()

        #check if data already exist
        # if UserModel.find_by_username(username=data["username"]): return {"message" : f"username {data['username']} already exists."},400 # 400 is for bad request
        print(data)
        if UserModel.find_by_email(email=data["email"]): return {"message" : f"email {data['email']} already exists."},400 # 400 is for bad request
        print(data)
        user = UserModel(**data)

        #insert
        try:
            user.save_to_db()
        except Exception as e:
            print(e)
            return {"message" : "An error occured inserting the item"}, 500 #Internal server error

        return user.json(), 201


#class to create user and get user
class User(Resource):
    @jwt_required()
    def get(self, username):
        user = UserModel.find_by_username(username=username)

        if user: return {"user" : user.json()},201
        return {"message" : 'user not found'}, 400

    @jwt_required() #use for authentication before calling post
    def put(self, username):
        
        data = UserRegister.parser.parse_args()
        user = UserModel.find_by_username(username=username)
        email = UserModel.find_by_email(email=data["email"])
        
        if user:
            #update
            try:
                # for product in products: product.update_self_vars(data)
                if email and not (email.email == user.email): return {"message" : f"email {data['email']} already exists."},400 # 400 is for bad request
                for each in data.keys(): user.__setattr__(each, data[each])
                user.save_to_db()
            except Exception as e:
                print(f"error is {e}")
                return {"message" : "An error occured updating the item the item"}, 500 #Internal server error

        #confirm the unique key to be same with the product route
        else:
            # user = UserModel.instance_from_dict(dict_=data)
            user = UserModel(**data)
            #insert
            try:
                if email: return {"message" : f"email {data['email']} already exists."},400 # 400 is for bad request
                user.save_to_db()
            except Exception as e:
                print(f"error is {e}")
                return {"message" : "An error occured inserting the item"}, 500 #Internal server error

        return user.json(), 201



    @jwt_required() #use for authentication before calling post
    def delete(self, username, password=None):
        user = UserModel.find_by_username(username=username)
        if user:
            user.delete_from_db()
            return {"message" : "User deleted"}, 200 # 200 ok 
            
        return {"message" : "User Not found"}, 400 # 400 is for bad request

class UserExt(Resource):

    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(id=user_id)

        if not user: return {"message" : "User not found"}, 404
        return {"user":user.json()}, 200
    
    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(id=user_id)

        if not user: return {"message" : "User not found"}, 404
        user.delete_from_db()
        
        return {"message" : "User deleted."}, 200

class UserLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(name="userid", type=str, required=True, help="userid cannot be blank",case_sensitive=False)
    parser.add_argument(name="password", type=str, required=True, help="password cannot be blank")

    @classmethod
    def post(cls):
        #get user
        data = cls.parser.parse_args()

        #find user in database
        user = UserModel.find_by_id(id=data['userid'])
        if user and safe_str_cmp(user.password,data['password']):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)

            return {
                    "access_token"  : access_token,
                    "refresh_token" : refresh_token
                    }, 200
        return {"message" : "Invalid credentials"}