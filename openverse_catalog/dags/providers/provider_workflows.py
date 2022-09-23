import importlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional, Sequence, Type

from providers.provider_api_scripts.brooklyn_museum import BrooklynMuseumDataIngester
from providers.provider_api_scripts.cleveland_museum import ClevelandDataIngester
from providers.provider_api_scripts.finnish_museums import FinnishMuseumsDataIngester
from providers.provider_api_scripts.inaturalist import INaturalistDataIngester
from providers.provider_api_scripts.metropolitan_museum import MetMuseumDataIngester
from providers.provider_api_scripts.museum_victoria import VictoriaDataIngester
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester
from providers.provider_api_scripts.science_museum import ScienceMuseumDataIngester
from providers.provider_api_scripts.stocksnap import StockSnapDataIngester
from providers.provider_api_scripts.wikimedia_commons import (
    WikimediaCommonsDataIngester,
)


@dataclass
class ProviderWorkflow:
    """
    Required Arguments:

    provider_script:  string path for the provider_script file whose main
                      function is to be run. If the optional argument
                      `dated` is True, then the function must take a
                      single parameter (date) which will be a string of
                      the form 'YYYY-MM-DD'. Otherwise, the function
                      should take no arguments.

    Optional Arguments:

    dag_id:             string giving a unique id of the DAG to be created. By
                        default this will be set to the name of the provider_script,
                        appended with 'workflow'.
    ingestion_callable: ProviderDataIngester class whose `ingest_records` method is
                        to be run. Temporarily, may also be a `main` function for
                        providers that have not yet been refactored. TODO: Remove this
                        comment when refactors are completed.
    default_args:       dictionary which is passed to the airflow.dag.DAG
                        __init__ method and used to optionally override the
                        DAG_DEFAULT_ARGS.
    start_date:         datetime.datetime giving the first valid execution
                        date of the DAG.
    max_active_runs:    integer that sets the number of dagruns of this DAG
                        which can be run in parallel.
    max_active_tasks:   integer that sets the number of tasks which can
                        run simultaneously for this DAG.
                        It's important to keep the rate limits of the
                        Provider API in mind when setting this parameter.
    schedule_string:    string giving the schedule on which the DAG should
                        be run.  Passed to the airflow.dag.DAG __init__
                        method.
    dated:              boolean giving whether the `main_function` takes a
                        string parameter giving a date (i.e., the date for
                        which data should be ingested).
    pull_timeout:       datetime.timedelta giving the amount of time a given data
                        pull may take.
    load_timeout:       datetime.timedelta giving the amount of time the load_data
                        task may take.
    doc_md:             string which should be used for the DAG's documentation markdown
    media_types:        list describing the media type(s) that this provider handles
                        (e.g. `["audio"]`, `["image", "audio"]`, etc.)
    create_preingestion_tasks: callable that returns an airflow task or task group to
                        to run any necessary pre-ingestion tasks, such as loading bulk
                        data from S3
    create_postingestion_tasks: callable that returns an airflow task or task group to
                        to run any necessary post-ingestion tasks, such as dropping data
                        loaded during pre-ingestion
    """

    provider_script: str
    # TODO: update the ingestion_callable to only accept ProviderDataIngester classes
    # when all provider scripts have been refactored.
    ingestion_callable: Type[ProviderDataIngester] | callable = None
    dag_id: str = ""
    default_args: Optional[Dict] = None
    start_date: datetime = datetime(1970, 1, 1)
    max_active_runs: int = 1
    max_active_tasks: int = 1
    schedule_string: str = "@monthly"
    dated: bool = False
    pull_timeout: timedelta = timedelta(hours=24)
    load_timeout: timedelta = timedelta(hours=1)
    doc_md: str = ""
    media_types: Sequence[str] = ("image",)
    create_preingestion_tasks: Optional[callable] = None
    create_postingestion_tasks: Optional[callable] = None

    def __post_init__(self):
        if not self.dag_id:
            self.dag_id = f"{self.provider_script}_workflow"

        provider_script = importlib.import_module(
            f"providers.provider_api_scripts.{self.provider_script}"
        )

        if not self.ingestion_callable:
            self.ingestion_callable = provider_script.main

        if not self.doc_md:
            self.doc_md = provider_script.__doc__


PROVIDER_WORKFLOWS = [
    ProviderWorkflow(
        provider_script="brooklyn_museum",
        start_date=datetime(2020, 1, 1),
        ingestion_callable=BrooklynMuseumDataIngester,
    ),
    ProviderWorkflow(
        provider_script="cleveland_museum",
        ingestion_callable=ClevelandDataIngester,
        start_date=datetime(2020, 1, 15),
        pull_timeout=timedelta(hours=12),
    ),
    ProviderWorkflow(
        provider_script="europeana",
        start_date=datetime(2011, 9, 1),
        schedule_string="@daily",
        dated=True,
    ),
    ProviderWorkflow(
        provider_script="finnish_museums",
        ingestion_callable=FinnishMuseumsDataIngester,
        start_date=datetime(2020, 9, 1),
        pull_timeout=timedelta(days=5),
        load_timeout=timedelta(days=5),
    ),
    ProviderWorkflow(
        provider_script="flickr",
        start_date=datetime(2004, 2, 1),
        schedule_string="@daily",
        dated=True,
    ),
    ProviderWorkflow(
        provider_script="inaturalist",
        ingestion_callable=INaturalistDataIngester,
        create_preingestion_tasks=INaturalistDataIngester.create_preingestion_tasks,
        create_postingestion_tasks=INaturalistDataIngester.create_postingestion_tasks,
        schedule_string="@monthly",
        pull_timeout=timedelta(days=5),
        load_timeout=timedelta(days=5),
    ),
    ProviderWorkflow(
        provider_script="freesound",
        media_types=("audio",),
    ),
    ProviderWorkflow(
        provider_script="jamendo",
        media_types=("audio",),
    ),
    ProviderWorkflow(
        provider_script="metropolitan_museum",
        ingestion_callable=MetMuseumDataIngester,
        start_date=datetime(2016, 9, 1),
        schedule_string="@daily",
        dated=True,
        pull_timeout=timedelta(hours=12),
    ),
    ProviderWorkflow(
        provider_script="museum_victoria",
        ingestion_callable=VictoriaDataIngester,
        start_date=datetime(2020, 1, 1),
    ),
    ProviderWorkflow(
        provider_script="nypl",
        start_date=datetime(2020, 1, 1),
    ),
    ProviderWorkflow(
        provider_script="phylopic",
        start_date=datetime(2011, 1, 1),
        schedule_string="@weekly",
        dated=True,
        pull_timeout=timedelta(hours=12),
    ),
    ProviderWorkflow(
        provider_script="rawpixel",
        pull_timeout=timedelta(hours=12),
    ),
    ProviderWorkflow(
        provider_script="science_museum",
        ingestion_callable=ScienceMuseumDataIngester,
        start_date=datetime(2020, 1, 1),
    ),
    ProviderWorkflow(
        provider_script="smithsonian",
        start_date=datetime(2020, 1, 1),
        schedule_string="@weekly",
        load_timeout=timedelta(hours=4),
    ),
    ProviderWorkflow(
        provider_script="smk",
        start_date=datetime(2020, 1, 1),
    ),
    ProviderWorkflow(
        provider_script="stocksnap",
        ingestion_callable=StockSnapDataIngester,
    ),
    ProviderWorkflow(
        provider_script="walters",
        start_date=datetime(2020, 9, 27),
    ),
    ProviderWorkflow(
        provider_script="wikimedia_commons",
        ingestion_callable=WikimediaCommonsDataIngester,
        start_date=datetime(2020, 11, 1),
        schedule_string="@daily",
        dated=True,
        pull_timeout=timedelta(hours=12),
        media_types=("image", "audio"),
    ),
    ProviderWorkflow(
        provider_script="wordpress",
        pull_timeout=timedelta(hours=12),
    ),
]
