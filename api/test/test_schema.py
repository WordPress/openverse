import schemathesis

from test.constants import API_URL


schema = schemathesis.from_uri(f"{API_URL}/v1/schema/")


@schema.parametrize()
def test_schema(case):
    case.call_and_validate()
