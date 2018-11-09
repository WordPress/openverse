import yaml
import requests
import sys
import settings
import json
import logging as log
from uuid import uuid4

"""
Execute a crawl plan produced by crawl_plan.py.
"""


def cluster_healthcheck():
    """
    :return: True if Scrapy Cluster is fully operational, else False
    """
    try:
        r = requests.get(settings.CLUSTER_REST_URL)
        response = json.loads(r.text)
        if (
            not response['kafka_connected'] or
            not response['redis_connected'] or
            response['node_health'] != 'GREEN'
           ):
            return False
    except requests.exceptions.RequestException as e:
        log.error('Failed to reach Scrapy Cluster REST endpoint.')
        return False
    return True


def set_rate_limits(crawl_plan, crawl_uuid):
    """
    Use the Scrapy Cluster REST API to set rate limits for each domain.
    """
    status_codes = set()
    log.info('Setting rate limits...')
    for domain in crawl_plan['domains']:
        req = {
            "appid": "crawl_planner",
            "domain": domain,
            "action": "domain-update",
            "window": crawl_plan['domains'][domain]['window'],
            "hits": crawl_plan['domains'][domain]['hits'],
        }
        response = requests.post(settings.CLUSTER_REST_URL + '/feed', json=req)
        status_codes.add(response)
    for code in status_codes:
        if 200 > code > 299:
            log.error('Failed to set rate limits. Aborting crawl.')
            sys.exit(1)


if __name__ == '__main__':
    log.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        level=log.INFO
    )
    log.info("Performing cluster healthcheck")
    if not cluster_healthcheck():
        log.error("Cluster healthcheck failed. Aborting crawl.")
        sys.exit(1)
    with open("crawl_plan.yml") as plan_file:
        parsed_plan = yaml.load(plan_file)
    # Unique identifier associated with one executed crawl plan.
    # Used for debugging and audit purposes.
    crawl_uuid = str(uuid4())
    log.info('Crawl ID: ' + crawl_uuid)
    set_rate_limits(parsed_plan, crawl_uuid)
