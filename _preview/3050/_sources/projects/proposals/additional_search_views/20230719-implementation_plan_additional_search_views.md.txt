# 2023-07-20 Implementation Plan: Additional Search Views

**Author**: @obulat

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @zackkrida
- [ ] @sarayourfriend

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/410)
- [Project Proposal](https://docs.openverse.org/projects/proposals/additional_search_views/20230424-project_proposal_additional_search_views.html)
- [Milestone](https://github.com/WordPress/openverse/milestone/17)

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

API endpoints return all media with the selected tag, from the selected source
or by the selected creator, sorted by date added to Openverse.

Frontend allows to browse media items by a selected creator, source, or with a
selected tag.

The single result pages link to these collection views; the external links are
also updated to clearly show that they are external.

## Step-by-step plan

1. Update the Elasticsearch index to enable exact matching of the `tag`,
   `source` and `creator` fields (both the query analyzer and the index
   analyzer). This will require reindexing.
2. Add API endpoints for exact matching of the `tag`, `source` and `creator`
   fields.
3. Create the new components: `VCollectionHeader`, `VCollectionLink` and `VTag`.
4. Update the store and utils used to construct the API query to allow for
   searching by `tag`, `creator` or `source`, in addition to the current search
   by title/description/tags combination.
5. Add a switchable "additional_search_views" feature flag.
6. Create a page for `tag` / `creator` /`source` collections. The page should
   handle fetching and updating the search store state.
7. Update the single result pages: tags area, the "creator" and "source" area
   under the main media item.
8. Add the Analytics event `VISIT_SOURCE_LINK` and update where
   `VISIT_CREATOR_LINK` is sent.
9. Cleanup after the feature flag is removed:
   - Remove conditional rendering on the single result pages.
   - Remove the `additional_search_views` feature flag and `VMediaTag`
     component.

## Step details

### 1. Search controller updates

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

To enable exact matching, we don't need any changes in Elasticsearch index
because we already have the `.keyword` fields for `creator`, `source` and
`tags`. We just need to use them in the query. This will allow for exact
matching of the values (e.g. `bike` will not match `bikes` or `biking`), and
will probably make the search more performant since the fields and the query
won't need to be analyzed and/or stemmed.

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

The new search controller should allow for using different filters for the first
step and to not use the full-text search. We should also create a new serializer
for collection search requests. It should include the common parameters for
`list` requests, such as `page` and `page_size`, and the parameters for the
exact matches: `tag`, `creator` and `source`.

### 2. New API endpoints

The new routes should use path parameters instead of query parameters for the
`tag`, `creator` and `source` values. This will make the URLs more readable,
easier to share, will be easier to cache or perform cache invalidation required
by #1969. The path parameters should be URL encoded to preserve special
characters and spaces.

Instead of using query strings, we can describe the resource via the path:
`/<media type>/source/<source>/creator/<creator>` is very clean, easy to read
and understand, and very easy to manage the cache for because it is a static
path. The source page can use the same route by leaving off the creator. This
removes the need to manage specific query params as well and would allow us to
add querying within these routes more easily in the future behind the regular q
parameter if we wanted.

For the tag route, the singular `tag` rather than plural `tags` should be used
for legibility since we are presenting a single tag.

The new views should use the same pagination and dead link cleanup as the search
views.

### 3. New and updated components

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

_Note_: There are sources that only have works by one creator. In this case, we
should probably still have two separate pages for the source and the creator,
but we might want to add a note that the creator is the only one associated with
this source.

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

### 4. Nuxt store and API request changes

We can re-use the search store as is for these pages. Currently, the frontend
can perform searches by `source` parameter. If `searchBy` value is set, then the
`q` parameter is replaced with the `<searchBy>=<searchTerm>` query parameter.

For this project, we should add new values to the `searchBy` filter.

The API request URL is constructed from the search store state in the
[`prepare-search-query-params` method](https://github.com/WordPress/openverse/blob/b4b46b903731870015c475d2c08eebef7ec6b25b/frontend/src/utils/prepare-search-query-params.ts#L22-L25).
We will need to update this method to use the `searchBy` filter value to
construct the API request path as described in the "API Changes" section.

#### Update the `searchBy` filter

The `searchBy` filter will be used to determine the shape of the API request.
While currently these parameters will be mutually exclusive (we can only search
by one of them), we might want to allow searching by multiple parameters in the
future.

For other filters, we only use `toggle` method to update the value. However, for
`searchBy`, we need to be able to check one of the `searchBy` parameters, and
uncheck the others. To enable that, we should add a new `search` store method.

If `searchBy` is set to `tag`, `creator` or `source`, then the media store
should create search path instead of the search query. So, instead of calling
`prepareSearchQuery` to create the query parameters, it should call
`prepareSearchPath` to create the path.

```typescript
const searchPathOrQuery = searchBy
  ? prepareSearchPath(searchParams, mediaType)
  : prepareSearchQuery(searchParams, mediaType)

const prepareSearchPath = (
  searchParams: Record<string, string>,
  mediaType: SupportedMediaType
) => {
  let path
  if (searchBy === "tag") {
    path = `${mediaType}/tag/${searchTerm}`
  } else {
    path = `${mediaType}/source/${searchParams[`${mediaType}Provider`]}`
    if (searchBy === "creator") {
      path += `/creator/${searchTerm}`
    }
  }
  return path
}
```

### 5. Add the `additional_search_views` feature flag

The flag should be switchable, and off by default.

### 6. Create a page for `tag` / `creator` /`source` collections.

Nuxt allows creating nested dynamic routes like
`/pages/_collection/_mediaType/_term`.

We should add the following pages:

- `/pages/_mediaType/tag/_tag`
- `/pages/_mediaType/source/_source`
- `/pages/_mediaType/source/_source/creator/_creator` (this page might not be
  needed as it might be handled by the source page)

To make sure that the `mediaType`, `source` and `creator` parameters are valid,
this page should use the
[`validate` method](https://v2.nuxt.com/docs/components-glossary/validate/) to
make sure that and show an error page if necessary.

```typescript
function validate({ params, $pinia }): boolean {
  const { collection, mediaType, term } = params
  // Check that collection is one of ["tag", "creator" or "source"],
  // and mediaType is one of `supportedMediaTypes`.
  // Check that `term` is correctly escaped.
  // If the params are not valid, return `false` to show the error page.
  return isValid ? true : false
}
```

This page should also update the state (`searchType`, `searchTerm` and
`searchBy` and `provider` filters) in the `search` store and handle fetching
using `mediaStore`'s `fetchMedia` method in the `useFetch` hook.

Since it is not possible to change the path or query parameters from this page
client-side, fetching can be much simpler than on the current search page (that
has to watch for changes in the route and fetch if necessary).

This page should use `VCollectionHeader` and the image grid or the audio
collection.

### 7. Update the single result pages

All of these changes should be conditional on whether the
`additional_search_views` feature flag is enabled.

The Figma links for new designs:

- [Image single result](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-63284&mode=dev)
- [Audio single result](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-63285&mode=dev)

#### Update the `VCollectionLink` area on the single result page

The content info line under the main item on the single result page should be
replaced with a section that has two buttons: one for a creator link and a
source link. This section should be horizontally scrollable on mobile. It should
implement a scroll-snap (example: https://play.tailwindcss.com/AbfA33Za50)

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

### 8. Additional analytics events

Some existing events will already track the new views events. The views can be
tracked as page views, so no separate event is necessary. The only way to access
the pages is directly or via links on the single results, which will all be
captured by standard page visits. Clicking on the items will be tracked as
`SELECT_SEARCH_RESULT` events. These events can be narrowed by pathname
(`/search` or `/tag\*`, for example) to determine where the event occurred.

Two analytics events should be added or updated:

- The clicks on external creator link in the `VCollectionHeader` should be
  tracked as `VISIT_CREATOR_LINK` events.

- We should also a special event for visiting source `VISIT_SOURCE_LINK`,
  similar to `VISIT_CREATOR_LINK`.

### 9. Cleanup after the feature flag is enabled in production

After the feature flag is enabled in production, we should remove the
conditional rendering on the single result pages and remove the
`additional_search_views` feature flag and (old) `VMediaTag` component.

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

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->
