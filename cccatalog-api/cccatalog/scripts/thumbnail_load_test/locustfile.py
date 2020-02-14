import csv
import gevent.queue
import gevent.pool
import grequests
import statistics
import json
import datetime
from locust import HttpLocust, TaskSet, task, between
from collections import defaultdict
"""
Swarm the API server with requests for thumbnails.

Bear in mind that performance will be dramatically different if the cache has
been warmed up. You want to test dynamic resizing performance, not cache 
retrieval, so empty the thumbnail S3 bucket before running this against a live
server.
"""
PROXY_URL = "https://api-dev.creativecommons.engineering/t/600"
url_queue = gevent.queue.Queue()
provider_counts = defaultdict(int)
url_provider = {}
thumb_statuses = defaultdict(int)
response_times = []

with open('url_dump.csv') as urls_csv:
    reader = csv.reader(urls_csv)
    for row in reader:
        url = row[0]
        provider = row[1]
        url_queue.put((url, provider))
        url_provider[url] = provider
        provider_counts[provider] += 1


def _thumb_failure(request, exception):
    print(f'Failed to load thumbnail! Req, reason: {request}, {exception}')


def _print_current_stats():
    mean_response_time = statistics.mean(response_times)
    failed = 0
    successful = 0
    for status in thumb_statuses:
        num_statuses = thumb_statuses[status]
        if status >= 300:
            failed += num_statuses
        else:
            successful += num_statuses

    out = {
        'timestamp': str(datetime.datetime.now()),
        'mean_response_time': mean_response_time,
        'successful': successful,
        'failed': failed
    }
    print(json.dumps(out))


class ThumbTask(TaskSet):
    @task
    def load_thumbs(self):
        reqs = []
        providers = []
        for _ in range(20):
            base_url, provider = url_queue.get()
            providers.append(provider)
            proxied_url = f'{PROXY_URL}/{base_url}'
            print(proxied_url)
            reqs.append(grequests.get(proxied_url))
        thumb_responses = grequests.map(reqs, exception_handler=_thumb_failure)
        for resp in thumb_responses:
            response_times.append(resp.elapsed.total_seconds())
            thumb_statuses[resp.status_code] += 1
        _print_current_stats()


class ThumbLocust(HttpLocust):
    wait_time = between(5, 10)
    task_set = ThumbTask
