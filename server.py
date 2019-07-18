from flask import Flask
from flask_restplus import Api, Resource, fields

app = Flask(__name__)
api = Api(app)

movies_namespace = api.namespace("movies")

movie_model = api.model("Movie", {
    "id": fields.String(readOnly=True),
    "title": fields.String(required=True),
    "year": fields.Integer(),
    "genres": fields.List(
        fields.String(),
        required=True
    )
})


class MovieDAO:
    def __init__(self):
        self.counter = 0
        self.movies = []

    def create(self, data):
        movie = data
        movie["id"] = self.counter = self.counter + 1
        self.movies.append(movie)
        return movie


movie_dao = MovieDAO()
movie_dao.create({"title": "Terminator", "year": 1984,
                  "genres": ["Action", "Sci-Fi", "Fantasy"]})
movie_dao.create({"title": "Forrest Gump", "year": 1994,
                  "genres": ["Drama", "Romance"]})
movie_dao.create({"title": "Harry Potter and the Sorcerer's Stone",
                  "genres": ["Adventure", "Family", "Fantasy"]})


@movies_namespace.route("/")
class MovieList(Resource):
    @movies_namespace.marshal_list_with(movie_model)
    def get(self):
        return movie_dao.movies

    @movies_namespace.expect(movie_model)
    @movies_namespace.marshal_with(movie_model, code=201)
    def post(self):
        return movie_dao.create(api.payload), 201


if __name__ == "__main__":
    app.run(debug=True)
