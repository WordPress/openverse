from test.factory.faker import Faker
from uuid import uuid4

from django.conf import settings

import factory
from elasticsearch import Elasticsearch
from elasticsearch_dsl.response import Hit
from factory.django import DjangoModelFactory

from api.constants.licenses import ALL_LICENSES
from api.models.media import AbstractMedia


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
        "mature",
        "title",
        "tags",
    )

    # Sub-factories must set this to their corresponding
    # ``AbstractMatureMedia`` subclass
    _mature_factory = None

    _highest_pre_existing_pk = None

    class Meta:
        abstract = True

    id = factory.sequence(lambda n: n)

    identifier = factory.sequence(lambda _: str(uuid4()))

    foreign_identifier = factory.sequence(lambda _: uuid4())
    """The foreign identifier isn't necessarily a UUID but for test purposes it's fine if it looks like one"""

    license = Faker("random_element", elements=ALL_LICENSES)

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
    def create(cls, *args, **kwargs):
        """
        Create the media instance.

        If ``mature_reported`` kwarg is passed, this is understood to mean
        a document identified as mature as a result of a user report.

        Provider-supplied maturity is only recorded in the ES
        index and should be tested via the ``create_es_document``
        helper method or mocking.
        """
        mature_reported = kwargs.pop("mature_reported", False)

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
        if mature_reported:
            cls._mature_factory.create(media_obj=model)

        return model

    @classmethod
    def _create_es_source_document(
        cls,
        media: AbstractMedia,
        # If ``None`` this will default to the ``media.mature``
        # property value. Otherwise it will force the document
        # value.
        mature: bool | None,
    ) -> dict:
        mature = media.mature if mature is None else mature
        return {"mature": mature} | {
            field: getattr(media, field) for field in cls._document_fields
        }

    @classmethod
    def save_model_to_es(
        cls,
        media: AbstractMedia,
        *,
        filtered: bool = True,
        mature: bool | None = None,
    ):
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
            id=media.pk,
            document=source_document,
            refresh=True,
        )
        if filtered:
            es.create(
                index=f"{origin_index}-filtered",
                id=media.pk,
                document=source_document,
                refresh=True,
            )

    @classmethod
    def create_hit(
        cls, media: AbstractMedia, *, _score: float = 1.0, mature: bool | None = None
    ) -> Hit:
        # ``document`` should match the dictionary returned
        # by Elasticsearch. ``_source`` only contains the
        # fields that are defined in the ``MediaFactory``,
        # not all the fields for a
        document = {
            "_index": media._meta.db_table,
            "_type": "doc",
            "_id": media.pk,
            "_score": _score,
            "_source": cls._create_es_source_document(
                media,
                mature,
            ),
        }

        return Hit(document)


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
