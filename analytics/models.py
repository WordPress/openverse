import enum
from sqlalchemy import Integer, Column, UUID, Enum, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class EventBase(Base):
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, server_default=func.now())

class SearchEvent(EventBase):
    """
    Store searches linked to a session UUID.
    """
    __tablename__ = "search_event"

    query = Column(String)
    session_uuid = Column(UUID)


class SearchRatingEvent(EventBase):
    """
    Users can provide feedback about the quality of search results.
    """
    __tablename__= "search_rating_event"

    query = Column(String)
    rating = Column(Integer)


class ResultClickedEvent(EventBase):
    """
    Link result clicks to search sessions.
    """
    __tablename__ = "result_clicked_event"

    session_uuid = Column(UUID)
    result_uuid = Column(UUID)
    query = Column(String)


class DetailPageEvents(enum.Enum):
    ATTRIBUTION_CLICKED = enum.auto()
    REUSE_SURVEY = enum.auto()
    SOURCE_CLICKED = enum.auto()
    CREATOR_CLICKED = enum.auto()
    SHARED_SOCIAL = enum.auto()


class DetailPageEvent(EventBase):
    """
    Events that happen on result pages, such as clicking an attribution button
    or sharing the result on social media.
    """
    __tablename__ = "detail_page_event"

    event_type = Column(Enum(DetailPageEvents))
