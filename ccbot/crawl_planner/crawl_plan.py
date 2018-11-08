import logging as log
import psycopg2
import settings
import json
import csv
import requests
import yaml
from collections import defaultdict
from urlparse import urlparse
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
    VERY_HEAVY = 4
    # MAXIMUM_OVERDRIVE_BABY = 5


# Corresponds to Scrapy Cluster QUEUE_WINDOW setting.
# Do not change this unless you really know what you're doing.
RATE_LIMIT_WINDOW = 60


# Thresholds for rate limit strategies. For example, a content provider with
# 9,999 images will receive VERY_LIGHT crawler load, while one with 10,000 will
# receive LIGHT crawler load.
RATE_LIMIT_STRATEGY_THRESHOLDS = [
    (1, RateLimitStrategies.VERY_LIGHT),
    (10000, RateLimitStrategies.LIGHT),
    (100000, RateLimitStrategies.MODERATE),
    (1000000, RateLimitStrategies.HEAVY),
    (5000000, RateLimitStrategies.VERY_HEAVY),
    # (20000000, RateLimitStrategies.MAXIMUM_OVERDRIVE_BABY)
]

# Requests per second associated with each strategy
STRATEGY_RPS = {
    RateLimitStrategies.VERY_LIGHT: settings.VERY_LIGHT_RPS,
    RateLimitStrategies.LIGHT: settings.LIGHT_RPS,
    RateLimitStrategies.MODERATE: settings.MODERATE_RPS,
    RateLimitStrategies.HEAVY: settings.HEAVY_RPS,
    RateLimitStrategies.VERY_HEAVY: settings.VERY_HEAVY_RPS,
    # RateLimitStrategies.MAXIMUM_OVERDRIVE_BABY: settings.MAX_RPS
}


def get_strategy(num_images):
    """
    Given the number of images a provider has, find the appropriate rate limit
    strategy.
    """
    strategy = RateLimitStrategies.VERY_LIGHT
    for pair in RATE_LIMIT_STRATEGY_THRESHOLDS:
        threshold, strat = pair
        if num_images >= threshold:
            strategy = strat
    return strategy


def plan():
    """
    Synthesize all collected information and produce a crawl plan YAML.
    """
    log.info('Requesting content provider statistics...')
    stats_request = requests.get(
        settings.CCCATALOG_API_URL + '/statistics/image'
    )
    stats_json = json.loads(stats_request.text)
    stats_dict = {}
    for pair in stats_json:
        provider = pair['provider_name']
        n_images = pair['image_count']
        stats_dict[provider] = n_images
    log.info("Associating image domain names with providers...")
    provider_info = get_provider_info("url_dump.csv")
    provider_domains, num_urls = provider_info

    plan_config = {
        # Extra information for human readers
        'info': {},
        # Actual configuration sent to Scrapy Cluster crawlers
        'domains': {}
    }
    info = {
        'providers': {},
        # Total number of URLs in the URL dump file.
        'num_urls': num_urls
    }
    for provider in provider_domains:
        # Choose rate limit strategy based on amount of content
        image_count = stats_dict[provider]
        strategy = get_strategy(image_count)
        provider_rps = STRATEGY_RPS[strategy]
        info['providers'][provider] = {}
        info['providers'][provider]['requests_per_second'] = provider_rps
        for domain in provider_domains[provider]:
            plan_config['domains'] = {
                domain: {
                    'window': RATE_LIMIT_WINDOW,
                    'hits': STRATEGY_RPS[strategy] * RATE_LIMIT_WINDOW
                }
            }
    plan_config['info'] = info
    with open('crawl_plan.yml', 'w') as plan_file:
        yaml.dump(plan_config, plan_file, default_flow_style=False)


def get_provider_info(filename):
    """
    Given a URL dump csv, associate each domain with a provider. This is
    necessary because image CDNs are often not on the same domain as the parent
    website.
    """
    provider_domains = defaultdict(set)
    num_urls = 0
    with open(filename, 'r') as url_file:
        reader = csv.DictReader(url_file)
        for row in reader:
            netloc = urlparse(row['url']).netloc
            netloc = netloc.replace('www.', "")
            provider = row['provider']
            provider_domains[provider].add(netloc)
            num_urls += 1
    return provider_domains, num_urls


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
        query = "COPY (select url, identifier, provider from image) " \
                "TO STDOUT WITH CSV HEADER"
        cur.copy_expert(query, url_file)
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
    log.info('Planning crawl...')
    plan()
    log.info('Successfully produced crawl_plan.yml and url_dump.csv!')
