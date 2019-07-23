from bson import ObjectId
from pymongo import MongoClient


class MovieService:
    def __init__(self):
        self._movie_collection = MongoClient().vote_for_movie.movies

    def get_all(self, genre, actor):
        query_object = {}

        if genre:
            query_object["genres"] = {"$all": [genre]}

        if actor:
            query_object["actors"] = {"$all": [actor]}

        return list(self._movie_collection.find(query_object))

    def get(self, movie_id):
        query_object = {
            "_id": ObjectId(movie_id)
        }

        return self._movie_collection.find_one(query_object)

    def find_and_rate(self, movie_id, mark):
        movie = self.get(movie_id)
        if not movie:
            return False

        movie["sumOfMarks"] += mark
        movie["numberOfMarks"] += 1

        self._movie_collection.replace_one(
            {"_id": ObjectId(movie_id)},
            movie
        )

        return True
