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
Swarm the API server with async requests for thumbnails. Requires `url_dump.csv`
in the same directory as the script. It is intentionally omitted from source
control.

The format of the csv is:
url,provider
https://example.com,exampleprovider
http://secondexample.com,secondprovider
. . .

To prepare the server for testing:
    - Ensure that the hardware allocation matches production.
    - Disable referer origin limiting in the imageproxy server.
    - Empty the S3 thumbnail cache bucket.

To run the test:
`locust`
Open the web interface and start a test with the desired number of workers.
Watch the console for updates on the progress of the test and the number of
successful vs failed thumbnails.

Optionally rerun the test after the cache has been warmed up.
"""
PROXY_URL = "https://api-dev.creativecommons.engineering/t/600/"

url_queue = gevent.queue.Queue()
provider_counts = defaultdict(int)
url_provider = {}
thumb_statuses = defaultdict(int)
statuses_by_provider = {}
response_times = []


with open('url_dump.csv') as urls_csv:
    reader = csv.reader(urls_csv)
    for row in reader:
        if row[0] == 'url':
            continue
        url = row[0]
        provider = row[1]
        url_queue.put((url, provider))
        url_provider[url] = provider
        provider_counts[provider] += 1


def print_current_stats():
    """
    Re-compute and print current thumbnail statistics.
    """
    mean_response_time = statistics.mean(response_times)
    failed = 0
    successful = 0
    for status in thumb_statuses:
        num_statuses = thumb_statuses[status]
        if status >= 300 and status != 404:
            failed += num_statuses
        else:
            successful += num_statuses

    out = {
        'timestamp': str(datetime.datetime.now()),
        'mean_response_time': mean_response_time,
        'successful': successful,
        'failed': failed,
        'statuses': thumb_statuses,
        'provider_statuses': statuses_by_provider
    }
    print(json.dumps(out))


def record_stats(responses, providers):
    for idx, resp in enumerate(responses):
        response_times.append(resp.elapsed.total_seconds())
        thumb_statuses[resp.status_code] += 1
        provider = providers[idx]
        if provider not in statuses_by_provider:
            statuses_by_provider[provider] = defaultdict(int)
        statuses_by_provider[provider][resp.status_code] += 1


class ThumbTask(TaskSet):
    @task
    def load_thumbs(self):
        reqs = []
        providers = []
        for _ in range(20):
            base_url, provider = url_queue.get()
            providers.append(provider)
            proxied_url = f'{PROXY_URL}{base_url}'
            reqs.append(grequests.get(proxied_url))
        thumb_responses = grequests.map(reqs)
        record_stats(thumb_responses, providers)
        print_current_stats()


class ThumbLocust(HttpLocust):
    """
    Load a page's worth of thumbnails every 3 to 6 seconds.
    """
    wait_time = between(3, 6)
    task_set = ThumbTask
