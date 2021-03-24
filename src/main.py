"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorites_planets, Favorites_characters
import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
jwt = JWTManager(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)




@app.route('/register', methods=['POST'])
def register():
    request_body = request.get_json()

    if not request_body.get("name", None):
        return jsonify({"message": "Invalid client request, name is required", "status": False, "exists": False}), 400
    if not request_body.get("lastname", None):
        return jsonify({"message": "Invalid client request, lastname is required", "status": False, "exists": False}), 400
    if not request_body.get("mail", None):
        return jsonify({"message": "Invalid client request, mail is required", "status": False, "exists": False}), 400
    if not request_body.get("password", None):
        return jsonify({"message": "Invalid client request, password is required", "status": False, "exists": False}), 400
    
    user = User.query.filter_by(mail=request_body.get("mail")).first()
    if not user is None:
        return jsonify({"message": "User already exists", "status": False, "exists": True}), 409


    user = User(request_body.get("name"), request_body.get("lastname"), request_body.get("mail"), request_body.get("password"))

    user.password = generate_password_hash(user.password)

    db.session.add(user)
    
    db.session.commit()

    return jsonify({"message": "Successful register", "status": True, "exists": False}), 200

@app.route('/login', methods=['POST'])
def login():
    request_body = request.get_json()

    if not request_body.get("mail", None):
        return jsonify({"message": "User name is required", "status": False}), 400

    if not request_body.get("password", None):
        return jsonify({"message": "User name is required", "status": False}), 400

    user = User.query.filter_by(mail=request_body.get("mail")).first()
    
    if not user:
        return jsonify({"message": "Username/Password are incorrect", "status": False}), 401


    if not check_password_hash(user.password, request_body.get("password")):
        return jsonify({"message": "Username/Password are incorrect", "status": False}), 401

    #Token session
    expiry_token = datetime.timedelta(days=3)
    access_token = create_access_token(identity=user.id, expires_delta=expiry_token)

    response_body = {
        "message": "Successful login",
        "status": True,
        "user": user.serialize(),
        "token": access_token,
        "expiry": expiry_token.total_seconds()*1000
    }
    return jsonify(response_body), 200

@app.route('/session', methods=['GET'])
@jwt_required()
def check_session():
    user_id = get_jwt_identity()
    print(user_id)
    query = User.query.get(user_id);
    if query is None:
        return jsonify({"message": "Invalid token", "status": False}), 401


    return jsonify({"message": "Session ok", "status": True}), 200

@app.route('/people/page/<int:num_page>', methods=['GET'])
# https://www.swapi.tech/api/people?page=2&limit=10
def get_people(num_page):
    query = Character.query.offset(num_page).limit(10)
    
    results = list(map(lambda character: character.serialize(), query))

    if len(results) == 0:
        status = False
    else: 
        status = True

    response_body = {
        "message": results,
        "status": status
    }

    return jsonify(response_body), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_character(people_id):

    query = Character.query.get(people_id)


    if query is None:
        return jsonify({"message": "Character not found", "status": False}), 404

    results = query.serialize()

    response_body = {
        "message": results,
        "status": True
    }

    return jsonify(response_body), 200

@app.route('/planets/page/<int:num_page>', methods=['GET'])
def get_planets(num_page):
    query = Planet.query.offset(num_page).limit(10)

    results = list(map(lambda planet: planet.serialize(), query))

    if len(results) == 0:
        status = False
    else: 
        status = True

    response_body = {
        "message": results,
        "status": status
    }

    return jsonify(response_body), 200

@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):

    query = Planet.query.get(planet_id)

    if query is None:
        return jsonify({"message": "Planet not found", "status": False}), 404


    results = query.serialize()

    response_body = {
        "message": results,
        "status": True
    }

    return jsonify(response_body), 200

@app.route('/users', methods=['GET'])
def get_users():

    query = User.query.all()

    results = list(map(lambda user: user.serialize(), query))

    response_body = {
        "message": results
    }

    return jsonify(response_body), 200

@app.route('/users/favorites', methods=['GET'])
@jwt_required()
def get_favorites():
    user_id = get_jwt_identity()
    query_favorites_characters = Favorites_characters.query.filter_by(user_id=user_id)
    query_favorites_planet = Favorites_planets.query.filter_by(user_id=user_id)

    if query_favorites_characters is None or query_favorites_planet is None:
        return jsonify({"message": "User not found", "status": False}), 404

    results = []

    results += list(map(lambda favorite_character: favorite_character.serialize(), query_favorites_characters))
    results += list(map(lambda favorite_planet: favorite_planet.serialize(), query_favorites_planet))

    for result in results:
        if result.get("type") == "planet":
            query = Planet.query.get(result.get("planet_uid"));
            result["name"] = query.serialize().get("name")
        else:
            query = Character.query.get(result.get("character_uid"));
            result["name"] = query.serialize().get("name")

    response_body = {
        "message": results,
        "status": True
    }

    return jsonify(response_body), 200

@app.route('/users/favorites', methods=['POST'])
@jwt_required()
def add_favorites():
    user_id = get_jwt_identity()
    request_body = request.get_json()
    query_user = User.query.get(user_id)

    if query_user is None:
        return jsonify({"message": "User not found", "status": False}), 404


    if not "type" in request_body:
        raise APIException("Invalid client request, has no favorite type ", status_code=400)
    if request_body["type"] == "character":
        if not "character_uid" in request_body:
            raise APIException("Invalid client request, has no favorite character_uid ", status_code=400)

        query_character = Character.query.get(request_body["character_uid"])

        if query_character is None:
            return jsonify({"message": "Character not found", "status": False}), 404
            
        else:
            query_favorite_character = Favorites_characters.query.get((user_id, request_body["character_uid"]))
            if query_favorite_character is None:
                favorite_character = Favorites_characters(user_id, request_body["character_uid"])
                db.session.add(favorite_character)
                db.session.commit()
            else:
                return jsonify({"message": "Invalid client request, favorite already exists", "status": False}), 400


    elif request_body["type"] == "planet":
        if not "planet_uid" in request_body:
            raise APIException("Invalid client request, has no favorite planet_uid ", status_code=400)

        query_planet = Planet.query.get(request_body["planet_uid"])

        if query_planet is None:
            return jsonify({"message": "Planet not found", "status": False}), 404

        else:
            query_favorite_planet = Favorites_planets.query.get((user_id, request_body["planet_uid"]))
            if query_favorite_planet is None:
                favorite_planet = Favorites_planets(user_id, request_body["planet_uid"])
                db.session.add(favorite_planet)
                db.session.commit()
            else:
                return jsonify({"message": "Invalid client request, favorite already exists", "status": False}), 400


    else:
        raise APIException("Invalid client request, no valid type found", status_code=400)

    response_body = {
        "message": "Favorite successfully added", 
        "status": True
    }

    return jsonify(response_body), 200

@app.route('/favorite/<int:favorite_id>', methods=['DELETE'])
@jwt_required()
def delete_favorites(favorite_id):
    user_id = get_jwt_identity()
    request_body = request.get_json()

    query_user = User.query.get(user_id)

    if query_user is None:
        return jsonify({"message": "User not found", "status": False}), 404


    if not "type" in request_body:
        raise APIException("Invalid client request, has no favorite type ", status_code=400)
    if request_body["type"] == "character":

            query_favorite_character = Favorites_characters.query.get((user_id, favorite_id))
            if not query_favorite_character is None:
                db.session.delete(query_favorite_character)
                db.session.commit()
            else:
                return jsonify({"message": "Favorite not found", "status": False}), 404


    elif request_body["type"] == "planet":

            query_favorite_planet = Favorites_planets.query.get((user_id, favorite_id))
            if not query_favorite_planet is None:
                db.session.delete(query_favorite_planet)
                db.session.commit()
            else:
                return jsonify({"message": "Favorite not found", "status": False}), 404


    else:
        raise APIException("Invalid client request, no valid type found", status_code=400)

    response_body = {
        "message": "favorite successfully deleted",
        "status": True
    }

    return jsonify(response_body), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
