from flask_restplus import Namespace, Resource, fields
from pymongo import MongoClient

api = Namespace("movies", description="Movies related operations")

movie_fields = api.model("Movie", {
    "id": fields.String(readonly=True, attribute="_id"),
    "title": fields.String(required=True),
    "year": fields.Integer(),
    "genres": fields.List(fields.String(), required=True),
    "actors": fields.List(fields.String(), required=True)
})

movie_collection = MongoClient().vote_for_movie.movies


@api.route("/")
class MovieList(Resource):
    @api.marshal_list_with(movie_fields)
    def get(self):
        return list(movie_collection.find())
