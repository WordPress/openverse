from django.conf import settings

import schemathesis


schema = schemathesis.from_uri(f"{settings.CANONICAL_ORIGIN}/v1/schema/")


@schema.parametrize()
def test_schema(case):
    case.call_and_validate()
