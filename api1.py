from flask import Blueprint
from flask_restplus import Api

from apis.movies import api as movie_api
from apis.votings import api as voting_api

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(
    blueprint,
    title="Vote For Movie API",
    version="0.1.0",
    description="A vote-for-movie API."
)

api.add_namespace(movie_api)
api.add_namespace(voting_api)
