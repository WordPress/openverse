from sqlalchemy import Integer, distinct, func
from sqlalchemy.sql.expression import cast

from analytics.models import (
    AttributionRefererReport,
    AttributionReferrerEvent,
    DetailPageEvent,
    DetailPageEvents,
    Image,
    ResultClickedEvent,
    SearchEvent,
    SearchRatingEvent,
    SourceUsageReport,
    TopResultsReport,
    TopSearchesReport,
    UsageReport,
)


def generate_usage_report(session, start_time, end_time):
    """Get usage stats between start and end dates"""
    results_clicked = (
        session.query(ResultClickedEvent)
        .filter(
            start_time < ResultClickedEvent.timestamp,
            ResultClickedEvent.timestamp < end_time,
        )
        .count()
    )
    attribution_buttonclicks = (
        session.query(DetailPageEvent)
        .filter(
            start_time < DetailPageEvent.timestamp,
            DetailPageEvent.timestamp < end_time,
            DetailPageEvent.event_type == DetailPageEvents.ATTRIBUTION_CLICKED,
        )
        .count()
    )
    survey_responses = (
        session.query(DetailPageEvent)
        .filter(
            DetailPageEvent.timestamp > start_time,
            DetailPageEvent.timestamp < end_time,
            DetailPageEvent.event_type == DetailPageEvents.REUSE_SURVEY,
        )
        .count()
    )
    source_clicked = (
        session.query(DetailPageEvent)
        .filter(
            DetailPageEvent.timestamp > start_time,
            DetailPageEvent.timestamp < end_time,
            DetailPageEvent.event_type == DetailPageEvents.SOURCE_CLICKED,
        )
        .count()
    )
    creator_clicked = (
        session.query(DetailPageEvent)
        .filter(
            DetailPageEvent.timestamp > start_time,
            DetailPageEvent.timestamp < end_time,
            DetailPageEvent.event_type == DetailPageEvents.CREATOR_CLICKED,
        )
        .count()
    )
    shared_social = (
        session.query(DetailPageEvent)
        .filter(
            DetailPageEvent.timestamp > start_time,
            DetailPageEvent.timestamp < end_time,
            DetailPageEvent.event_type == DetailPageEvents.SHARED_SOCIAL,
        )
        .count()
    )
    sessions = session.query(
        func.count(distinct(SearchEvent.session_uuid)).filter(
            SearchEvent.timestamp > start_time, SearchEvent.timestamp < end_time
        )
    ).scalar()
    searches = (
        session.query(SearchEvent)
        .filter(SearchEvent.timestamp > start_time, SearchEvent.timestamp < end_time)
        .count()
    )
    attribution_referer_hits = (
        session.query(AttributionReferrerEvent)
        .filter(
            AttributionReferrerEvent.timestamp > start_time,
            AttributionReferrerEvent.timestamp < end_time,
        )
        .count()
    )
    avg_rating = session.query(
        func.avg(cast(SearchRatingEvent.relevant, Integer())).filter(
            SearchRatingEvent.timestamp > start_time,
            SearchRatingEvent.timestamp < end_time,
        )
    )
    try:
        avg_searches_per_session = searches / sessions
    except ZeroDivisionError:
        avg_searches_per_session = 0
    report = UsageReport(
        results_clicked=results_clicked,
        attribution_buttonclicks=attribution_buttonclicks,
        survey_responses=survey_responses,
        source_clicked=source_clicked,
        creator_clicked=creator_clicked,
        shared_social=shared_social,
        sessions=sessions,
        searches=searches,
        attribution_referer_hits=attribution_referer_hits,
        avg_rating=avg_rating,
        avg_searches_per_session=avg_searches_per_session,
        start_time=start_time,
        end_time=end_time,
    )
    session.add(report)
    session.commit()
    return report


def generate_source_usage_report(session, start_time, end_time):
    source_usage = (
        session.query(Image.source, func.count(ResultClickedEvent.result_uuid))
        .select_from(Image)
        .join(ResultClickedEvent, ResultClickedEvent.result_uuid == Image.identifier)
        .filter(
            ResultClickedEvent.timestamp > start_time,
            ResultClickedEvent.timestamp < end_time,
        )
        .group_by(Image.source)
        .all()
    )
    reports = []
    for res in source_usage:
        source_id, num_clicks = res
        report = SourceUsageReport(
            source_id=source_id,
            result_clicks=num_clicks,
            start_time=start_time,
            end_time=end_time,
        )
        reports.append(report)
        session.add(report)
    session.commit()
    return reports


def generate_referrer_usage_report(session, start_time, end_time):
    attribution_embeddings = (
        session.query(
            AttributionReferrerEvent.referer_domain,
            func.count(AttributionReferrerEvent.referer_domain),
        )
        .filter(
            AttributionReferrerEvent.timestamp > start_time,
            AttributionReferrerEvent.timestamp < end_time,
        )
        .group_by(AttributionReferrerEvent.referer_domain)
        .all()
    )
    reports = []
    for res in attribution_embeddings:
        domain, count = res
        report = AttributionRefererReport(
            domain=domain, hits=count, start_time=start_time, end_time=end_time
        )
        reports.append(report)
        session.add(report)
    session.commit()
    return reports


def generate_top_searches(session, start_time, end_time):
    top_searches = (
        session.query(SearchEvent.query, func.count(SearchEvent.query))
        .filter(SearchEvent.timestamp > start_time, SearchEvent.timestamp < end_time)
        .group_by(SearchEvent.query)
        .limit(100)
        .all()
    )
    reports = []
    for res in top_searches:
        query, count = res
        report = TopSearchesReport(
            term=query, hits=count, start_time=start_time, end_time=end_time
        )
        reports.append(report)
        session.add(report)
    session.commit()
    return reports


def generate_top_result_clicks(session, start_time, end_time):
    top_results = (
        session.query(
            ResultClickedEvent.result_uuid,
            Image.title,
            Image.source,
            func.count(ResultClickedEvent.result_uuid).label("num_hits"),
        )
        .filter(
            ResultClickedEvent.timestamp > start_time,
            ResultClickedEvent.timestamp < end_time,
            ResultClickedEvent.result_uuid == Image.identifier,
        )
        .group_by(ResultClickedEvent.result_uuid, Image.title, Image.source)
        .limit(500)
        .all()
    )
    reports = []
    for res in top_results:
        _uuid, title, source, count = res
        report = TopResultsReport(
            result_uuid=_uuid,
            hits=count,
            source=source,
            title=title,
            start_time=start_time,
            end_time=end_time,
        )
        reports.append(report)
        session.add(report)
    session.commit()
    return reports
