# Authentication and Throttling

This document primarily serves to document our additions to DRF's built-in
throttling support. In order to accomplish this, some basic facts about our
OAuth flow and configuration must also be explained.

This document deals primarily with the server's perspective of the OAuth flow
and assumes you are familiar with the user's perspective. If you are not
familiar with the user's perspective, please study the
[Register and Authenticate](https://api.openverse.org/v1/#section/Register-and-Authenticate)
section of the API documentation.

Furthermore, this section assumes at least a surface level understanding of the
`django-oauth-toolkit` library and its concepts. In particular, it is necessary
to understand the
[`Application` concept, the docs for which can be found here](https://django-oauth-toolkit.readthedocs.io/en/latest/advanced_topics.html#extending-the-application-model).

## Flow

When a user makes the initial request to create their OAuth application, we
create a `ThrottledApplication` model to associate to the likewise generated
OAuth client. Whenever the user generates a new token using their client ID and
key pair, it is automatically associated with the `ThrottledApplication` for the
client via a
[foreign key referencing the application on the access token](https://django-oauth-toolkit.readthedocs.io/en/latest/models.html#oauth2_provider.models.AbstractAccessToken).
This allows us to retrieve the application for the token using just the token
itself.

## `ThrottledApplication`

The `ThrottledApplication` is an extension of the base `AbstractApplication`
class from `django-oauth-toolkit` that adds an additional concept of a
`rate_limit_model`. Each rate limit model can be thought of as a "tiers" of rate
limiting that the Openverse API supports.

## Rate limit models (tiers)

The following tiers exist:

- `standard`: The default rate limit that anyone is able to unlock simply by
  authenticating. Slightly higher and much more useful limit for an application.
- `enhanced`: A selectively granted rate limit that allows for significantly
  higher burst and sustained requests.
- `exempt`: A rate limit model that exists purely to accommodate internal
  infrastructural needs. For example, the server that renders the frontend can
  use tokens of this tier to prevent itself from being rate limited by the API
  during server side rendering. Likewise, when we need to circumvent the
  throttling to do load testing, we use a key of this tier.

## Throttles

Each of these tiers also have corresponding throttle classes that are configured
in `settings.py`. Each throttle class declares a "scope" applied to it. The
"scope" defines the rate. The throttle class merely indicates to the view
whether it itself applies to the incoming request. If it does not, then it
returns a `None` cache key from `get_cache_key` and the view ignores the
throttle class. If the throttle does apply to the request, then it returns a
formatted cache key that the base DRF view then uses to determine whether the
requester is still within the limits of their scope.

To further understand this concept, it may be helpful to read the code for
[`SimpleRateThrottle`](https://github.com/encode/django-rest-framework/blob/129890ab1bbbba2deb96b8e30675dfb1060d7615/rest_framework/throttling.py#L50)
and the
[`check_throttles` method of the DRF base view class](https://github.com/encode/django-rest-framework/blob/101aff6c43f6fa96174683e050988428143d1040/rest_framework/views.py#L352-L371).

Each of the tiers above have their own scope namespace. For example, enhanced
applications will use the scopes namespaced with
`enhanced_oauth2_client_credentials`. To determine which scope a given
authenticated request should have applied to it, we need to determine which
application rate limit tier it belongs to. To simplify this abstract process, we
use the `OAuth2IdRateThrottle` base class. All it does is take an incoming
authenticated request, retrieve the application for the given access token, and
then create a cache key based on the client ID and scope if the class is
configured to handle the application's rate limit tier.

Individual tiers have complementary subclasses of `OAuth2IdRateThrottle` that
configure which scope to apply to a particular rate limit tier. Please refer to
the `catalog.api.utils.throttle` module for example implementations of this
pattern.
