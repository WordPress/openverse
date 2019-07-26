import enum
from sqlalchemy import Integer, Column, Enum, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SearchEvent(Base):
    """
    Store searches linked to a session UUID.
    """
    __tablename__ = "search_event"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, server_default=func.now(), index=True)
    query = Column(String, index=True)
    session_uuid = Column(UUID, index=True)


class SearchRatingEvent(Base):
    """
    Users can provide feedback about the quality of search results.
    """
    __tablename__= "search_rating_event"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, server_default=func.now(), index=True)
    query = Column(String, index=True)
    rating = Column(Integer)


class ResultClickedEvent(Base):
    """
    Link result clicks to search sessions.
    """
    __tablename__ = "result_clicked_event"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, server_default=func.now(), index=True)
    session_uuid = Column(UUID, index=True)
    result_uuid = Column(UUID, index=True)
    query = Column(String, index=True)
    result_rank = Column(Integer)


class DetailPageEvents(enum.Enum):
    ATTRIBUTION_CLICKED = enum.auto()
    REUSE_SURVEY = enum.auto()
    SOURCE_CLICKED = enum.auto()
    CREATOR_CLICKED = enum.auto()
    SHARED_SOCIAL = enum.auto()


class DetailPageEvent(Base):
    """
    Events that happen on result pages, such as clicking an attribution button
    or sharing the result on social media.

    """
    __tablename__ = "detail_page_event"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, server_default=func.now(), index=True)
    result_uuid = Column(UUID, index=True)
    event_type = Column(Enum(DetailPageEvents), index=True)
