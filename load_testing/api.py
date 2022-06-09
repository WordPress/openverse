from random import randrange

from locust import HttpUser, task
from utils.dictionary import random_words


class APIUser(HttpUser):
    @task
    def images_stats(self):
        self.client.get("/v1/images/stats")

    @task
    def audio_stats(self):
        self.client.get("/v1/audio/stats")

    def _do_search(self, type, term):
        self.client.get(f"/v1/{type}?q={term}")

    @task
    def image_search(self):
        for word in random_words(10):
            self._do_search("images", word)

    @task
    def audio_search(self):
        for word in random_words(10):
            self._do_search("audio", word)
