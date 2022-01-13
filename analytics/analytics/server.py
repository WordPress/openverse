import logging
import sys
from uuid import UUID

import falcon
from falcon_cors import CORS
from spectree import Response, SpecTree

from analytics import settings
from analytics.docs.schemas.requests import (
    DetailEventSchema,
    ResultClickEventSchema,
    SearchEventSchema,
    SearchRatingEventSchema,
)
from analytics.docs.schemas.responses import (
    BadRequestSchema,
    CreatedSchema,
    InternalServerErrorSchema,
    OkSchema,
)
from analytics.event_controller import EventController


with open("docs/redoc.html", "r") as redoc_html:
    page_templates = {"redoc": redoc_html.read()}
with open("docs/README.md", "r") as readme_file:
    description = readme_file.read()
spec = SpecTree(
    "falcon",
    title="Openverse Analytics",
    version=settings.VERSION,
    description=description,
    page_templates=page_templates,
    path="doc",
    mode="strict",
    validation_error_status=400,
)

resp = Response(
    HTTP_201=CreatedSchema,
    HTTP_400=BadRequestSchema,
    HTTP_500=InternalServerErrorSchema,
)


class HealthResource:
    @spec.validate(
        resp=Response(HTTP_200=OkSchema),
        validation_error_status=200,  # never fails validation
        tags=["health"],
    )
    def on_get(self, _, resp):
        """detail"""
        resp.media = {"status": "200 OK"}
        resp.status = falcon.HTTP_200


class BaseEventResource:
    """Base class for all resource that need access to an event controller"""

    @staticmethod
    def _validate_uuid(field, uuid):
        try:
            return UUID(uuid, version=4).hex
        except ValueError:
            raise falcon.HTTPBadRequest(description=f"{field} must be a v4 UUID")

    def __init__(self, event_controller: EventController, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_controller = event_controller


class SearchEventResource(BaseEventResource):
    @spec.validate(
        json=SearchEventSchema,
        resp=resp,
        tags=["search_event"],
    )
    def on_post(self, req, resp):
        """create

        Register a search query event.
        """

        j = req.media
        try:
            self.event_controller.create_search(
                query=j["query"],
                session_uuid=j["session_uuid"],
            )
            resp.media = {"status": "201 Created"}
            resp.status = falcon.HTTP_201
        except Exception as e:
            raise falcon.HTTPInternalServerError(description=str(e))


class SearchRatingEventResource(BaseEventResource):
    @spec.validate(
        json=SearchRatingEventSchema,
        resp=resp,
        tags=["search_rating_event"],
    )
    def on_post(self, req, resp):
        """create

        Submit a user's rating of a search.
        """

        j = req.media
        try:
            self.event_controller.create_search_rating(
                query=j["query"],
                relevant=j["relevant"],
            )
            resp.media = {"status": "201 Created"}
            resp.status = falcon.HTTP_201
        except Exception as e:
            raise falcon.HTTPInternalServerError(description=str(e))


class ResultClickEventResource(BaseEventResource):
    @spec.validate(
        json=ResultClickEventSchema,
        resp=resp,
        tags=["result_click_event"],
    )
    def on_post(self, req, resp):
        """create

        Submit an event indicating which result was clicked for a given search
        query.
        """

        j = req.media
        try:
            self.event_controller.create_result_click(
                query=j["query"],
                session_uuid=j["session_uuid"],
                result_uuid=j["result_uuid"],
                rank=j["result_rank"],
            )
            resp.media = {"status": "201 Created"}
            resp.status = falcon.HTTP_201
        except Exception as e:
            raise falcon.HTTPInternalServerError(description=str(e))


class DetailEventResource(BaseEventResource):
    @spec.validate(
        json=DetailEventSchema,
        resp=resp,
        tags=["detail_page_event"],
    )
    def on_post(self, req, resp):
        """create

        Record events occurring on detail pages, such as sharing an image to
        social media or clicking through to its source.
        """

        j = req.media
        try:
            self.event_controller.create_detail_event(
                event=j["event_type"],
                result_uuid=j["result_uuid"],
            )
            resp.media = {"status": "201 Created"}
            resp.status = falcon.HTTP_201
        except Exception as e:
            raise falcon.HTTPInternalServerError(description=str(e))


def create_api(log=True):
    """Create an instance of the Falcon API server."""

    if log:
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(filename)s:%(lineno)d - %(message)s"
        )
        handler.setFormatter(formatter)
        root.addHandler(handler)

    cors = CORS(
        allow_origins_list=settings.ORIGINS,
        allow_all_methods=True,
        allow_all_headers=True,
    )
    _api = falcon.App(middleware=[cors.middleware])

    event_controller = EventController()

    _api.add_route("/", HealthResource())
    _api.add_route("/search_event", SearchEventResource(event_controller))
    _api.add_route("/search_rating_event", SearchRatingEventResource(event_controller))
    _api.add_route("/result_click_event", ResultClickEventResource(event_controller))
    _api.add_route("/detail_page_event", DetailEventResource(event_controller))

    return _api


api = create_api()
spec.register(api)
