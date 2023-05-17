# 2023-05-17 Implementation Plan: Copy updates `mature` -> `sensitive`

**Author**: @aetherunbound

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [ ] @krysal
- [ ] @dhruvkb

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
to copy/text itself. Field and model names for the API should also be updated
when possible, but without the need for database migrations (i.e., using
[Django's built-in tools for specifying different underlying names for fields and tables](https://docs.djangoproject.com/en/4.2/ref/models/options/#table-names)).

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

The following models will need to be updated. Since we want to avoid a migration
with this work, they will need to
[explicitly reference the old table names using `Meta::db_table`](https://docs.djangoproject.com/en/4.2/ref/models/options/#table-names).

- [`AbstractMatureMedia`](https://github.com/WordPress/openverse/blob/2041c5df1e9d5d1f9f37e7c177f2e70f61ea5dba/api/api/models/media.py#L334-L333)
- [`MatureImage`](https://github.com/WordPress/openverse/blob/2041c5df1e9d5d1f9f37e7c177f2e70f61ea5dba/api/api/models/image.py#L83)
- [`MatureAudio`](https://github.com/WordPress/openverse/blob/2041c5df1e9d5d1f9f37e7c177f2e70f61ea5dba/api/api/models/audio.py#L263)

The
[`mature` reason](https://github.com/WordPress/openverse/blob/2041c5df1e9d5d1f9f37e7c177f2e70f61ea5dba/api/api/models/media.py#L22-L21)
(and
[`mature_filtered`](https://github.com/WordPress/openverse/blob/2041c5df1e9d5d1f9f37e7c177f2e70f61ea5dba/api/api/models/media.py#L18-L17)
value) in `AbstractMediaReport` definition will also need to be changed to
`sensitive` and `sensitive_filtered` respectively. In order to remain backwards
compatible with the frontend, incoming references on reports for `mature` will
need to be mapped to the new value.

Per the
[detecting sensitive textual content project plan](https://docs.openverse.org/projects/proposals/trust_and_safety/detecting_sensitive_textual_content/20230309-project_proposal_detecting_sensitive_textual_content.html#designation-of-results-with-sensitive-terms),
the `mature` field of the media serializer will remain, and will eventually have
a `sensitivity` field added to it to encapsulate specific information about the
reason behind a media being marked sensitive. Those changes are not under the
purview of this IP.

The Elasticsearch model property
[`mature`](https://github.com/WordPress/openverse/blob/2041c5df1e9d5d1f9f37e7c177f2e70f61ea5dba/ingestion_server/ingestion_server/elasticsearch_models.py#L118)
will also not be affected.

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
[`en.json5` base translations file](https://github.com/WordPress/openverse/blob/2041c5df1e9d5d1f9f37e7c177f2e70f61ea5dba/frontend/src/locales/scripts/en.json5#L1-L0).
The `filters.mature` key can be removed entirely, as it references a filter
which no longer exists.

## Dependencies

### Infrastructure

<!-- Describe any infrastructure that will need to be provisioned or modified. In particular, identify associated potential cost changes. -->

### Tools & packages

<!-- Describe any tools or packages which this work might be dependent on. If multiple options are available, try to list as many as are reasonable with your own recommendation. -->

### Other projects or work

<!-- Note any projects this plan is dependent on. -->

## Alternatives

<!-- Describe any alternatives considered and why they were not chosen or recommended. -->

## Design

<!-- Note any design requirements for this plan. -->

## Parallelizable streams

<!-- What, if any, work within this plan can be parallelized? -->

## Blockers

<!-- What hard blockers exist which might prevent further work on this project? -->

## API version changes

<!-- Explore or mention any changes to the API versioning scheme. -->

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

## Privacy

<!-- How does this approach protect users' privacy? -->

## Localization

<!-- Any translation or regional requirements? Any differing legal requirements based on user location? -->

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->

```

```
