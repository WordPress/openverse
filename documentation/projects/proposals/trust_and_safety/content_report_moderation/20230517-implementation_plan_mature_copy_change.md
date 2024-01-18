# 2023-05-17 Implementation Plan: Copy updates `mature` -> `sensitive`

**Author**: @aetherunbound

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @krysal
- [x] @sarayourfriend

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/383)
- [Project Proposal](https://docs.openverse.org/projects/proposals/trust_and_safety/content_report_moderation/20230411-project_proposal_content_report_moderation.html)

## Overview

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

This implementation plan concerns the copy changes necessary for updating
references of `mature` content to `sensitive` content. These changes will be
made to the frontend and Django API, both in code and in web-facing copy. There
should be no design changes or new features as part of this plan, only changes
to copy/text itself. The initial approach for this effort was to only update
field and model names for the API without the need for database migrations
(i.e., using
[Django's built-in tools for specifying different underlying names for fields and tables](https://docs.djangoproject.com/en/4.2/ref/models/options/#table-names)).
After some discussion however, we decided that now would be an ideal time to
perform the migrations since the process will only become more difficult and
take longer as the tables/columns grow.

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

All references to `mature` in code and copy will be updated to `sensitive`,
except where `mature` is
[part of a data model](https://github.com/WordPress/openverse/blob/0f90f84d4bf856297356a918e4cc4fe42d07ffc2/ingestion_server/ingestion_server/elasticsearch_models.py#L118)
or makes the most sense to keep (e.g. when interacting with certain provider
aspects).

## Outlined Steps

<!-- Describe the implementation step necessary for completion. -->

The work is broken up into two services (API and frontend) and those services
are broken into two aspects (code and copy).

### API

#### Code

```{note}
**Update 2023-12-20**: The maintainers determined after the fact that the multi-step
process for updating the table names themselves would be too complicated, so this
plan was modified to only change the names referenced within the code and within
the tables themselves. The previous plan is kept for posterity below.
```

The following model names will need to be updated:

- [`AbstractMatureMedia`](https://github.com/WordPress/openverse/blob/aa16d4f1be7607b12c428886b9890bdd947cc71c/api/api/models/media.py#L332)
- [`MatureImage`](https://github.com/WordPress/openverse/blob/eb0e906e7300e32fae945eb9222ed47a50fb72a2/api/api/models/image.py#L83)
- [`MatureAudio`](https://github.com/WordPress/openverse/blob/aa16d4f1be7607b12c428886b9890bdd947cc71c/api/api/models/audio.py#L263)

The database table name for these models will _not_ be changed, and they will
need to be referenced using
[the `db_table` model attribute](https://docs.djangoproject.com/en/5.0/ref/models/options/#django.db.models.Options.db_table).
This can be accomplished in a zero-downtime manner with a single deployment.

The
[`mature` reason](https://github.com/WordPress/openverse/blob/2041c5df1e9d5d1f9f37e7c177f2e70f61ea5dba/api/api/models/media.py#L22-L21)
(and
[`mature_filtered`](https://github.com/WordPress/openverse/blob/2041c5df1e9d5d1f9f37e7c177f2e70f61ea5dba/api/api/models/media.py#L18-L17)
value) in `AbstractMediaReport` were initially going to be changed as part of
this, they will actually be deprecated in further steps as described by the
[Django admin tools and access control for moderators plan](20231208-implementation_plan_django_admin_moderator_access.md).
They will not be changed at this time.

<details> <summary>Prior plan involving table changes</summary>

The media report tables already use table aliases as well
([`ImageReport`](https://github.com/WordPress/openverse/blob/7b95a4c8eaa9804f53b4be7ac969e04ca437695a/api/api/models/image.py#L121-L122)
and
[`AudioReport`](https://github.com/WordPress/openverse/blob/7b95a4c8eaa9804f53b4be7ac969e04ca437695a/api/api/models/audio.py#L304-L305)) -
since we're already performing table renames as part of this implementation
plan, it makes sense to rename these tables for the same reason.

In order to perform both of these changes in a
[zero-downtime manner](https://docs.openverse.org/general/zero_downtime_database_management.html),
the following steps will need to be taken:

1. Add new models with updated names and fields for `SensitiveImage` and
   `SensitiveAudio`. Also add new models for `ImageReport` and `AudioReport`.
   This will require renaming code references from the existing `ImageReport`
   and `AudioReport` models to `NsfwReport` and `NsfwReportAudio` temporarily
   while maintaining the reference to the existing table name. Said another way:
   - `ImageReport` -> `NsfwReport` _(code only, `db_table` should remain the
     same)_
   - `AudioReport` -> `NsfwReportAudio` _(code only, `db_table` should remain
     the same)_
   - Add `ImageReport` _(new model, `db_table` will not need to be overridden)_
   - Add `AudioReport` _(new model, `db_table` will not need to be overridden)_
2. Modify the API to write to both the old and new tables for each of the above
   instances. On the new report tables, the `mature_filtered` reason should be
   written as `sensitive_filtered`. Data should continue to be read from the
   original tables during this time.
3. Deploy this version of the API.
4. Create a
   [data management command](https://docs.openverse.org/general/zero_downtime_database_management.html#django-management-command-based-data-transformations)
   which copies all data from the original tables to the new tables. The
   `identifier` field can be used for determining which rows have already been
   copied.
5. Deploy this version of the API and run the data management command until no
   more rows need to be copied for each of the columns.
6. Modify the ingestion server to use the new tables as reference for
   determining mature status. Specifically the
   [`exists_in_mature` table check](https://github.com/WordPress/openverse/blob/765a24028baa922b27fc0c38b8ae4c69902eec40/ingestion_server/ingestion_server/queries.py#L33-L37)
   (this will necessarily involve updating tests and initialization SQL as
   well).
7. Remove all code references to the old models (`MatureImage`, `MatureAudio`,
   `NsfwReport`, `NsfwReportAudio`from the API, but leave the models in place
   for the time being. Data should now only be written to and read from the new
   tables.
8. Deploy this version of the API so that the only versions currently deployed
   are writing to the new tables.
9. Remove the old models (`MatureImage`, `MatureAudio`, `NsfwReport`,
   `NsfwReportAudio`) from the API codebase and deploy this version of the API.
   This will remove the old tables from the database.

</details>

Per the
[detecting sensitive textual content project plan](https://docs.openverse.org/projects/proposals/trust_and_safety/detecting_sensitive_textual_content/20230309-project_proposal_detecting_sensitive_textual_content.html#designation-of-results-with-sensitive-terms),
the `mature` field of the media serializer will remain, and will eventually have
a `sensitivity` field added to it to encapsulate specific information about the
reason behind a media being marked sensitive. Those changes are not under the
purview of this implementation plan.

The Elasticsearch model property
[`mature`](https://github.com/WordPress/openverse/blob/2041c5df1e9d5d1f9f37e7c177f2e70f61ea5dba/ingestion_server/ingestion_server/elasticsearch_models.py#L118)
will also not be affected as part of this effort.

#### Copy

Most changes necessary for updating the copy in the Django Admin UI will be
reflected by the code changes that are made above (since the Admin UI
introspects the code directly). The only other references that will need to be
updated are the `help_text` values in the following places:

- [`MatureImage::media_obj`](https://github.com/WordPress/openverse/blob/098925afa90b26881b4b4d3e2baffa69049692c0/api/api/models/image.py#L102)
- [`MatureAudio::media_obj`](https://github.com/WordPress/openverse/blob/098925afa90b26881b4b4d3e2baffa69049692c0/api/api/models/audio.py#L282)
- [`AbstractMatureMedia::media_obj`](https://github.com/WordPress/openverse/blob/2041c5df1e9d5d1f9f37e7c177f2e70f61ea5dba/api/api/models/media.py#L356)
- [`MediaSerializer::mature`](https://github.com/WordPress/openverse/blob/2041c5df1e9d5d1f9f37e7c177f2e70f61ea5dba/api/api/serializers/media_serializers.py#L433)
- [`MediaSearchRequestSerializer::mature`](https://github.com/WordPress/openverse/blob/2041c5df1e9d5d1f9f37e7c177f2e70f61ea5dba/api/api/serializers/media_serializers.py#L122)

Changes to `help_text` will produce no-op migrations within Django.

### Frontend

#### Code

At present, the following locations within the codebase make reference to the
word `mature`:

- `src/components/VErrorSection/meta/VErrorSection.stories.mdx`
- `src/components/VFilters/VFilterChecklist.vue`
- `src/components/VFilters/VSearchGridFilter.vue`
- `src/constants/content-report.ts`
- `src/constants/filters.ts`
- `src/stores/media/index.ts`
- `src/stores/media/single-result.ts`
- `src/stores/search.ts`
- `src/types/media.ts`
- `src/utils/content-safety.ts`
- `src/utils/search-query-transform.ts`
- `test/playwright/e2e/report-media.spec.ts`
- `test/playwright/e2e/search-query-server.spec.ts`
- `test/unit/fixtures/audio.js`
- `test/unit/specs/components/v-content-report-form.spec.js`
- `test/unit/specs/stores/search-store.spec.js`
- `test/unit/specs/utils/search-query-transform.spec.js`

The following objects within the codebase will need to be renamed (along with
any references that depend on them):

- [`Filters` interface](https://github.com/WordPress/openverse/blob/f676e57e2dbe9e92f568d413ade83ce6c2f38f9b/frontend/src/constants/filters.ts#L28)
- [`NonMatureFilterCategory` type](https://github.com/WordPress/openverse/blob/f676e57e2dbe9e92f568d413ade83ce6c2f38f9b/frontend/src/constants/filters.ts#L31)
- [`mediaFilterKeys` constant references](https://github.com/WordPress/openverse/blob/f676e57e2dbe9e92f568d413ade83ce6c2f38f9b/frontend/src/constants/filters.ts#L37)
- [`filterCodesPerCategory` constant](https://github.com/WordPress/openverse/blob/f676e57e2dbe9e92f568d413ade83ce6c2f38f9b/frontend/src/constants/filters.ts#L86)
- [Content report constant](https://github.com/WordPress/openverse/blob/6baeb6b41430a586d4ed6c6976b7bae8ba1167fa/frontend/src/constants/content-report.ts#L2)
- References to `Fake ~50% of results as mature` in
  [`src/stores/media/single-result.ts`](https://github.com/WordPress/openverse/blob/74da3d852a45c514c0159038c86164a26d70504b/frontend/src/stores/media/single-result.ts#L122)
  and
  [`src/stores/media/index.ts`](https://github.com/WordPress/openverse/blob/74da3d852a45c514c0159038c86164a26d70504b/frontend/src/stores/media/index.ts#L432).
- [Search store references](https://github.com/WordPress/openverse/blob/92ea64c6d4ac1801785eadf99a3782628eadad06/frontend/src/stores/search.ts)
- [Content report utilities](https://github.com/WordPress/openverse/blob/74da3d852a45c514c0159038c86164a26d70504b/frontend/src/utils/content-safety.ts#L10-L23)
- All affected tests.

The following references _will not be_ affected because they correspond to
either the data model or to the API query parameter `mature`. The query
parameter will be changed to `include_sensitive_results` in the API
[as part of another project](https://docs.openverse.org/projects/proposals/trust_and_safety/detecting_sensitive_textual_content/20230309-project_proposal_detecting_sensitive_textual_content.html#filtering)

- [Search query transform utilities](https://github.com/WordPress/openverse/blob/92ea64c6d4ac1801785eadf99a3782628eadad06/frontend/src/utils/search-query-transform.ts#L31)
  _(query parameter)_
- [`Media` interface attributes](https://github.com/WordPress/openverse/blob/930a2ec4583d53e2f17e7aa397dc9b3b32cc8ebb/frontend/src/types/media.ts#L48)
  _(data model)_

#### Copy

Almost all copy changes necessary can be made in the
[`en.json5` base translations file](https://github.com/WordPress/openverse/blob/2041c5df1e9d5d1f9f37e7c177f2e70f61ea5dba/frontend/src/locales/scripts/en.json5).
The `filters.mature` key can be removed entirely, as it references a filter
which no longer exists.

## Dependencies

### Infrastructure

<!-- Describe any infrastructure that will need to be provisioned or modified. In particular, identify associated potential cost changes. -->

This work will include several migrations for the API as well as a deployment
for the ingestion server, which will need to be deployed one after another in
production as described in [the API section](#api).

### Tools & packages

<!-- Describe any tools or packages which this work might be dependent on. If multiple options are available, try to list as many as are reasonable with your own recommendation. -->

No other tools or packages should be required.

### Other projects or work

<!-- Note any projects this plan is dependent on. -->

This work intersects with, but is distinct from, the
["Detecting and Blurring Sensitive Textual Content" project](https://docs.openverse.org/projects/proposals/trust_and_safety/detecting_sensitive_textual_content/index.html).

## Design

<!-- Note any design requirements for this plan. -->

No design work should be necessary.

## Parallelizable streams

<!-- What, if any, work within this plan can be parallelized? -->

The frontend copy work and the API copy & code work can be done simultaneously.
The frontend code work should wait until the API work is complete so the content
reporting using `sensitive` rather than `mature` is available on the API prior
to the frontend code changes. It will also need to take into account and
coordinate with the changes being made as part of the
["Fetching, blurring sensitive results"](https://docs.openverse.org/projects/proposals/trust_and_safety/detecting_sensitive_textual_content/20230506-implementation_plan_frontend_blurring_sensitive.html)
implementation.

## Blockers

<!-- What hard blockers exist which might prevent further work on this project? -->

No known blockers at the time of drafting.

## API version changes

<!-- Explore or mention any changes to the API versioning scheme. -->

If the API backwards compatibility for using `mature` rather than `sensitive` on
the content reporting endpoint is removed, we will need to change the API
versioning scheme. The removal of this backwards compatibility is not strictly a
requirement for the success of this IP, so there is not an urgent necessity to
change the API version.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

No accessibility changes should be necessary, as this should only affect copy.

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

In the case that we needed to roll back, the code and copy changes could be
easily undone.

The API changes would be more difficult to roll back, as they would require the
reverse of the multi-step migrations described in [the API section](#api). This
would still be feasible, but we should be clear before moving forward that the
changes to the table names are ones we wish to make at this juncture.

## Localization

<!-- Any translation or regional requirements? Any differing legal requirements based on user location? -->

Any changes that we make to the frontend copy will need to have new or existing
translations associated with it.

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

We should be careful that any changes made to the API as part of this effort are
done in a backwards compatible way, and that we do not introduce any breaking
behavior.
