from flask import request
from flask_restplus import Namespace, Resource, fields

from .services import MovieService

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

movie_service = MovieService()


@api.route("/")
class MovieList(Resource):
    @api.marshal_list_with(movie_fields)
    def get(self):
        movies = movie_service.get_all(
            request.args.get("genre"),
            request.args.get("actor")
        )

        return movies


def get_movie_or_404(movie_id):
    movie = movie_service.get(movie_id)
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

        is_found = movie_service.find_and_rate(
            movie_id, movie_action["data"]["mark"]
        )

        if not is_found:
            api.abort(404, f"Movie {movie_id} not found.")

        return {"message": "Action performed."}, 201
