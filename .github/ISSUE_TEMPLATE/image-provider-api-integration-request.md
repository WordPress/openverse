---
name: Image Provider API Integration Request
about: Tell us about an API providing CC-licensed images
title: "[API Integration] Provider name here"
labels: enhancement, not ready for work, providers
assignees: ''

---

## Provider API Endpoint / Documentation
<!-- Please provide links to the API endpoint, and any known documentation -->

## Provider description
<!-- Please provide a clear and concise description of the image provider -->

## Licenses Provided
<!-- Which licenses does the provider use for images (if known) -->

## Provider API Technical info
<!-- Please provide any technical details that might be useful for -->
<!-- implementation, e.g., rate limits, filtering options, overall volume, -->
<!-- etc. -->

## General Recommendations for implementation
<!-- modify this section if necessary -->

- The script should be in the `src/cc_catalog_airflow/dags/provider_api_scripts/` directory.
- The script should have a test suite in the same directory.
- The script must use the `ImageStore` class (Import this from
  `src/cc_catalog_airflow/dags/provider_api_scripts/common/storage/image.py`).
- The script should use the `DelayedRequester` class (Import this from
  `src/cc_catalog_airflow/dags/provider_api_scripts/common/requester.py`).
- The script must not use anything from
  `src/cc_catalog_airflow/dags/provider_api_scripts/modules/etlMods.py`, since
  that module is deprecated.
- If the provider API has can be queried by 'upload date' or something similar,
  the script should take a `--date` parameter when run as a script, giving the
  date for which we should collect images. The form should be `YYYY-MM-DD` (so,
  the script can be run via `python my_favorite_provider.py --date 2018-01-01`).
- The script must provide a main function that takes the same parameters as from
  the CLI. In our example from above, we'd then have a main function
  `my_favorite_provider.main(date)`. The main should do the same thing calling
  from the CLI would do.
- The script *must* conform to [PEP8][pep8]. Please use `pycodestyle` (available via
  `pip install pycodestyle`) to check for compliance.
- The script should use small, testable functions.
- The test suite for the script may break PEP8 rules regarding long lines where
  appropriate (e.g., long strings for testing).

[pep8]: https://www.python.org/dev/peps/pep-0008/

## Examples of other Provider API Scripts
<!-- It's unlikely this section needs to be modified -->

For example Provider API Scripts and accompanying test suites, please see

- `src/cc_catalog_airflow/dags/provider_api_scripts/flickr.py` and
- `src/cc_catalog_airflow/dags/provider_api_scripts/test_flickr.py`, or
- `src/cc_catalog_airflow/dags/provider_api_scripts/wikimedia_commons.py` and
- `src/cc_catalog_airflow/dags/provider_api_scripts/test_wikimedia_commons.py`.
