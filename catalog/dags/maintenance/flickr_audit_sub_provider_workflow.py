"""
# Flickr Sub Provider Audit

Check the list of member institutions of the Flickr Commons for institutions that
have cc-licensed images and are not already configured as sub-providers for the Flickr
DAG. Report suggestions for new sub-providers to Slack.
"""

import logging
from typing import NamedTuple

from airflow import DAG
from airflow.exceptions import AirflowSkipException
from airflow.models import Variable
from airflow.operators.python import PythonOperator

from common.constants import DAG_DEFAULT_ARGS
from common.loader import provider_details as prov
from common.requester import DelayedRequester
from common.slack import send_alert
from providers.provider_api_scripts.flickr import LICENSE_INFO


logger = logging.getLogger(__name__)

DAG_ID = "flickr_audit_sub_provider_workflow"
MAX_ACTIVE = 1


class SuggestedSubProvider(NamedTuple):
    """
    A Flickr Commons institution which should be considered for addition as a
    Flickr sub-provider.

    name:     The name of the institution
    nsid:     The unique id of the institution
    cc_count: The number of CC-licensed images for this institution
    """

    name: str
    nsid: str
    cc_count: int


class FlickrSubProviderAuditor:
    endpoint = "https://www.flickr.com/services/rest"
    retries = 2

    # Institutions with fewer than this number of cc-licensed images will not be
    # recommended as a new sub provider.
    minimum_image_count = 300

    # NSIDs in this list should not be reported for consideration for
    # becoming a sub-provider.
    nsids_to_skip = [
        # TODO: Currently contains graphic medical imagery. Reconsider once
        # content safety progress is made.
        "61270229@N05",
        # TODO: Internet Archive Book Images. Latest images were uploaded in
        # 2015 and have not been previously ingested. Reconsider adding this
        # subprovider when we have the ability to backfill these images.
        # https://github.com/WordPress/openverse/issues/3490#issuecomment-1857072575  # noqa: E501
        "126377022@N07",
    ]

    def __init__(self):
        self.api_key = Variable.get("API_KEY_FLICKR")
        self.requester = DelayedRequester(headers={"Accept": "application/json"})
        self.base_params = {
            "api_key": self.api_key,
            "format": "json",
            "nojsoncallback": 1,
        }
        # Get the list of institutions that are already configured for Flickr
        self.current_institutions = set().union(*prov.FLICKR_SUB_PROVIDERS.values())

    def get_institutions(self):
        response_json = self.requester.get_response_json(
            self.endpoint,
            self.retries,
            query_params={
                "method": "flickr.commons.getInstitutions",
                **self.base_params,
            },
        )
        if response_json:
            return response_json.get("institutions", {}).get("institution", [])

        return None

    def get_cc_image_count(self, name, nsid):
        """Return the number of cc licensed images for this institution."""

        # The Flickr API is consistently returning a count of '0' when querying for
        # images matching multiple license types from a particular user. It gives more
        # accurate results when you query for one license at a time, however, so we have
        # to make separate requests for each license type.
        logger.info(f"Checking records for {name}")

        count = 0
        for license in LICENSE_INFO.keys():
            response_json = self.requester.get_response_json(
                self.endpoint,
                self.retries,
                query_params={
                    "method": "flickr.photos.search",
                    "media": "photos",
                    "license": license,
                    "user_id": nsid,
                    "safe_search": 1,
                    **self.base_params,
                },
            )

            if response_json:
                sub_total = response_json.get("photos", {}).get("total", 0)
                if sub_total > 0:
                    logger.info(f"Found {sub_total} records for license type {license}")
                count += sub_total

        logger.info(f"TOTAL COUNT for {name}: {count}")
        return count

    def get_new_institutions_with_cc_licensed_images(self):
        new_institutions_with_cc_images: list[SuggestedSubProvider] = []

        # Get the full list of Flickr commons institutions from the API
        institutions = self.get_institutions()

        for institution in institutions:
            name = institution.get("name", {}).get("_content")
            nsid = institution.get("nsid")

            if not name or not nsid:
                continue

            # Skip institutions that are already configured as sub-providers
            if nsid in self.current_institutions:
                continue

            # Skip institutions that have been added to the nsids_to_skip list
            if nsid in self.nsids_to_skip:
                continue

            # Skip institutions that do not have enough cc-licensed images. Many
            # institutions have "no known copyright restrictions", but no cc
            # license. See https://www.flickr.com/commons/usage
            cc_count = self.get_cc_image_count(name, nsid)
            if cc_count < self.minimum_image_count:
                continue

            # Otherwise, consider this institution for addition as a
            # sub-provider.
            new_institutions_with_cc_images.append(
                SuggestedSubProvider(name, nsid, cc_count)
            )

        return new_institutions_with_cc_images


def audit_flickr_sub_providers():
    auditor = FlickrSubProviderAuditor()

    potential_sub_providers = auditor.get_new_institutions_with_cc_licensed_images()
    if not potential_sub_providers:
        raise AirflowSkipException("No new potential sub-providers were identified.")

    message = "Consider adding the following sub-providers for Flickr:"
    for name, nsid, cc_count in potential_sub_providers:
        message += "\n"
        message += f"{name}: {nsid} _({cc_count} cc-licensed images)_"

    send_alert(message, dag_id=DAG_ID, username="Flickr SubProvider Suggestions")
    return message


dag = DAG(
    dag_id=DAG_ID,
    default_args=DAG_DEFAULT_ARGS,
    max_active_runs=MAX_ACTIVE,
    catchup=False,
    schedule="@monthly",
    doc_md=__doc__,
    tags=["maintenance"],
)

with dag:
    PythonOperator(
        task_id="audit_flickr_sub_providers",
        python_callable=audit_flickr_sub_providers,
    )
