from flask_restplus import Namespace, Resource, fields

api = Namespace("movies", description="Movies related operations")

movie_fields = api.model("Movie", {
    "id": fields.String(readOnly=True),
    "title": fields.String(required=True),
    "year": fields.Integer(),
    "genres": fields.List(fields.String(), required=True),
    "actors": fields.List(fields.String(), required=True)
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
movie_dao.create({
    "title": "Terminator", "year": 1984,
    "genres": ["Action", "Sci-Fi", "Fantasy"],
    "actors": ["Schwarzenegger"]
})
movie_dao.create({
    "title": "Forrest Gump", "year": 1994,
    "genres": ["Drama", "Romance"],
    "actors": ["Hanks"]
})
movie_dao.create({
    "title": "Harry Potter and the Sorcerer's Stone",
    "genres": ["Adventure", "Family", "Fantasy"],
    "actors": ["Radcliffe", "Watson"]
})


@api.route("/")
class MovieList(Resource):
    @api.marshal_list_with(movie_fields)
    def get(self):
        return movie_dao.movies

    @api.expect(movie_fields)
    @api.marshal_with(movie_fields, code=201)
    def post(self):
        return movie_dao.create(api.payload), 201
