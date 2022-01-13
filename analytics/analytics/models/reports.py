from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ReportMixin(object):
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime, index=True)


class UsageReport(Base, ReportMixin):
    """Tracks statistics for the last 24 hours"""

    __tablename__ = "usage_reports"
    results_clicked = Column(Integer)
    attribution_buttonclicks = Column(Integer)
    survey_responses = Column(Integer)
    source_clicked = Column(Integer)
    creator_clicked = Column(Integer)
    shared_social = Column(Integer)
    sessions = Column(Integer)
    searches = Column(Integer)
    attribution_referer_hits = Column(Integer)
    avg_rating = Column(Float)
    avg_searches_per_session = Column(Float)


class SourceUsageReport(Base, ReportMixin):
    __tablename__ = "source_report"

    source_id = Column(String, index=True)
    result_clicks = Column(Integer, index=True)


class AttributionRefererReport(Base, ReportMixin):
    __tablename__ = "attribution_referer_report"

    domain = Column(String, index=True)
    hits = Column(Integer, index=True)


class TopSearchesReport(Base, ReportMixin):
    __tablename__ = "top_searches"
    term = Column(String, index=True)
    hits = Column(Integer, index=True)


class TopResultsReport(Base, ReportMixin):
    __tablename__ = "top_results"
    result_uuid = Column(UUID, index=True)
    hits = Column(Integer, index=True)
    source = Column(String, index=True)
    title = Column(String, index=True)
