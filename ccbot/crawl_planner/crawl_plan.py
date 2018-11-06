import logging as log
import psycopg2
import settings

"""
Plan an image validation crawl. A crawl plan determines which URLs need to be 
validated and sets appropriate rate limits for each content provider. The plan
can be fine-tuned by hand.
"""


def plan():
    with open('plan.yaml', 'w') as plan_file:
        pass


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
        cur.copy_to(url_file, table='image')
    cur.close()
    conn.close()


if __name__ == '__main__':
    log.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        level=log.INFO
    )
    # There are hundreds of millions of URLs, so they won't fit into RAM.
    log.info("Dumping remote image URLs to local disk...")
    dump_urls()
    log.info('Created url_dump.csv.')
    log.info('Planning crawl...')
    plan()
