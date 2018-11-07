import logging as log
import psycopg2
import settings
import json
import requests
from enum import Enum

"""
Produce an image validation crawl plan. A crawl plan determines which URLs need 
to be validated and sets appropriate rate limits for each content provider. The
plan can be adjusted by hand if need be. Regardless of the rate limits set by 
this plan, crawlers will respect robots.txt.

Network dependencies: Direct access to the cccatalog database; access to API
"""


class RateLimitStrategies(Enum):
    VERY_LIGHT = 0
    LIGHT = 1
    MODERATE = 2
    HEAVY = 3
    MAXIMUM_OVERDRIVE_BABY = 4


# Thresholds for rate limit strategies. For example, a content provider with
# 99 images will receive VERY_LIGHT crawler load, while one with 100 will
# receive LIGHT crawler load.
RATE_LIMIT_STRATEGY_THRESHOLDS = [
    (1, RateLimitStrategies.VERY_LIGHT),
    (10000, RateLimitStrategies.LIGHT),
    (100000, RateLimitStrategies.MODERATE),
    (1000000, RateLimitStrategies.HEAVY),
    (5000000, RateLimitStrategies.VERY_HEAVY),
    (20000000, RateLimitStrategies.MAXIMUM_OVERDRIVE_BABY)
]

# Requests per second associated with each strategy
STRATEGY_RPS = {
    RateLimitStrategies.VERY_LIGHT: settings.VERY_LIGHT_RPS,
    RateLimitStrategies.LIGHT: settings.LIGHT_RPS,
    RateLimitStrategies.MODERATE: settings.MODERATE_RPS,
    RateLimitStrategies.HEAVY: settings.HEAVY_RPS,
    RateLimitStrategies.VERY_HEAVY: settings.VERY_HEAVY_RPS,
    RateLimitStrategies.MAXIMUM_OVERDRIVE_BABY: settings.MAX_RPS
}


def get_strategy(num_images):
    strategy = RateLimitStrategies.VERY_LIGHT
    for pair in RATE_LIMIT_STRATEGY_THRESHOLDS:
        threshold, strat = pair
        if num_images >= threshold:
            strategy = strat
    return strategy


def plan():
    log.info('Requesting content provider statistics...')
    stats_request = requests.get(
        settings.CCCATALOG_API_URL + '/statistics/image'
    )
    stats_json = json.loads(stats_request.text)
    for provider in stats_json:
        # Choose rate limit strategy based on amount of content
        provider_name = provider['provider_name']
        image_count = int(provider['image_count'])
        strategy = get_strategy(image_count)


    with open('plan.yaml', 'w') as plan_file:
        pass


def get_provider_url_map(filename):
    with open(filename, 'r') as url_file:



def dump_urls():
    conn = psycopg2.connect(
        dbname='openledger',
        user='deploy',
        password=settings.DATABASE_PASSWORD,
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        connect_timeout=5
    )
    conn.set_session(readonly=True)
    cur = conn.cursor()
    with open('url_dump.csv', 'w') as url_file:
        cur.copy_to(url_file, "select url, identifier, provider from image")
    cur.close()
    conn.close()


if __name__ == '__main__':
    log.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        level=log.INFO
    )
    host = settings.DATABASE_HOST
    log.info("Dumping remote image URLs on {} to local disk...".format(host))
    dump_urls()
    log.info('Created url_dump.csv.')
    log.info("Associating domain names with providers...")
    provider_url_map = get_provider_url_map("url_dump.csv")
    log.info('Planning crawl...')
    plan()
