from models import SearchEvent, SearchRatingEvent, ResultClickedEvent, \
    DetailPageEvent, DetailPageEvents
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import DATABASE_CONNECTION

class EventController:
    def __init__(self):
        self.engine = create_engine(DATABASE_CONNECTION)

    def _persist(self, _object):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        session.add(_object)
        session.commit()

    def create_search(self, session_uuid, query):
        search = SearchEvent(
            session_uuid=session_uuid,
            query=query
        )
        self._persist(search)

    def create_search_rating(self, query, relevant):
        if type(relevant) != bool:
            raise ValueError('Invalid rating; must be a boolean.')
        search_rating = SearchRatingEvent(
            query=query,
            relevant=relevant
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
        _event = DetailPageEvents[event]
        detail_event = DetailPageEvent(
            event_type=_event,
            result_uuid=result_uuid
        )
        self._persist(detail_event)

    def list_valid_detail_events(self):
        return [k.name for k in DetailPageEvents]
