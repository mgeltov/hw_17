# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app)
api = Api(app)


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")




movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')

class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre = fields.Pluck(GenreSchema, 'name')
    director = fields.Pluck(DirectorSchema, 'name')

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)



@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        movies_query = db.session.query(Movie)
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id:
            movies_query = db.session.query(Movie).filter(Movie.director_id == director_id)
        if genre_id:
            movies_query = db.session.query(Movie).filter(Movie.genre_id == genre_id)
        if director_id and genre_id:
            movies_query = db.session.query(Movie).filter(Movie.genre_id == genre_id, Movie.director_id == director_id)
        return movies_schema.dump(movies_query.all()), 200


@movie_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid):
        movie = db.session.query(Movie).get(mid)
        if not movie:
            return f"There's no movie with id {mid}", 404
        return movie_schema.dump(movie), 200


@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        directors = db.session.query(Director).all()
        return directors_schema.dump(directors), 200

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)

        return 'New director is added', 201


@director_ns.route('/<int:did>')
class DirectorView(Resource):
    def get(self, did):
        director = db.session.query(Director).get(did)
        if not director:
            return f"There's no director with id {did}", 404
        return director_schema.dump(director), 200

    def put(self, did):
        req_json = request.json
        director = db.session.query(Director).get(did)
        if not director:
            return f"There's no director with id {did}", 404
        director.name = req_json.get('name')
        db.session.add(director)
        db.session.commit()
        return f"Director with id {did} is changed", 204

    def patch(self, did):
        req_json = request.json
        director = db.session.query(Director).get(did)
        if not director:
            return f"There's no director with id {did}", 404
        if 'name' in req_json:
            director.name = req_json.get('name')
            db.session.add(director)
            db.session.commit()
            return f"Director with id {did} is changed", 204

    def delete(self, did):
        director = db.session.query(Director).get(did)
        if not director:
            return f"There's no director with id {did}", 404
        db.session.delete(director)
        db.session.commit()
        return f"Director with id {did} is deleted", 204

@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        genres = db.session.query(Genre).all()
        return directors_schema.dump(genres), 200

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_genre)

        return 'New genre is added', 201


@genre_ns.route('/<int:gid>')
class GenreView(Resource):
    def get(self, gid):
        genre = db.session.query(Genre).get(gid)
        if not genre:
            return f"There's no genre with id {gid}", 404
        return director_schema.dump(genre), 200

    def put(self, gid):
        req_json = request.json
        genre = db.session.query(Genre).get(gid)
        if not genre:
            return f"There's no genre with id {gid}", 404
        genre.name = req_json.get('name')
        db.session.add(genre)
        db.session.commit()
        return f"Genre with id {gid} is changed", 204

    def patch(self, gid):
        req_json = request.json
        genre = db.session.query(Genre).get(gid)
        if not genre:
            return f"There's no genre with id {gid}", 404
        if 'name' in req_json:
            genre.name = req_json.get('name')
            db.session.add(genre)
            db.session.commit()
            return f"Genre with id {gid} is changed", 204

    def delete(self, gid):
        genre = db.session.query(Genre).get(gid)
        if not genre:
            return f"There's no genre with id {gid}", 404
        db.session.delete(genre)
        db.session.commit()
        return f"Genre with id {gid} is deleted", 204

app.run()