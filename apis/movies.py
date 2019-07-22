from flask_restplus import Namespace, Resource, fields
from pymongo import MongoClient

api = Namespace("movies", description="Movies related operations")

movie_fields = api.model("Movie", {
    "id": fields.String(readOnly=True, attribute="_id"),
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

    @api.expect(movie_fields)
    @api.marshal_with(movie_fields, code=201)
    def post(self):
        if "id" in api.payload:
            del api.payload["id"]
        result = movie_collection.insert_one(api.payload)
        movie = movie_collection.find_one({"_id": result.inserted_id})
        return movie, 201
