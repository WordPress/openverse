import pytest
import datetime
import uuid
import analytics.settings as settings
import requests
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from analytics.attribution_worker import parse_message, is_valid
from analytics.reporting import generate_usage_report,\
    generate_source_usage_report, generate_referrer_usage_report
from analytics.models import AttributionReferrerEvent
"""
End-to-end tests of the analytics server. Run with `pytest -s`.
"""


API_URL = os.getenv('ANALYTICS_SERVER_URL', 'http://localhost:8090')
session_id = '00000000-0000-0000-0000-000000000000'
result_id = '380e1781-bb07-4d6f-aa65-e199ad6d68cb'
test_query = 'integration test'
engine = create_engine(settings.DATABASE_CONNECTION)
session_maker = sessionmaker(bind=engine)
session = session_maker()


def test_search_event():
    body = {
        'query': test_query,
        'session_uuid': session_id
    }
    response = requests.post(API_URL + '/search_event', json=body, verify=False)
    assert response.status_code == 201


def test_search_rating():
    body = {
        'query': test_query,
        'relevant': True
    }
    response = requests.post(
        API_URL + '/search_rating_event', json=body, verify=False
    )
    assert response.status_code == 201

    invalid_rating = {
        'query': test_query,
        'relevant': 6
    }
    bad_response = requests.post(
        API_URL + '/search_rating_event', json=invalid_rating, verify=False
    )
    assert bad_response.status_code == 400


def test_result_clicked():
    body = {
        'query': test_query,
        'session_uuid': session_id,
        'result_uuid': result_id,
        'result_rank': 0
    }
    response = requests.post(
        API_URL + '/result_click_event', json=body, verify=False
    )
    assert response.status_code == 201


def test_detail_event():
    body = {
        'event_type': 'SHARED_SOCIAL',
        'result_uuid': result_id
    }
    response = requests.post(
        API_URL + '/detail_page_event', json=body, verify=False
    )
    assert response.status_code == 201

    invalid_event = {
        'event_type': 'FOO',
        'result_uuid': result_id
    }
    bad_response = requests.post(
        API_URL + '/detail_page_event', json=invalid_event, verify=False
    )
    assert bad_response.status_code == 400


# Attribution logging tests
def mock_attribution_event(_json: dict):
    return json.dumps({
        'message': json.dumps(_json)
    })


def test_attribution_validation():
    valid_msg = mock_attribution_event({
        'http_referer': 'https://alden.page/blog',
        'request': 'GET /static/img/cc-nd_icon.svg HTTP/1.1'
    })
    invalid_msg = mock_attribution_event({
        'http_referer': 'https://search.creativecommons.org/photos/12345',
        'request': 'GET /static/img/cc-nd_icon.svg HTTP/1.1'
    })
    assert is_valid(parse_message(valid_msg))
    assert not is_valid(parse_message(invalid_msg))


def test_msg_parsing_noparam():
    test_msg = mock_attribution_event({
        'http_referer': 'https://alden.page/blog',
        'request': 'GET /static/img/cc-nd_icon.svg HTTP/1.1',
    })
    parsed = parse_message(test_msg)
    assert parsed['http_referer'] == 'https://alden.page/blog'
    assert parsed['resource'] == '/static/img/cc-nd_icon.svg'
    assert parsed['identifier'] is None


def test_msg_parsing_valid_param():
    test_msg = mock_attribution_event({
        'http_referer': 'https://alden.page/blog',
        'request': 'GET /static/img/cc-nd_icon.svg?image_id=b45c0995-9896-4ba8-838d-096ec4e9cdf4 HTTP/1.1',
    })
    parsed = parse_message(test_msg)
    assert parsed['identifier'] == 'b45c0995-9896-4ba8-838d-096ec4e9cdf4'


def test_msg_parsing_invalid_params():
    test_msg = mock_attribution_event({
        'http_referer': 'https://alden.page/blog',
        'request': 'GET /static/img/cc-nd_icon.svg?image_id=lol&notreal=param?hi HTTP/1.1',
    })
    parsed = parse_message(test_msg)
    assert parsed['identifier'] is None


def test_usage_report():
    start_time = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
    end_time = datetime.datetime.utcnow()
    report = generate_usage_report(session, start_time, end_time)


def test_source_usage():
    start_time = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
    end_time = datetime.datetime.utcnow()
    source_usage = generate_source_usage_report(session, start_time, end_time)
    assert source_usage['behance'] >= 1


def test_attribution_embedding():
    start_time = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
    end_time = datetime.datetime.utcnow()
    event = AttributionReferrerEvent(
        image_uuid=result_id,
        full_referer='https://alden.page/blog',
        referer_domain='alden.page',
        resource='/static/img/cc-by.svg'
    )
    session.add(event)
    session.commit()
    attribution_usage = generate_referrer_usage_report(
        session, start_time, end_time
    )
    assert attribution_usage['alden.page'] >= 1
