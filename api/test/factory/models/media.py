from uuid import uuid4

from django.conf import settings

import factory
import pook
from elasticsearch import Elasticsearch
from elasticsearch_dsl.response import Hit
from factory.django import DjangoModelFactory

from api.constants.licenses import ALL_LICENSES
from api.models.media import AbstractMedia
from test.factory.faker import Faker


CREATED_BY_FIXTURE_MARKER = "__created_by_test_fixture"


_highest_pre_existing_pk = {}


class MediaFactory(DjangoModelFactory):
    """Base factory for models that extend from the AbstractMedia class."""

    # Sub-factories can extend this with media-specific fields
    _document_fields = (
        "id",
        "identifier",
        "foreign_identifier",
        "license",
        "foreign_landing_url",
        "url",
        "thumbnail",
        "title",
        "tags",
        "provider",
    )

    # Sub-factories must set this to their corresponding
    # ``AbstractSensitiveMedia`` subclass
    _sensitive_factory = None

    _highest_pre_existing_pk = None

    class Meta:
        abstract = True

    id = factory.sequence(lambda n: n)

    identifier = factory.sequence(lambda _: str(uuid4()))

    foreign_identifier = factory.sequence(lambda _: uuid4())
    """The foreign identifier isn't necessarily a UUID but for test purposes it's fine if it looks like one"""

    license = Faker("random_element", elements=ALL_LICENSES)
    provider = Faker("random_element", elements=("wikimedia", "flickr"))

    foreign_landing_url = Faker("globally_unique_url")
    url = Faker("globally_unique_url")
    thumbnail = Faker("image_url")
    title = Faker("sentence", nb_words=4)
    tags = factory.List(
        [
            {
                "name": CREATED_BY_FIXTURE_MARKER,
            }
        ]
    )

    @classmethod
    def create(cls, *args, **kwargs) -> AbstractMedia | tuple[AbstractMedia, Hit]:
        r"""
        Create the media instance.

        :param \**kwargs:
            In addition to the media properties handled by the factory,
            see the factory-behaviour specific kwargs below.

        :Keyword Arguments:
            * *mature_reported* (``bool``) --
                Create a mature report for this media.
            * *provider_marked_mature* (``bool``) --
                Set ``mature=true`` on the Elasticsearch document.
            * *sensitive_text* (``bool``) --
                Whether the media should be treated as having sensitive text.
                If not, it will be added to the filtered index.
            * *skip_es* (``bool``) --
                Skip Elasticsearch document creation.
            * *with_hit* (``bool``) --
                Whether to return the Elasticsearch ``Hit`` along with the
                created media object.
        """
        mature_reported = kwargs.pop("mature_reported", False)
        provider_marked_mature = kwargs.pop("provider_marked_mature", False)
        sensitive_text = kwargs.pop("sensitive_text", False)
        skip_es = kwargs.pop("skip_es", False)
        with_hit = kwargs.pop("with_hit", False)

        pook_active = pook.isactive()
        if pook_active:
            # Temporarily disable pook so that the calls to ES to create
            # the factory document don't fail
            pook.disable()

        model_class = cls._meta.get_model_class()
        if cls._highest_pre_existing_pk is None:
            response = settings.ES.search(
                index=model_class._meta.db_table, sort={"id": "desc"}, size=1
            )

            cls._highest_pre_existing_pk = int(response["hits"]["hits"][0]["_id"])

        kwargs.setdefault(
            "id", cls._meta.next_sequence() + cls._highest_pre_existing_pk + 1
        )

        model = super().create(*args, **kwargs)

        if not skip_es:
            hit = cls._save_model_to_es(
                model,
                add_to_filtered_index=not sensitive_text,
                mature=provider_marked_mature or mature_reported,
            )
        else:
            hit = None

        if mature_reported:
            cls._sensitive_factory.create(media_obj=model)

        if pook_active:
            # Reactivate pook if it was active
            pook.activate()

        if with_hit:
            return model, hit

        return model

    @classmethod
    def _create_es_source_document(
        cls,
        media: AbstractMedia,
        mature: bool,
    ) -> dict:
        return {"mature": mature} | {
            field: getattr(media, field) for field in cls._document_fields
        }

    @classmethod
    def _save_model_to_es(
        cls,
        media: AbstractMedia,
        *,
        add_to_filtered_index: bool = True,
        mature: bool = False,
    ) -> Hit:
        """
        Persist a media model to Elasticsearch.

        ``test.unit.conftest::cleanup_test_documents_elasticsearch`` is
        responsible for cleaning up documents created in tests.
        """
        es: Elasticsearch = settings.ES

        origin_index = media._meta.db_table
        source_document = cls._create_es_source_document(media, mature)

        es.create(
            index=origin_index,
            id=str(media.pk),
            document=source_document,
            refresh=True,
        )
        if add_to_filtered_index:
            es.create(
                index=f"{origin_index}-filtered",
                id=media.pk,
                document=source_document,
                refresh=True,
            )

        return Hit(
            {
                "_index": origin_index,
                "_score": 1.0,
                "_id": str(media.pk),
                "_source": source_document,
            }
        )


class IdentifierFactory(factory.SubFactory):
    """
    A factory for creating a related model and returning the UUID.

    Distinct from the `SubFactory` in that this creates the related model but
    uses a specific attribute from it for the resulting value instead of the
    related model itself.
    """

    def evaluate(self, instance, step, extra):
        model = super().evaluate(instance, step, extra)
        return model.identifier


class MediaReportFactory(DjangoModelFactory):
    class Meta:
        abstract = True
