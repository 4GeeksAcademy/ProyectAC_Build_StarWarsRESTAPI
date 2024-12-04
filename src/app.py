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

# ENDPOINTS
# ENDPOINTS DE USUARIOS
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'Se necesitan username, email y password'}), 400

    # Verificar si el usuario ya existe
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'El correo electrónico ya está registrado'}), 400

    user = User(username=username, email=email, password=password, is_active=True)
    db.session.add(user)
    db.session.commit()
    return jsonify({'msg': 'Usuario creado con éxito', 'id': user.id}), 201

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    return jsonify({'error': 'Autenticación no implementada. Debe reemplazar el user_id fijo.'}), 501

# ENDPOINTS DE PERSONAJES
@app.route('/characters', methods=['GET'])
def get_characters():
    characters = Character.query.all()
    return jsonify([{
        'id': cha.id,
        'name': cha.name,
        'hair_color': cha.hair_color,
        'eye_color': cha.eye_color,
        'gender': cha.gender
    } for cha in characters]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person_by_id(people_id):
    character = Character.query.get(people_id)
    if not character:
        return jsonify({'error': 'Personaje no encontrado'}), 404
    return jsonify({
        'id': character.id,
        'name': character.name,
        'hair_color': character.hair_color,
        'eye_color': character.eye_color,
        'gender': character.gender
    }), 200

# ENDPOINTS DE PLANETAS
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([{
        'id': planet.id,
        'name': planet.name,
        'climate': planet.climate,
        'terrain': planet.terrain,
        'population': planet.population,
        'climate': planet.climate,
        'gravity': planet.gravity
    } for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({'error': 'Planeta no encontrado'}), 404
    return jsonify({
        'id': planet.id,
        'name': planet.name,
        'climate': planet.climate,
        'terrain': planet.terrain
    }), 200

# FAVORITOS
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

@app.route('/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    favorite = Favorite.query.get(favorite_id)
    if not favorite:
        return jsonify({'error': 'Favorito no encontrado'}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'msg': 'Eliminado de Favoritos'}), 200

# COMENTARIOS
@app.route('/comments', methods=['POST'])
def add_comment():
    data = request.json
    content = data.get('content')
    user_id = data.get('user_id')

    if not content or not user_id:
        return jsonify({'error': 'Se requieren el contenido y la identificación del usuario'}), 400

    comment = Comment(content=content, user_id=user_id)
    db.session.add(comment)
    db.session.commit()
    return jsonify({'msg': 'Comentario añadido'}), 201

# PLUSES
# AÑADIR UN PLANETA (POST)
@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.json
    name = data.get('name')
    terrain = data.get('terrain')
    population = data.get('population')
    climate = data.get('climate')
    gravity = data.get('gravity')

    if not name or not terrain or not population or not climate or not gravity:
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    planet = Planet(name=name, terrain=terrain, population=population, climate=climate, gravity=gravity)
    db.session.add(planet)
    db.session.commit()
    return jsonify({'msg': 'Planeta creado exitosamente', 'id': planet.id}), 201

# MODIFICAR UN PLANETA (PUT)
@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    data = request.json
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({'error': 'Planeta no encontrado'}), 404

    planet.name = data.get('name', planet.name)
    planet.terrain = data.get('terrain', planet.terrain)
    planet.population = data.get('population', planet.population)
    planet.climate = data.get('climate', planet.climate)
    planet.gravity = data.get('gravity', planet.gravity)

    db.session.commit()
    return jsonify({'msg': 'Planeta actualizado exitosamente'}), 200

# ELIMINAR UN PLANETA (DELETE)
@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({'error': 'Planeta no encontrado'}), 404

    db.session.delete(planet)
    db.session.commit()
    return jsonify({'msg': 'Planeta eliminado exitosamente'}), 200

# AÑADIR UN PERSONAJE (POST)
@app.route('/people', methods=['POST'])
def create_character():
    data = request.json
    name = data.get('name')
    hair_color = data.get('hair_color')
    eye_color = data.get('eye_color')
    gender = data.get('gender')
    species = data.get('species')
    height = data.get('height')

    if not name or not gender or not species or not height:
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    character = Character(name=name, hair_color=hair_color, eye_color=eye_color, gender=gender, species=species, height=height)
    db.session.add(character)
    db.session.commit()
    return jsonify({'msg': 'Personaje creado exitosamente', 'id': character.id}), 201

# MODIFICAR UN PERSONAJE (PUT)
@app.route('/people/<int:people_id>', methods=['PUT'])
def update_character(people_id):
    data = request.json
    character = Character.query.get(people_id)
    if not character:
        return jsonify({'error': 'Personaje no encontrado'}), 404

    character.name = data.get('name', character.name)
    character.hair_color = data.get('hair_color', character.hair_color)
    character.eye_color = data.get('eye_color', character.eye_color)
    character.gender = data.get('gender', character.gender)
    character.species = data.get('species', character.species)
    character.height = data.get('height', character.height)

    db.session.commit()
    return jsonify({'msg': 'Personaje actualizado exitosamente'}), 200


# ELIMINAR UN PERSONAJE (DELETE)
@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_character(people_id):
    character = Character.query.get(people_id)
    if not character:
        return jsonify({'error': 'Personaje no encontrado'}), 404

    db.session.delete(character)
    db.session.commit()
    return jsonify({'msg': 'Personaje eliminado exitosamente'}), 200


# Configuración de inicio
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)