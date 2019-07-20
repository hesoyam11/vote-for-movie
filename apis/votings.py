from datetime import datetime

from flask_restplus import Namespace, Resource, fields

api = Namespace("votings", description="Votings related operations")

choice_fields = api.model("Choice", {
    "id": fields.Integer(readonly=True),
    "title": fields.String(required=True),
    "votes": fields.Integer(readonly=True, default=0)
})

voting_fields = api.model("Voting", {
    "id": fields.String(readonly=True),
    "choices": fields.List(fields.Nested(choice_fields)),
    "currentVotes": fields.Integer(readonly=True),
    "maxVotes": fields.Integer,
    "endDateTime": fields.DateTime(dt_format="iso8601")
})

CHOICE_ACTION_TYPES = ("vote",)

choice_action_fields = api.model("Choice Action", {
    "type": fields.String(required=True)
})


class VotingDAO:
    def __init__(self):
        self.counter = 0
        self.votings = []

    def create(self, data):
        voting = data

        self.counter += 1
        voting["id"] = str(self.counter)

        choice_id_counter = 0
        for choice in voting["choices"]:
            choice["id"] = choice_id_counter
            choice_id_counter += 1

        self.votings.append(voting)
        return voting

    def get(self, voting_id):
        for voting in self.votings:
            if voting["id"] == voting_id:
                return voting
        return None


voting_dao = VotingDAO()
voting_dao.create({
    "choices": [
        {
            "title": "Ice Age 2",
            "votes": 2
        },
        {
            "title": "Terminator",
            "votes": 5
        }
    ],
    "currentVotes": 7,
    "maxVotes": 10,
    "endDateTime": None
})


@api.route("/")
class VotingList(Resource):
    @api.marshal_list_with(voting_fields)
    def get(self):
        return voting_dao.votings

    @api.expect(voting_fields)
    @api.marshal_with(voting_fields, code=201)
    def post(self):
        return voting_dao.create(api.payload), 201


def get_voting_or_404(voting_id):
    voting = voting_dao.get(voting_id)
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
    @api.marshal_with(choice_fields, code=201)
    def post(self, voting_id, choice_id):
        action_type = api.payload["type"]

        if action_type not in CHOICE_ACTION_TYPES:
            api.abort(400, f"Action type not supported.")

        voting = get_voting_or_404(voting_id)

        end_datetime = voting.get("endDateTime", None)
        max_votes = voting.get("maxVotes", None)

        if end_datetime and end_datetime >= datetime.now() or \
                max_votes and voting["currentVotes"] >= max_votes:
            api.abort(403, f"The voting is closed!")

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

        return selected_choice, 201
