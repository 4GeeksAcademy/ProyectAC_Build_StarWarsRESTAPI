"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite, Comment

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# OBTENER USUARIOS
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id' : user.id, 'username' : user.username, 'email' : user.email} for user in users]), 200

# OBTENER PERSONAJES
@app.route('/characters', methods=['GET'])
def get_characters():
    characters = Character.query.all()
    return jsonify([{'id': cha.id, 'name': cha.name, 'description': cha.description} for cha in characters]), 200

# OBTENER PERSONAJE POR ID
@app.route('/people/<int:people_id>', methods=['GET'])
def get_person_by_id(people_id):
    character = Character.query.get(people_id)
    if not character:
        return jsonify({'error': 'Character not found'}), 404
    return jsonify({
        'id': character.id,
        'name': character.name,
        'description': character.description
    }), 200

# LISTAR TODOS LOS REGISTROS DE PERSONAJES
@app.route('/people', methods=['GET'])
def get_all_people():
    characters = Character.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description
    } for c in characters]), 200

# OBTENER PLANETAS
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([{'id': planet.id, 'name': planet.name, 'climate': planet.climate} for planet in planets]), 200

# OBTENER UN PLANETA POR ID
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({'error': 'Planet not found'}), 404
    return jsonify({
        'id': planet.id,
        'name': planet.name,
        'climate': planet.climate,
        'terrain': planet.terrain
    }), 200

# AÑADIR A FAVORITO
@app.route('/favorites', methods=['POST'])
def add_favorite():
    data = request.json
    user_id = data.get('user_id')
    character_id = data.get('character_id')
    planet_id = data.get('planet_id')

    if not user_id or (not character_id and not planet_id):
        return jsonify({'error': 'Se requiere el ID de usuario y de personaje o de planeta'}), 400

    favorite = Favorite(user_id=user_id, character_id=character_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({'msg': 'Favorito añadido'}), 201

# BORRAR DE FAVORITOS
@app.route('/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    favorite = Favorite.query.get(favorite_id)
    if not favorite:
        return jsonify({'error': 'Favorito no encontrado'}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'msg': 'Eliminado de favoritos'}), 200

# AÑADIR UN PLANETA A FAVORITOS
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = 1  # Usuario actual (deberías cambiar esto con la autenticación)
    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({'msg': 'Planet added to favorites'}), 201

# ELIMINAR UN PLANETA DE FAVORITOS
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def remove_favorite_planet(planet_id):
    user_id = 1  # Usuario actual
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({'error': 'Favorite not found'}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'msg': 'Planet removed from favorites'}), 200

# AÑADIR UN PERSONAJE A FAVORITOS
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    user_id = 1  # Usuario actual
    favorite = Favorite(user_id=user_id, character_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({'msg': 'Person added to favorites'}), 201

# ELIMINAR UN PERSONAJE DE FAVORITOS
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def remove_favorite_person(people_id):
    user_id = 1  # Usuario actual
    favorite = Favorite.query.filter_by(user_id=user_id, character_id=people_id).first()
    if not favorite:
        return jsonify({'error': 'Favorite not found'}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'msg': 'Person removed from favorites'}), 200

# LISTAR LOS FAVORITOS DEL USUARIO ACTUAL
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = 1  # Usuario actual
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': f.id,
        'planet_id': f.planet_id,
        'character_id': f.character_id
    } for f in favorites]), 200

# CREAR UN NUEVO USUARIO
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')

    if not username or not email:
        return jsonify({'error': 'Se necesita un nombre de usuario y un correo electrónico'}), 400

    # Verificar si el usuario ya existe
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'El correo electrónico ya está registrado'}), 400

    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return jsonify({'msg': 'Usuario creado con éxito', 'id': user.id}), 201

# AGREGAR COMENTARIOS
@app.route('/comments', methods=['POST'])
def add_comment():
    data = request.json
    content = data.get('content')
    user_id = data.get('user_id')
    character_id = data.get('character_id')
    planet_id = data.get('planet_id')

    if not content or not user_id:
        return jsonify({'error': 'Content and user ID are required'}), 400

    comment = Comment(content=content, user_id=user_id, character_id=character_id, planet_id=planet_id)
    db.session.add(comment)
    db.session.commit()
    return jsonify({'msg': 'Comment added successfully'}), 201

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)