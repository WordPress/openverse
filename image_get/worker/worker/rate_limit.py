"""
Every TLD (e.g. flickr.com, metmuseum.org) gets a token bucket. Before a worker
crawls an image from a domain, it must acquire a token from the right bucket.
If there aren't enough tokens, the request will block until it has been
replenished.

When a new domain is discovered, the crawler will collect samples to determine a
baseline time to first byte (TTFB), which is used to measure whether we are
placing any strain on a server. Once a baseline has been established, we will
slowly ramp up the request rate until there is noticeable strain in the form of
an increase in TTFB or errors are returned (such as 429 Rate Limit Exceeded).

The crawler cluster uses a masterless model, meaning every worker will try to
manage the token buckets. Race conditions are prevented with distributed locks.
To minimize contention and blocking, we should lock optimistically whenever
feasible.
"""


class RateLimitedClientSession:
    """
    Wraps aiohttp.ClientSession and enforces rate limits.
    """
    def __init__(self, client):
        self.client = client

    async def _get_token(self, tld):
        pass

    async def get(self, url):
        return await self.client.get(url)
