# Frontend reverse proxy

The frontend service relies on an Nginx reverse proxy in live environments to
facilitate per-request logging in a format that matches other services we run
(namely, Django). It also acts as a [proxy for Plausible][plausible_proxy],
removing the need for Nuxt to handle these requests, freeing it up to handle
rendering SSR requests.

[plausible_proxy]: https://plausible.io/docs/proxy/guides/nginx

Additionally, the reverse proxy may be used in the future for the following:

- Serving static Nuxt content, freeing Nuxt from serving these requests. This is
  considered relatively low value due to Cloudflare caching already handling 99%
  of the benefit this would bring for the vast majority of cases.

## Testing

To test the frontend reverse proxy locally, run `./ov just frontend/up`. To test
the integration with your local Plausible container, follow the existing
instructions in [the frontend analytics documentation][analytics_docs].
Everything should "just work".

[analytics_docs]: /frontend/guides/analytics.md#plausible-set-up-and-first-run
