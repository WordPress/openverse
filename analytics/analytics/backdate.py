"""
A one-off script for generating analytics reports back to September 2019, when
we first started collecting analytics data.
"""

import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from analytics import settings
from analytics.report_controller import (
    generate_referrer_usage_report,
    generate_source_usage_report,
    generate_top_result_clicks,
    generate_top_searches,
    generate_usage_report,
)


engine = create_engine(settings.DATABASE_CONNECTION)
session_maker = sessionmaker(bind=engine)
session = session_maker()
backdate_limit = datetime.datetime(year=2019, month=9, day=10)
current_end_date = datetime.datetime.utcnow()
while current_end_date > backdate_limit:
    start_date = current_end_date - datetime.timedelta(days=1)

    generate_usage_report(session, start_date, current_end_date)
    generate_source_usage_report(session, start_date, current_end_date)
    generate_referrer_usage_report(session, start_date, current_end_date)
    generate_top_searches(session, start_date, current_end_date)
    generate_top_result_clicks(session, start_date, current_end_date)

    current_end_date -= datetime.timedelta(days=1)
    print(f"Generated backdated reports for {current_end_date}")
