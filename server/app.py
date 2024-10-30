#!/usr/bin/env python3

from flask import make_response, request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

@app.before_request
def check_if_logged_in():
    if not session.get('user_id') and request.endpoint == 'recipes':
        return make_response({'error': 'please login to review recipes'}, 401)

class Signup(Resource):
    def post(self):
        user_data = request.get_json()
        
        username = user_data.get('username')
        password = user_data.get('password')
        bio = user_data.get('bio')
        image_url = user_data.get('image_url')
        if username:
            new_user = User(username=username, bio=bio, image_url=image_url)
            new_user.password_hash = password
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return new_user.to_dict(), 201
        response = make_response({'error': 'invalid user'}, 422)
        return response 



class CheckSession(Resource):
    def get(self):
        if session['user_id']:
            user = User.query.filter_by(id=session['user_id']).first()
            response = make_response(user.to_dict(), 200)
            return response 
        return make_response({'error': 'unauthorized'}, 401)
    

class Login(Resource):
    def post(self):
        data = request.get_json()

        user = User.query.filter_by(username=data.get('username')).first()
        if user and user.authenticate(data.get('password')):
            session['user_id'] = user.id
            return make_response(user.to_dict(), 200)
        return make_response({'error': 'invalid login credentials'}, 401)

class Logout(Resource): 
    def delete(self):
        if session['user_id']:
            session['user_id'] = None
        
            return {}, 204
        return {}, 401


    

    
class RecipeIndex(Resource):
    def get(self):
        user = User.query.filter_by(id=session.get('user_id')).first()
       

        recipes = [recipe.to_dict() for recipe in user.recipes]
        return make_response(recipes, 200)
        # return make_response({'Recipes': 'no recipes to display'}, 200)
    
    def post(self):
        data = request.get_json()
        
        try: 
            recipe = Recipe(title=data.get('title'), instructions=data.get('instructions'), 
                            minutes_to_complete = data.get('minutes_to_complete'), user_id=session['user_id'] )
            db.session.add(recipe)
            db.session.commit()

            return make_response(recipe.to_dict(), 201)
        
        except:
            return make_response({'error': 'test'}, 422)

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)