import json
import random
import uuid

from locust import HttpLocust, TaskSet, task


class BrowseResults(TaskSet):
    @task(30)
    def view_image(self):
        if self.parent.results:
            image_id = random.choice(self.parent.results)["id"]
            self.client.get(f"/image/{image_id}", name="/image/[id]")

    @task(10)
    def favorite_images(self):
        pass
        if self.parent.results:
            list_length = random.choice([2, 2, 2, 2, 2, 2, 2, 2, 6, 6, 6, 9])
            selected_images = self.parent.results[0:list_length]
            ids = [image["id"] for image in selected_images]
            self.client.post("/list", {"title": "Load test" + str(ids), "images": ids})

    @task(10)
    def shorten_link(self):
        _unique = str(uuid.uuid4())
        image_link = f"http://api-dev.openverse.engineering/list/{_unique}"
        self.client.post("/link", {"full_url": image_link})


class UserBehavior(TaskSet):
    tasks = {BrowseResults: 8}

    def __init__(self, parent):
        self.results = None
        self.query = None
        with open("./common_english_words.txt", "r") as f:
            self.common_words = f.read().splitlines()
        super().__init__(parent)

    @task(1000)
    def search(self):
        query_length = random.choice([1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 5])
        query = [random.choice(self.common_words) for _ in range(query_length)]
        query = ",".join(query)
        self.query = query
        response = self.client.get(
            f"/image/search?q={query}", name="/image/search?q=[keywords]"
        )
        self.results = json.loads(response.content.decode("utf-8"))["results"]


class SearchUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 3000
    max_wait = 9000
