from bson import ObjectId
from flask import request
from flask_restplus import Namespace, Resource, fields
from pymongo import MongoClient

api = Namespace("movies", description="Movies related operations")

movie_fields = api.model("Movie", {
    "id": fields.String(readonly=True, attribute="_id"),
    "title": fields.String(required=True),
    "year": fields.Integer(),
    "genres": fields.List(fields.String(), required=True),
    "actors": fields.List(fields.String(), required=True),
    "sumOfMarks": fields.Integer(readonly=True),
    "numberOfMarks": fields.Integer(readonly=True)
})

mark_data_fields = api.model("Mark Data", {
    "mark": fields.Integer(required=True, min=1, max=100, example=75)
})

movie_action_fields = api.model("Movie Action", {
    "type": fields.String(required=True, example="rate"),
    "data": fields.Nested(mark_data_fields, required=True)
})

movie_collection = MongoClient().vote_for_movie.movies


@api.route("/")
class MovieList(Resource):
    @api.marshal_list_with(movie_fields)
    def get(self):
        query_object = {}

        genre = request.args.get("genre")
        if genre:
            query_object["genres"] = {"$all": [genre]}

        actor = request.args.get("actor")
        if actor:
            query_object["actors"] = {"$all": [actor]}

        return list(movie_collection.find(query_object))


def get_movie_or_404(movie_id):
    movie = movie_collection.find_one({"_id": ObjectId(movie_id)})
    if not movie:
        api.abort(404, f"Movie {movie_id} not found.")
    return movie


@api.route("/<movie_id>")
class MovieDetail(Resource):
    @api.marshal_with(movie_fields)
    def get(self, movie_id):
        return get_movie_or_404(movie_id)


@api.route("/<movie_id>/actions/")
class MovieActionList(Resource):
    @api.expect(movie_action_fields)
    def post(self, movie_id):
        movie_action = api.payload

        if movie_action["type"] != "rate":
            api.abort(400, "Action type not supported.")

        movie = get_movie_or_404(movie_id)

        movie["sumOfMarks"] += movie_action["data"]["mark"]
        movie["numberOfMarks"] += 1

        movie_collection.replace_one(
            {"_id": ObjectId(movie_id)},
            movie
        )

        return {"message": "Action performed."}, 201
