# 2023-07-20 Implementation Plan: Additional Search Views

**Author**: @obulat

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @zackkrida
- [x] @sarayourfriend

```{note}
The original version of this plan was significantly revised on 2024-03-01 due to problems discovered during the implementation work. See [Plan revisions](#plan-revisions) section for summary of changes, and [Original plan](/projects/proposals/additional_search_views/SUPERSEDED-20230719-implementation_plan_additional_search_views.md) for the original version.
```

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/410)
- [Project Proposal](https://docs.openverse.org/projects/proposals/additional_search_views/20230424-project_proposal_additional_search_views.html)
- [Milestone](https://github.com/WordPress/openverse/milestone/17)

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

API returns all media with the selected tag, from the selected source or by the
selected creator within a given source, sorted by date added to Openverse, when
`collection` parameter is set in the search endpoints. Sample API URLs:

- `/v1/<images|audio>/?collection=tag&tag=cat`
- `/v1/<images|audio>/?collection=source&source=flickr`
- `/v1/<images|audio>/?collection=creator&source=flickr&creator=Photographer`

Frontend allows to browse media items by a selected creator, source, or with a
selected tag on `/collection` page. Sample frontend URLs:

- `/<image|audio>/collection?tag=cat`,
- `/<image|audio>/collection?source=flickr` and
- `/<image|audio>/collection?source=flickr&creator=Photographer`.

These pages are indexed by search engines, have relevant SEO properties and can
be shared with an attractive thumbnail and relevant data.

The single result pages are updated to add the links to source, creator and tag
collections.

## Step-by-step plan

1. API changes: Add API collection ES query builder for exact matching of the
   `tag`, `source` and `creator` fields to the search controller. Update the
   request serializer to validate collection parameters.
2. Add a switchable "additional_search_views" feature flag.
3. Update the store and utils used to construct the API query to allow for
   retrieving the collections by `tag`, `creator` or `source`.
4. Create a page for collections that handles parameter validation, media
   fetching and setting relevant SEO properties.
5. Create the new components: `VCollectionHeader`, `VCollectionLink` and `VTag`.
6. Update the single result pages: tags area, the "creator" and "source" area
   under the main media item.
7. Add the Analytics event `VISIT_SOURCE_LINK` and update where
   `VISIT_CREATOR_LINK` is sent. Also update the `SELECT_SEARCH_RESULT`,
   `REACH_RESULT_END` and `LOAD_MORE` events to include the new views.
8. Cleanup after the feature flag is removed:
   - Remove conditional rendering (single result pages, sources page).
   - Remove the `additional_search_views` feature flag and `VMediaTag`
     component.
   - Stabilize the `collection` query parameters in the API (remove `unstable__`
     prefix)

## Step details

### 1. API changes

Currently, when filtering the search results, the API matches some query
parameters in a fuzzy way: an item matches the query if the field value contains
the query string as a separate word. When indexing the items, we "analyze" them,
which means that we split the field values by whitespace and stem them. We also
do the same to the query string. This means that the query string "bike" will
match the field value "bikes", "biking", or "bike shop".

For these pages, however, we need an exact match.

One alternative implementation considered when writing this plan was to use the
database instead of the Elasticsearch to get the results. This would make it
easy to get the exact matches. However, there are some problems with using the
database rather than ES to access anything:

- The database does not cache queries in the same way that ES does. Repeated
  queries will not necessarily be as efficient as from ES.
- The database does not score documents at all, so the order will different
  dramatically to the way that ES would order the documents. That's an issue
  with respect to popularity data today already, but will become even more of an
  issue if we start to score documents based on other metrics as theorised by
  our search relevancy discussions.
- `creator` is not indexed in the API database, so a query against it will be
  very slow.

#### Search controller updates

To enable exact matching, we don't need any changes in Elasticsearch index
because we already have the `.keyword` fields for `creator`, `source` and
`tags`. Using these fields in the `term` query will allow for exact matching of
the values (e.g. `bike` will not match `bikes` or `biking`), and will probably
make the search more performant since the fields and the query won't need to be
analyzed and/or stemmed.

The search controller's `search` method should be refactored to be smaller and
allow for more flexibility when creating the search query. The current
implementation of query building consists of 3 steps.

We **first** apply the `filters`: if the query string has any parameters other
than `q`, we use them for exact matches that must be in the search results, or
must be excluded from the search results (if the parameter starts with
`exclude_`).

**Then**, if `q` parameter is present, we apply the `q` parameter, which is a
full-text search within `tags`, `title` and `description` fields. This is a
fuzzy search, which means that the query string is stemmed and analyzed, and the
field values are stemmed and analyzed, and the documents are scored based on the
relevance of the match. If `q` is not present, but one of the
`creator`/`source`/`tags` parameter is present, we search within those fields
for fuzzy matches.

**Finally**, we apply the ranking and sorting parameters, and "highlight" the
fields that were matched in the results.

The search controller needs to be updated to extract the first 2 steps into a
`build_search_query` method. A new `build_collection_query` should be added and
used when the `collection` parameter is present. This method should create a
filter query for the relevant field and value.

The pagination and dead link cleanup should be the same for additional search
queries as for the default search queries.

#### Search request serializer updates

_The initial version of this plan proposed to add new API endpoints and use path
parameters for the values (e.g., `/image/tag/cat`) to make the URLs more
readable, easier to share, will be easier to cache or perform cache invalidation
required by [#1969](https://github.com/WordPress/openverse/issues/1969).
However, since tags and creator names contain characters that are special for
path segments (`/`, `?` and `&`) that cannot be properly encoded, this approach
turned out to be not feasible. See
[PR#3793](https://github.com/WordPress/openverse/pull/3793) for attempts at
making the path parameters work_

```{note}
The new query parameters (`collection` and `tag`) will have `unstable__` prefix until this project is
launched. In the text below, for brevity, the prefix is omitted.
```

The collections will use the `search` endpoint with `collection` query parameter
set to `tag`, `creator` or `source`, and the following additional query
parameters:

- `collection=tag` will require `tag` parameter to be set
- `collection=source` will require `source` parameter to be set
- `collection=creator` will require both `source` and `creator` parameter to be
  set.

This means that the existing `source` and `creator` parameters will be reused.
For the tag collection, the new singular `tag` parameter should be used, rather
than the existing plural `tags`, since we are only presenting a single tag.

`MediaSearchRequestSerializer` should be updated to validate the `collection`
parameter. This validator will check that the request contains the necessary
additional parameters: `source` for `collection=source`, `creator` and `source`
for `collection=creator`, and `tag` for `collection=tag`. It will only validate
that the parameters _have_ values, but not the values themselves.

The `MediaSearchRequestSourceSerializer` currently splits the `source` parameter
value by `,` and validates that each value is a valid source. This validator
will be updated:

- If the `collection` parameter is not present, it will behave as before.
- If the `collection` parameter is set to `source` or `creator`, it will take
  the value of `source` as is, and check if this value is present in the list of
  valid sources, without splitting it by `,`. If the value is not valid, it will
  return a 400 error, showing the invalid value, as well as a list of valid
  sources for the media type.
- If the `collection` parameter is set to `tag`, it will return the value as-is,
- because it will be ignored in the search controller.

The documentation for the `source` parameter should be updated to reflect that
it accepts a single source when there is a `collection` parameter set to
`source` or `creator`, and a comma-separated list of sources when there is no
`collection` parameter. Similarly, the documentation for `creator` parameter
should say that it accepts a comma-separated list of values when there is no `q`
parameter, and a single URI-encoded value when the `collection=creator`
parameter is present. The creator serializer does not need any changes as the
parsing (splitting by comma for regular searches and URI-decoding for `creator`
collections) is only done in the search controller.

The additional documentation for the search parameters should be added as a
draft so that it's not published on the API documentation site until we launch
this project and remove the `unstable__` prefix.

### 2. Add the `additional_search_views` feature flag

The flag should be switchable, and off by default. This will mean that the
changes are visible on [staging](https://staging.openverse.org) when the flag is
switched on using the preferences page. When the features are stable, we will
turn the flag on to test the new views in production. After we conclude that the
project is successful, we will remove the flag and the conditional rendering.

### 3. Nuxt store and API request changes

We can reuse the search store as is for these pages.

_Previously, the frontend search store had a `searchBy` filter that allowed to
search within the `creator` field. When `searchBy` value was set, the API `q`
parameter was replaced with the `<searchBy>=<searchTerm>` API query parameter.
This filter was removed because `searchBy` is not strictly a filter that can be
toggled on or off_

#### Add `strategy` and `collectionParams` to `search` store

The `strategy` parameter will be used to determine the API request query
parameters. If it is set to `"search"`, then the API query will be created using
the current approach. If it is set to `"collection"`, the query will be
constructed using the new method (`buildCollectionQuery`) to set `collection`
and other relevant parameters using the new `collectionParams` object in the
store. It will _not_ be setting the filter parameters such as license or
category, and will ignore such unsupported query parameters.

### 4. Create collection pages

We should add the following pages:

- `/image/collection.vue`
- `/audio/collection.vue`

#### Validation of the collection query parameters

This page will use the `collection` middleware to validate the collection query
parameters:

- if `collection` is set to `creator`, there should also exist a `source`
  parameter
- `source` parameter should be validated to be an existing source using the
  provider store
- `creator` and `tag` parameters should be decoded using `decodeURIComponent`.

The middleware validates that the values of parameters is not empty, and that
the `source` parameter is an existing source in the provider store. If the
values are invalid, the 404 yellow error page is shown.

#### Fetching the media

This page should also update the state (`searchType`, `collectionParams` and
`strategy`) in the `search` store and handle fetching using `mediaStore`'s
`fetchMedia` method in the `useFetch` hook.

The media collections should be updated (not as part of this project) to move
the load more methods to the page that fetches the media (i.e., `search.vue` or
`collection.vue`), and the `mediaStore` should be updated to remove the load
more methods.

#### SEO

This page should also have relevant SEO properties, and should be indexed by the
search engines.

The following titles should be used for the pages:

- "Images by Olga at Flickr" for the creator page
- "Audio from Wikimedia" for the source page
- "Images with the cat tag" for the tag page

There are i18n consideration for these titles that we will work on during the
implementation. It is important to make the titles translatable, which is
difficult if the non-translatable dynamic names are used inside the sentence due
to different sentence structures.

The generic Openverse thumbnail will be used. We could also generate a thumbnail
for the collection pages in the future, but this is not in scope for this
project.

### 5. Update the single result pages

All of these changes should be conditional on whether the
`additional_search_views` feature flag is enabled.

The Figma links for new designs:

- [Image single result](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-63284&mode=dev)
- [Audio single result](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-63285&mode=dev)

#### Update the `VCollectionLink` area on the single result page

The content info line under the main item on the single result page should be
replaced with a section that has two buttons: one for a creator link and a
source link. This section should be horizontally scrollable on mobile.
Initially, we planned to implement a scroll-snap (example:
https://play.tailwindcss.com/AbfA33Za50), however, since the source and creator
names can be very long, a scroll snap can make the links unusable, as they will
always snap to the start of the source name and not allow scrolling past it.

#### Use `VTag` with links for the tags

The tags should be rendered using the `VTag` component with links to the tag
collection page.

#### Update the tags area on the single result page

The tags area should be collapsible to make long lists of tags collapsible:
https://github.com/WordPress/openverse/issues/2589

#### Add the information popover next to source and provider links

The information popover should be added next to the source and provider links
that explains the difference between the source and provider.

[**Figma link**](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-56521&mode=dev)

### 6. New and updated components

#### Extract the `VAudioCollection` component

Currently, it is not possible to reuse the audio collection from the audio
search result page because it is a part of the `audio.vue` page. We should
extract the part that shows the loading skeleton, the column of `VAudioTrack`
rows and the Load more section into `VAudioCollection` component. This component
will be reused in the audio search page and on the Additional search views.

#### Add a `VCollectionHeader` component

The header should have an icon (tag, creator or source) and the name of the
tag/creator/source. For source and the creator, there should be an external link
button if it's available (not all creators have urls).

The header should also display the number of results, "251 audio files with the
selected tag", "604 images provided by this source", "37 images by this creator
in Hirshhorn Museum and Sculpture Garden".

```{note}
There are sources that only have works by one creator. In this case, we
should probably still have two separate pages for the source and the creator,
but we might want to add a note that the creator is the only one associated with
this source.
```

**Figma links**: **creator**
[desktop](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-56323&mode=design&t=pN0PPAzlKQEKT9tJ-4)
and
[mobile](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-56362&mode=design&t=suLIyJHNmZrM0mPH-4),
**source**
[desktop](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-56381&mode=design&t=suLIyJHNmZrM0mPH-4)
and
[mobile](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-56421&mode=design&t=suLIyJHNmZrM0mPH-4),
**tag**
[desktop](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1216-58402&mode=design&t=suLIyJHNmZrM0mPH-4)
and
[mobile](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-56457&mode=design&t=suLIyJHNmZrM0mPH-4).

#### Add `VCollectionLink` component

This component should be a `VButton` with `as="VLink"`, should have an icon, and
should accept a localized link to the creator or source page.

**Figma link**:
[creator and source buttons](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-56972&mode=dev)

#### Create a new `VTag` component to be a `VButton` wrapping a `VLink`

The
[`VMediaTag` component](https://github.com/WordPress/openverse/blob/c7b76139d5a001ce43bde27805be5394e5732d1a/frontend/src/components/VMediaTag/VMediaTag.vue)
should be updated to be a `VButton` wrapping a `VLink`, and should match the
design in the
[Figma mockups](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-56515&mode=design&t=nCX20BtJYqMOFAQm-4).
The component should link to the localized page for the tag collection.

#### Update links in the "information" section

The links to creator in the
[image](https://github.com/WordPress/openverse/blob/35f08e5710d59f6c10f0cf54103fcce151adfefe/frontend/src/pages/image/_id/index.vue#L62-L73)
and
[audio](https://github.com/WordPress/openverse/blob/35f08e5710d59f6c10f0cf54103fcce151adfefe/frontend/src/components/VAudioTrack/layouts/VFullLayout.vue#L32-L41)
single result pages Information section should have an "external link" icon.

Audio creator link should also be updated to match the image creator link. It
should be a conditional component: `VLink` if the `creator_url` is truthy and
`span` if the `creator_url` is falsy.

Currently, the `foreign_landing_url` is linked to the "source" in the
[image](https://github.com/WordPress/openverse/blob/35f08e5710d59f6c10f0cf54103fcce151adfefe/frontend/src/components/VImageDetails/VImageDetails.vue#L26-L28)
page and "provider" in the
[audio page](https://github.com/WordPress/openverse/blob/35f08e5710d59f6c10f0cf54103fcce151adfefe/frontend/src/components/VAudioDetails/VAudioDetails.vue#L61C1-L63).
The audio page should be updated to match the image page: the
`foreign_landing_url` link should be added to the "source", not provider.

### 7. Additional analytics events

Some existing events will already track the new views events. The views can be
tracked as page views, so no separate event is necessary. The only way to access
the pages is directly or via links on the single results, which will all be
captured by standard page visits. Clicking on the items will be tracked as
`SELECT_SEARCH_RESULT` events. These events can be narrowed by pathname
(`/search` or `/collection`, for example) to determine where the event occurred.

Analytics events should be added or updated:

- The clicks on external creator link in the `VCollectionHeader` should be
  tracked as `VISIT_CREATOR_LINK` events.

- We should also a special event for visiting source `VISIT_SOURCE_LINK`,
  similar to `VISIT_CREATOR_LINK`.

- The `REACH_RESULT_END`, `LOAD_MORE` and `SELECT_SEARCH_RESULT` events should
  add strategy (`search`/`tag`/`creator`/`source`) and set `query` to tag name,
  source name or source/creator pair: `cat`, `flickr` or `flickr/Olga`.

### 8. Cleanup after the feature flag is enabled in production

After the feature flag is enabled in production, we should remove the
conditional rendering on the single result pages and remove the
`additional_search_views` feature flag and (old) `VMediaTag` component.`

Remove the `unstable__` prefix from the `collection` and `tag` query parameters
in the API.

### Tests

We should add visual-regression tests for the new views. To minimize flakiness
due to slow loading of the images, we should probably use the
[ `{ filter: brightness(0%); }` trick](https://github.com/WordPress/openverse/blob/b4b46b903731870015c475d2c08eebef7ec6b25b/frontend/test/playwright/visual-regression/pages/pages.spec.ts#L49-L55)
for the images on the page.

The search store tests should be updated to reflect the changes to the filters.

## Dependencies

### Infrastructure

<!-- Describe any infrastructure that will need to be provisioned or modified. In particular, identify associated potential cost changes. -->

These views potentially might cause more load on our infrastructure due to
increase in scraping activity.

### Tools & packages

<!-- Describe any tools or packages which this work might be dependent on. If multiple options are available, try to list as many as are reasonable with your own recommendation. -->

No new tools or packages are necessary.

### Other projects or work

<!-- Note any projects this plan is dependent on. -->

Not applicable.

## Design

<!-- Note any design requirements for this plan. -->

[Figma designs in the dev mode](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?node-id=22%3A13656&mode=dev)

## Parallelizable streams

<!-- What, if any, work within this plan can be parallelized? -->

The API changes can be done independently of the frontend changes, although they
should be finished before the final testing of the frontend changes.

Adding the new components (step 3), Nuxt store update (step 4) and the
`additional_search_views` feature flag (step 5) can be done in parallel, and are
not dependent on anything.

The work on the single result pages (step 7) can be done in parallel with the
work on the collection pages (step 6), but should follow the previous steps.

The new frontend views can use the existing query parameters (`source`,
`creator` and `tags` - instead of `tag`) until the API changes are implemented
since this _will_ return _some_ relevant results, and changing the query
parameter names is easy.

## Blockers

<!-- What hard blockers exist which might prevent further work on this project? -->

The main blocker could be the maintainer capacity.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

We should make sure that the search titles are accessible, and the pages clearly
indicate the change of context.

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

To roll back the changes, we would need to set the feature flag to `OFF`.

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

The biggest risk I see is that this project might be seen as an "invitation" to
scraping. Hopefully, frontend rate limiting and the work on providing the
dataset would minimize such risks.

## Plan revisions

This plan was significantly revised on 2024-03-01 due to problems discovered
during the implementation of the path parameters. The API changes were updated
to use query parameters instead of path parameters, and to describe the new
request serializer. The frontend store and API request changes were updated to
use the new query parameters. The collection pages descriptions were updated to
reflect the new query parameters. The steps were reordered to reflect the new
implementation plan. More details on SEO was added in the collection pages
section. The analytics event parameters were updated.
