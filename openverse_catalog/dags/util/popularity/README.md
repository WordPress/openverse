# Popularity

This code allows for the calculation of image popularity within a provider. For example, this allows us to boost Flickr results that have more views than others.

## What this code does

1. Dump the popularity metrics for each row into a TSV.
2. Compute the 85th percentile for each metric, which is required for the popularity calculation. This is a heavyweight database calculation, so we cache it for a really long time.
3. Iterate through the TSV calculating the popularity for each row.
4. UPDATE all rows, setting the `normalized_popularity` key in the `meta_data` column.

## To start calculating popularity data for a provider

1. In your provider script, store the popularity metric you'd like to track in the `meta_data` column. See [stocksnap](https://github.com/WordPress/openverse-catalog/blob/6c172033e42a91bcd8f9bf78fd6b933a70bd88bf/openverse_catalog/dags/provider_api_scripts/stocksnap.py#L175-L185) as an example.
2. Add the provider name and metric to the `IMAGE_POPULARITY_METRICS` constant in the [popularity/sql.py](./sql.py) file.
3. Add the new provider and metric to the `INSERT INTO public.image_popularity_metrics` statement in [0004_openledger_image_view.sql](../../../../docker/local_postgres/0004_openledger_image_view.sql#L45). For now all percentiles should be set to `.85`, this may be adjusted in the future.
