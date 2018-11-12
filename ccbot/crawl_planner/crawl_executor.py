import yaml
import requests
import sys
import settings
import json
import logging as log
import csv
from uuid import uuid4
from confluent_kafka import Producer

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
    except requests.exceptions.RequestException:
        log.error('Failed to reach Scrapy Cluster REST endpoint.')
        return False
    return True


def set_rate_limits(crawl_plan, crawl_id):
    """
    Use the Scrapy Cluster REST API to set rate limits for each domain.
    """
    status_codes = set()
    for domain in crawl_plan['domains']:
        req = {
            'appid': "crawl_planner",
            'uuid': str(uuid4()),
            'domain': domain,
            'action': "domain-update",
            'crawlid': crawl_id,
            'window': crawl_plan['domains'][domain]['window'],
            'hits': crawl_plan['domains'][domain]['hits'],
        }
        response = requests.post(settings.CLUSTER_REST_URL + '/feed', json=req)
        status_codes.add(response)

    for code in status_codes:
        if 200 > code > 299:
            log.error('Failed to set rate limits. Aborting crawl.')
            sys.exit(1)


def schedule_crawl(url_csv_filename, crawl_id):
    """
    Consume a URL dump CSV and produce Kafka messages.

    :param url_csv_filename: The name of the URL CSV dump.
    :param crawl_id: A UUID identifying the crawl. Used to control the crawl.
    :return:
    """

    p = Producer({'bootstrap.servers': settings.CLUSTER_BROKER_HOSTS})
    with open(url_csv_filename, 'r') as url_file:
        reader = csv.DictReader(url_file)
        for idx, row in enumerate(reader):
            p.poll(0)
            msg = {
                'url': row['url'],
                'appid': "crawl_planner",
                'crawlid': crawl_id,
                'spiderid': 'validator',
                'attrs': row['identifier']
            }
            p.produce(settings.CLUSTER_INCOMING_TOPIC, msg)


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
    log.info('Setting rate limits...')
    set_rate_limits(parsed_plan)
    crawl_name = str(uuid4())
    log.info('Scheduling crawl {}...'.format(crawl_name))
    schedule_crawl('url_dump.csv', crawl_name)
