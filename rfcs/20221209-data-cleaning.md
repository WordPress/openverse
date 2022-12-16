# RFC: Cleaning up the upstream database

One of the steps of the [data refresh process for images][data-refresh] is
cleaning data that is not fit for production. This process runs weekly as
Airflow DAGs, the cleaned data is only saved to the API database (DB), which is
replaced when the data refresh finishes, so it needs to be cleaned every time.
At the time of this draft, this cleaning step takes up to 16 hours. It has been
stable in duration given the strategy changed to perform the validations and
transformations of the data upfront, when pulling from providers rather than
when copying the upstream catalog DB into the API DB, but images ingested prior
to this change remained untouched.

The reason why the cleaning step is only applied to images and not to audio
records is related to this change. The audio media type was integrated into
Openverse after the creation of the MediaStore classes, which are the ones
performing general and media-specific validations of the data pulled from
providers.

As seen, this is a costly process in terms of time and CPU resources, and it is
inefficient to repeat it every time. Here I want to propose solving it in origin
by doing a one-time pass by the image table of the upstream DB. We can follow
the approach proposed by a previous Data Engineer contributor to [clean
preexisting data using ImageStore][imagestore], see the details explained in the
pull request and linked issue. The advantage of this way is that we apply not
only the [cleaning steps defined in the ingestion server][cleanin-steps-is] but
all the extra validations which were added later. I can foresee us using the
same workflow in future opportunities if we require applying new modifications
to the existing data, as long as its feasibility is confirmed.

## Plan

After evaluating what needs to be done to get this rid of the duplicated
cleaning step, I collected the relevant issues of the openverse-catalog into a
new milestone, [Data cleaning unification][milestone], and determined a rough
plan to solve them:

    1. Include the ingestion server cleaning steps in the ImageStore class
        - correct tags
        - correct URI protocol
    2. Create and run an image_cleaner workflow as described above
    3. Remove the cleanup step for images from the ingestion process

Olga (@obulat) initiated this work as part of a bigger Data Normalization
project that we are breaking down into smaller pieces, so kudos to her for
identifying some issues as well. We could include more validations before the
second step, in case I have missed any, but keep in mind it could increase the
processing time as well. In a first run we mainly want to get rid of the
duplicated code and the extra wasted processing time.

I would like to see comments on this data project. Do you think the plan makes
sense? Are there alternative approaches to to consider?

[data-refresh]:
  https://github.com/WordPress/openverse-catalog/blob/main/DAGs.md#image_data_refresh
[imagestore]: https://github.com/cc-archive/cccatalog/pull/517
[milestone]: https://github.com/WordPress/openverse-catalog/milestone/11
[cleanin-steps-is]:
  https://github.com/WordPress/openverse-api/blob/e3a5cfb9e7a88f8afb8167b6e6072fa5115e1e53/ingestion_server/ingestion_server/cleanup.py
