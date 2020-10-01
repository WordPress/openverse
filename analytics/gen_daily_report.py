import datetime
import settings
import logging as log
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from analytics.report_controller import (
    generate_usage_report, generate_source_usage_report,
    generate_referrer_usage_report, generate_top_searches,
    generate_top_result_clicks
)

engine = create_engine(settings.DATABASE_CONNECTION)
session_maker = sessionmaker(bind=engine)
session = session_maker()
end_date = datetime.datetime.utcnow()
start_date = end_date - datetime.timedelta(days=1)

generate_usage_report(session, start_date, end_date)
generate_source_usage_report(session, start_date, end_date)
generate_referrer_usage_report(session, start_date, end_date)
generate_top_searches(session, start_date, end_date)
generate_top_result_clicks(session, start_date, end_date)

log.info(f'Generated analytics reports for {end_date}')