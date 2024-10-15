#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
   def post(self):
       data - request.get_json()
       try:
           user = User(
               username=data['username'],
               password_hash=['password'],
               image_url=data.get('image_url', ''),
               bio=data.get('bio', '')
               )
           db.session.add(user)
           db.session.commit()
           session['user_id'] = user.id
           return user.to_dict(), 201
       except IntegrityError:
           db.session.rollback()
           return {"errors": ["Username already taken"]}, 422

class CheckSession(Resource):
     def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"error": "Unauthorized"}, 401
        user = User.query.get(user_id)
        return user.to_dict(), 200
  

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and user.verify_password(data['password']):
            session['user_id'] = user.id
            return user.to_dict(), 200
        return {"error": "Invalid username or password"}, 401
    

 class Logout(Resource):
    def delete(self):
        if 'user_id' not in session or session['user_id'] is None:
            return jsonify({"error": "Unauthorized"}), 401
        
        # If a user is logged in, remove the user_id from the session
        session.pop('user_id', None)
        return '', 204
  

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"error": "Unauthorized"}, 401
        recipes = Recipe.query.all()
        return [recipe.to_dict() for recipe in recipes], 200

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"error": "Unauthorized"}, 401
        data = request.get_json()
        try:
            recipe = Recipe(
                title=data['title'],
                instructions=data['instructions'],
                minutes_to_complete=data.get('minutes_to_complete', 0),
                user_id=user_id
            )
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201
        except ValueError as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422
   

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)