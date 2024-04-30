import re

from django.conf import settings

import schemathesis


schema = schemathesis.from_uri(f"{settings.CANONICAL_ORIGIN}/v1/schema/")


# The null-bytes Bearer tokens are skipped.
# The pattern identifies tests with headers that are acceptable,
# by only allowing authorization headers that use characters valid for
# token strings.
# In test, the token produces an inscruitable error,
# but condition is irreproducible in actual local or live
# environments. Once Schemathesis implements options
# to configure which headers are used
# (https://github.com/schemathesis/schemathesis/issues/2137)
# we will revisit these cases.
TOKEN_TEST_ACCEPTABLE = re.compile(r"^Bearer \w+$")


@schema.parametrize()
def test_schema(case: schemathesis.Case):
    if case.headers and not TOKEN_TEST_ACCEPTABLE.findall(
        case.headers.get("Authorization")
    ):
        # Do not use `pytest.skip` here, unfortunately it causes a deprecation warning
        # from schemathesis's implementation of `parameterize`.
        return

    case.call_and_validate()
