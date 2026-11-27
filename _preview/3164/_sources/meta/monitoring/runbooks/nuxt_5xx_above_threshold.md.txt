# Run Book: Nuxt 5XX request count above threshold

```{admonition} Metadata
Status: **Unstable**

Maintainer: @dhruvkb

Alarm link:
- [production-nuxt](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:alarm/Nuxt+Production+HTTP+5XX+responses+count+over+threshold)
```

## Severity guide

Confirm there is not an outage.

Check if the connection to the API from Nuxt has been broken, which can result
in Nuxt returning 5XX errors.

If the connection is present and working, try to determine the source of the 5XX
errors (this can be checked by observing paths in the Cloudflare logs).

- If the API requests are returning 2XX responses, the severity is low. But you
  should continue to investigate the source of 5XX errors, which could be an
  external service like Plausible.
- If the API requests are returning 5XX responses, the severity is high. Further
  investigation into the API side is warranted to determine the cause for the
  5XX responses. Also refer to the
  [API 5XX runbook](/meta/monitoring/runbooks/index.md).

<!-- TODO: Update link to /meta/monitoring/runbooks/api_5xx_above_threshold.md -->

## Historical false positives

Nothing registered to date.

## Related incident reports

- _2023-08-28, 12:06 to 12:24 UTC_:

  5XX responses spiked to ~591 due to Plausible degradation. This was not
  detrimental to UX.
