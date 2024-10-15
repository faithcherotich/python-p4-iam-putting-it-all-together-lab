from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    # Relationships
    recipes = db.relationship('Recipe', backref='user', lazy=True, cascade="all, delete-orphan")

    # Serialization
    serialize_rules = ('-recipes.user',)  # Avoid circular reference when serializing
    
    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hash is not accessible")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # Method to verify password
    def verify_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    # Validation for username uniqueness
    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError("Username is required")
        return username

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    # Foreign Key and Relationship
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Serialization
    serialize_rules = ('-user.recipes',)

    # Validations
    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise ValueError("Title is required")
        return title

    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long")
        return instructions
   