import inspect
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from providers.provider_api_scripts.brooklyn_museum import BrooklynMuseumDataIngester
from providers.provider_api_scripts.cleveland_museum import ClevelandDataIngester
from providers.provider_api_scripts.europeana import EuropeanaDataIngester
from providers.provider_api_scripts.finnish_museums import FinnishMuseumsDataIngester
from providers.provider_api_scripts.flickr import FlickrDataIngester
from providers.provider_api_scripts.freesound import FreesoundDataIngester
from providers.provider_api_scripts.inaturalist import INaturalistDataIngester
from providers.provider_api_scripts.jamendo import JamendoDataIngester
from providers.provider_api_scripts.metropolitan_museum import MetMuseumDataIngester
from providers.provider_api_scripts.museum_victoria import VictoriaDataIngester
from providers.provider_api_scripts.nypl import NyplDataIngester
from providers.provider_api_scripts.phylopic import PhylopicDataIngester
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester
from providers.provider_api_scripts.rawpixel import RawpixelDataIngester
from providers.provider_api_scripts.science_museum import ScienceMuseumDataIngester
from providers.provider_api_scripts.smithsonian import SmithsonianDataIngester
from providers.provider_api_scripts.smk import SmkDataIngester
from providers.provider_api_scripts.stocksnap import StockSnapDataIngester
from providers.provider_api_scripts.wikimedia_commons import (
    WikimediaCommonsDataIngester,
)
from providers.provider_api_scripts.wordpress import WordPressDataIngester


@dataclass
class ProviderWorkflow:
    """
    Required Arguments:

    ingester_class: ProviderDataIngester class whose `ingest_records` method is
                        to be run.

    Optional Arguments:

    dag_id:             string giving a unique id of the DAG to be created. By
                        default this will be set to the name of the provider_script,
                        appended with 'workflow'.
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
                        (e.g. `["audio"]`, `["image", "audio"]`, etc.) By default this
                        will be set to the list of media_types supported in the
                        ProviderDataIngester.
    create_preingestion_tasks: callable that returns an airflow task or task group to
                        to run any necessary pre-ingestion tasks, such as loading bulk
                        data from S3
    create_postingestion_tasks: callable that returns an airflow task or task group to
                        to run any necessary post-ingestion tasks, such as dropping data
                        loaded during pre-ingestion
    tags:               list of any additional tags to apply to the generated DAG
    """

    ingester_class: type[ProviderDataIngester]
    dag_id: str = ""
    default_args: dict | None = None
    start_date: datetime = datetime(1970, 1, 1)
    max_active_runs: int = 1
    max_active_tasks: int = 1
    schedule_string: str = "@monthly"
    dated: bool = False
    pull_timeout: timedelta = timedelta(hours=24)
    load_timeout: timedelta = timedelta(hours=1)
    doc_md: str = ""
    media_types: Sequence[str] = ()
    create_preingestion_tasks: Callable | None = None
    create_postingestion_tasks: Callable | None = None
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        # Get the module the ProviderDataIngester was defined in
        provider_script = inspect.getmodule(self.ingester_class)
        self.provider_name = provider_script.__name__.split(".")[-1]

        if not self.dag_id:
            self.dag_id = f"{self.provider_name}_workflow"

        if not self.media_types:
            self.media_types = list(self.ingester_class.providers.keys())

        if not self.doc_md:
            self.doc_md = provider_script.__doc__


PROVIDER_WORKFLOWS = [
    ProviderWorkflow(
        start_date=datetime(2020, 1, 1),
        ingester_class=BrooklynMuseumDataIngester,
    ),
    ProviderWorkflow(
        ingester_class=ClevelandDataIngester,
        start_date=datetime(2020, 1, 15),
        pull_timeout=timedelta(hours=12),
    ),
    ProviderWorkflow(
        ingester_class=EuropeanaDataIngester,
        start_date=datetime(2022, 10, 27),
        schedule_string="@daily",
        dated=True,
    ),
    ProviderWorkflow(
        ingester_class=FinnishMuseumsDataIngester,
        start_date=datetime(2020, 9, 1),
        pull_timeout=timedelta(days=5),
        load_timeout=timedelta(days=5),
    ),
    ProviderWorkflow(
        ingester_class=FlickrDataIngester,
        start_date=datetime(2020, 11, 1),
        schedule_string="@daily",
        dated=True,
    ),
    ProviderWorkflow(
        ingester_class=FreesoundDataIngester,
    ),
    ProviderWorkflow(
        ingester_class=INaturalistDataIngester,
        create_preingestion_tasks=INaturalistDataIngester.create_preingestion_tasks,
        create_postingestion_tasks=INaturalistDataIngester.create_postingestion_tasks,
        schedule_string="@monthly",
        pull_timeout=timedelta(days=5),
        load_timeout=timedelta(days=5),
    ),
    ProviderWorkflow(
        ingester_class=JamendoDataIngester,
    ),
    ProviderWorkflow(
        ingester_class=MetMuseumDataIngester,
        start_date=datetime(2016, 9, 1),
        schedule_string="@daily",
        dated=True,
        pull_timeout=timedelta(hours=12),
    ),
    ProviderWorkflow(
        ingester_class=VictoriaDataIngester,
        start_date=datetime(2020, 1, 1),
    ),
    ProviderWorkflow(
        ingester_class=NyplDataIngester,
        start_date=datetime(2020, 1, 1),
    ),
    ProviderWorkflow(
        ingester_class=PhylopicDataIngester,
        start_date=datetime(2011, 2, 7),
        schedule_string="@daily",
        dated=True,
        pull_timeout=timedelta(hours=12),
    ),
    ProviderWorkflow(
        ingester_class=RawpixelDataIngester,
        pull_timeout=timedelta(hours=12),
    ),
    ProviderWorkflow(
        ingester_class=ScienceMuseumDataIngester,
        start_date=datetime(2020, 1, 1),
    ),
    ProviderWorkflow(
        ingester_class=SmithsonianDataIngester,
        start_date=datetime(2020, 1, 1),
        schedule_string="@weekly",
        load_timeout=timedelta(hours=4),
    ),
    ProviderWorkflow(
        ingester_class=SmkDataIngester,
        start_date=datetime(2020, 1, 1),
    ),
    ProviderWorkflow(
        ingester_class=StockSnapDataIngester,
    ),
    ProviderWorkflow(
        ingester_class=WikimediaCommonsDataIngester,
        start_date=datetime(2020, 11, 1),
        schedule_string="@daily",
        dated=True,
        pull_timeout=timedelta(hours=12),
    ),
    ProviderWorkflow(
        ingester_class=WordPressDataIngester,
        pull_timeout=timedelta(hours=12),
    ),
]
