import falcon
from controller import EventController

event_controller = EventController()

class SearchEventResource:
    def on_post(self, req, resp):
        j = req.media
        event_controller.create_search(
            query=j['query'],
            session_uuid=j['session_uuid']
        )
        resp.status = falcon.HTTP_201


class SearchRatingEventResource:
    def on_post(self, req, resp):
        j = req.media
        event_controller.create_search_rating(
            query=j['query'],
            rating=j['rating']
        )
        resp.status = falcon.HTTP_201


class ResultClickEventResource:
    def on_post(self, req, resp):
        j = req.media
        event_controller.create_result_click(
            session_uuid=j['session_uuid'],
            result_uuid=j['result_uuid'],
            query=j['query'],
            rank=j['result_rank']
        )
        resp.status = falcon.HTTP_201


class DetailEventResource:
    def on_post(self, req, resp):
        j = req.media
        try:
            event_controller.create_detail_event(
                event=j['event_type'],
                result_uuid=j['result_uuid']
            )
            resp.status = falcon.HTTP_201
        except KeyError:
            valid_events = event_controller.list_valid_detail_events()
            resp.body = \
                '{{"message": "Invalid event_type. Valid types: {}"}}' \
                .format(valid_events)
            resp.status = falcon.HTTP_400


api = falcon.API()
api.add_route('/search_event', SearchEventResource())
api.add_route('/search_rating_event', SearchRatingEventResource())
api.add_route('/result_click_event', ResultClickEventResource())
api.add_route('/detail_page_event', DetailEventResource())
