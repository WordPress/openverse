from models import SearchEvent, SearchRatingEvent, ResultClickedEvent, \
    DetailPageEvent, DetailPageEvents
from sqlalachemy import create_engine
from sqlalachemy.orm import sessionmaker
from settings import DATABASE_CONNECTION

class EventController:
    def __init__(self):
        self.engine = create_engine(DATABASE_CONNECTION)

    def _persist(_object):
        session = sessionmaker(bind=self.engine)
        session.add(_object)
        session.commit()

    def create_search(self, session_uuid, query):
        search = SearchEvent(
            session_uuid=session_uuid,
            query=query
        )
        self._persist(search)

    def create_search_rating(self, query, rating):
        search_rating = SearchRatingEvent(
            query=query,
            rating=rating
        )
        self._persist(search_rating)

    def create_result_click(self, session_uuid, result_uuid, query, rank):
        result_click = ResultClickedEvent(
            session_uuid=session_uuid,
            result_uuid=result_uuid,
            query=query,
            result_rank=rank
        )
        self._persist(result_click)

    def create_detail_event(self, event, result_uuid):
        detail_event = DetailPageEvent(
            event_type=event,
            result_uuid=result_uuid
        )
        self._persist(detail_event)
