"""
Content Provider:       Healthcheck

ETL Process:            Use the API to identify all openly licensed media.

Output:                 TSV file containing the media metadata.

Notes:                  {{API URL}}
                        No rate limit specified.
"""
import logging
from time import sleep

from util.loader import provider_details as prov


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


PROVIDER = prov.HEALTHCHECK_DEFAULT_PROVIDER


def main():
    logger.info("Healthcheck DAG starting; this will run for two minutes...")
    for i in range(120):  # run for two minutes
        logger.info(f"Healthcheck iteration {i}...")
        sleep(1)

    logger.info("Terminated!")


if __name__ == "__main__":
    main()
