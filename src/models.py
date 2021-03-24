from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    lastname = db.Column(db.String(250), nullable=False)
    mail = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)

    def __init__(self, name, lastname, mail, password):
        self.name = name
        self.lastname = lastname
        self.mail = mail
        self.password = password

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "lastname": self.lastname,
            "mail": self.mail
        }

class Planet(db.Model):
    __tablename__ = 'planet'
    uid = db.Column(db.Integer, primary_key=True)
    diameter = db.Column(db.Integer, nullable=False)
    rotation_period = db.Column(db.Integer, nullable=False)
    orbital_period = db.Column(db.Integer, nullable=False)
    gravity = db.Column(db.String(250), nullable=False)
    population = db.Column(db.Integer, nullable=False)
    climate = db.Column(db.String(250), nullable=False)
    terrain = db.Column(db.String(250), nullable=False)
    surface_water = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    edited = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    name = db.Column(db.String(250), nullable=False)

    def serialize(self):
        return {
            "uid" : self.uid,
            "diameter" : self.diameter,
            "rotation_period" : self.rotation_period,
            "orbital_period" : self.orbital_period,
            "gravity" : self.gravity,
            "population" : self.population,
            "climate" : self.climate,
            "terrain" : self.terrain,
            "surface_water" : self.surface_water,
            "created" : self.created,
            "edited" : self.edited,
            "name" : self.name
        }

class Character(db.Model):
    __tablename__ = 'character'
    uid = db.Column(db.Integer, primary_key=True)
    height = db.Column(db.Integer, nullable=False)
    mass = db.Column(db.Integer, nullable=False)
    hair_color = db.Column(db.String(250), nullable=False)
    skin_color = db.Column(db.String(250), nullable=False)
    eye_color = db.Column(db.String(250), nullable=False)
    birth_year = db.Column(db.String(250), nullable=False)
    gender = db.Column(db.String(250), nullable=False)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    edited = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    name = db.Column(db.String(250), nullable=False)
    homeworld = db.Column(db.Integer, db.ForeignKey('planet.uid'), nullable=False)
    planet = db.relationship('Planet', backref='character', lazy=True)

    def serialize(self):
        return {
            "uid" : self.uid,
            "height" : self.height,
            "mass" : self.mass,
            "hair_color" : self.hair_color,
            "skin_color" : self.skin_color,
            "eye_color" : self.eye_color,
            "birth_year" : self.birth_year,
            "gender" : self.gender,
            "created" : self.created,
            "edited" : self.edited,
            "name" : self.name,
            "homeworld" : self.homeworld
            }
    

class Favorites_planets(db.Model):
    __tablename__ = 'favorites_planets'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='favorites_planets', lazy=True)
    planet_uid = db.Column(db.Integer, db.ForeignKey('planet.uid'), primary_key=True)
    planet = db.relationship('Planet', backref='favorites_planets', lazy=True)

    def __init__(self, user_id, planet_uid):
        self.user_id = user_id
        self.planet_uid = planet_uid

    def serialize(self):
        return {
            "user_id" : self.user_id,
            "planet_uid" : self.planet_uid,
            "type": "planet"
        }

class Favorites_characters(db.Model):
    __tablename__ = 'favorites_characters'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='favorites_characters', lazy=True)
    character_uid = db.Column(db.Integer, db.ForeignKey('character.uid'), primary_key=True)
    character = db.relationship('Character', backref='favorites_characters', lazy=True)
    
    def __init__(self, user_id, character_uid):
        self.user_id = user_id
        self.character_uid = character_uid

    def serialize(self):
        return {
            "user_id" : self.user_id,
            "character_uid" : self.character_uid,
            "type": "character"
        }
