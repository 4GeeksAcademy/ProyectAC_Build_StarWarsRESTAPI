from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    favorite = db.relationship('Favorite', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
        }
    
class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    hair_color = db.Column(db.String(50))
    eye_color = db.Column(db.String(50))
    gender = db.Column(db.Enum("Male", "Female", "Other", name="gender_enum"))
    species = db.Column(db.String(50))
    height = db.Column(db.Integer)
    favorites = db.relationship('Favorite', backref='character', lazy=True)
    comments = db.relationship('Comment', backref='character', lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
            "gender": self.gender,
            "species": self.species,
            "height": self.height,
        }

class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    terrain = db.Column(db.String(50))
    population = db.Column(db.Integer)
    climate = db.Column(db.String(50))
    gravity = db.Column(db.String(50))
    favorites = db.relationship('Favorite', backref='planet', lazy=True)
    comments = db.relationship('Comment', backref='planet', lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "terrain": self.terrain,
            "population": self.population,
            "climate": self.climate,
            "gravity": self.gravity,
        }

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'), nullable=True)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "planet_id": self.planet_id,
        }

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def serialize(self):
        return {
            "id": self.id,
            "content": self.content,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "planet_id": self.planet_id,
            "created_at": self.created_at,
        }



    # Cualquier modificacion de este archico hay que ejecutar los comandos para crear una nueva version 
    # y subir esa nueva version y se quede registrada


# Convierte la información del usuario en un diccionario que puede ser convertido a JSON para enviarlo en respuestas de API.