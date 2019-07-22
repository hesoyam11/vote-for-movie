from datetime import datetime, timezone

import dateutil.parser
from bson.objectid import ObjectId
from flask_restplus import Namespace, Resource, fields
from pymongo import MongoClient

api = Namespace("votings", description="Votings related operations")

choice_fields = api.model("Choice", {
    "id": fields.Integer(readonly=True),
    "title": fields.String(required=True),
    "votes": fields.Integer(readonly=True)
})

voting_fields = api.model("Voting", {
    "id": fields.String(readonly=True, attribute="_id"),
    "choices": fields.List(fields.Nested(choice_fields)),
    "currentVotes": fields.Integer(readonly=True),
    "maxVotes": fields.Integer(min=1),
    "endDateTime": fields.DateTime(dt_format="iso8601")
})

CHOICE_ACTION_TYPES = ("vote",)

choice_action_fields = api.model("Choice Action", {
    "type": fields.String(required=True, default="vote", example="vote")
})

voting_collection = MongoClient().vote_for_movie.votings


@api.route("/")
class VotingList(Resource):
    @api.expect(voting_fields)
    @api.marshal_with(voting_fields, code=201)
    def post(self):
        if "id" in api.payload:
            del api.payload["id"]
        choice_id_counter = 0
        for choice in api.payload["choices"]:
            choice["id"] = choice_id_counter
            choice_id_counter += 1
            choice["votes"] = 0
        api.payload["currentVotes"] = 0
        result = voting_collection.insert_one(api.payload)
        voting = voting_collection.find_one({"_id": result.inserted_id})
        return voting, 201


def get_voting_or_404(voting_id):
    voting = voting_collection.find_one({"_id": ObjectId(voting_id)})
    if not voting:
        api.abort(404, f"Voting {voting_id} not found.")
    return voting


@api.route("/<string:voting_id>")
class Voting(Resource):
    @api.marshal_with(voting_fields)
    def get(self, voting_id):
        return get_voting_or_404(voting_id)


@api.route("/<string:voting_id>/choices/<int:choice_id>/actions/")
class ChoiceActionList(Resource):
    @api.expect(choice_action_fields)
    def post(self, voting_id, choice_id):
        action_type = api.payload["type"]

        if action_type not in CHOICE_ACTION_TYPES:
            api.abort(400, "Action type not supported.")

        voting = get_voting_or_404(voting_id)

        end_datetime = voting.get("endDateTime", None)
        max_votes = voting.get("maxVotes", None)

        end_datetime = dateutil.parser.parse(end_datetime) \
            if end_datetime else None

        if end_datetime and end_datetime >= datetime.now(timezone.utc) or \
                max_votes and voting["currentVotes"] >= max_votes:
            api.abort(403, "The voting is closed!")

        selected_choice = None
        for choice in voting["choices"]:
            if choice["id"] == choice_id:
                selected_choice = choice
                break
        if not selected_choice:
            api.abort(404, f"Choice {choice_id} not found.")

        if action_type == "vote":
            selected_choice["votes"] += 1
            voting["currentVotes"] += 1

        result = voting_collection.replace_one(
            {"_id": ObjectId(voting_id)},
            voting
        )

        if result.modified_count != 1:
            api.abort(500, "Database error.")

        return {"message": "Action is performed."}, 201
