# 2023-07-20 Implementation Plan: Additional Search Views

**Author**: @obulat

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [ ] @zackkrida
- [ ] @sarayourfriend

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/410)
- [Project Proposal](https://docs.openverse.org/projects/proposals/additional_search_views/20230424-project_proposal_additional_search_views.html)

## Overview

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

This plan describes the changes that need to be added on the frontend: the new
components, pages and store.

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

Three collection pages are added to Openverse:

- items with the selected tag
- items from the selected source (provider)
- items by the selected creator.

The pages re-use the existing image grid and audio collection views and can load
more images or audio items on the Load more button click. The single result
pages are updated to add the links to these pages, as seen in the Figma mockups:

- [Image single result](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-63284&mode=dev)
- [Audio single result](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-63285&mode=dev)

For the creator pages, a separate API media view is added to get the items that
match the creator and source pair exactly.

## Outlined Steps

<!-- Describe the implementation step necessary for completion. -->

### API changes

Currently, when filtering the search results, the API matches some query
parameters in a fuzzy way: an item matches the query if the field value contains
the query string as a separate word. When indexing the items, we "analyze" them,
which means that we split the field values by whitespace and stem them. We also
do the same to the query string. This means that the query string "bike" will
match the field value "bikes", "biking", or "bike shop".

For most of these pages, we need an exact match instead. This section will
describe each page and the necessary changes.

#### Source page

To get the items from the selected source, we can use the `source` query
parameter:
[https://api.openverse.engineering/v1/images/?source=met](https://api.openverse.engineering/v1/images/?source=met)

There is a limited number of sources, and we validate the `source` parameter
against the full list. This means that the `source` parameter will be matched
exactly.

#### Creator page

We could update the Elasticsearch index and the search controller to allow for
exact matching by the `creator` field. However, I think there is an easier way
that does not require any changes to the indexes: use the Django ORM to filter
the items by the creator name and the provider name.

We can add a media view at
`/api/v1/<media>/creator/?q=<creator_name>&provider=<provider_name>`. It would
use `self.get_queryset().filter(creator=creator, provider=provider)` to get all
the items by the creator from the provider. This view would also need to filter
out dead links, and return a paginated response.

#### Tag page

To get the items matching a tag, we can use the `tags` query parameter with a
quoted value.
[https://api.openverse.engineering/v1/images/?tags=%22black%20cat%22](https://api.openverse.engineering/v1/images/?source=met)
This query returns all images with tags that contain the phrase "black cat".

This would not match the tags exactly, but tags page is supposed to show all
items that are associated with the same topic or category.

We could also add a media view at `/api/v1/<media>/tags/?q=<tag_name>`, but it
is difficult to implement because the tags are stored as a list JSONField model.

### Nuxt store changes

We can re-use the search store as is for these pages. Currently, the store uses
the `searchBy` filter to determine the shape of the API query. If `searchBy`
value is set, then the `q` parameter is replaced with the
`<searchBy>=<searchTerm>` query parameter. API query parameters are constructed
from the search store state in the
[`prepare-search-query-params` method](https://github.com/WordPress/openverse/blob/b4b46b903731870015c475d2c08eebef7ec6b25b/frontend/src/utils/prepare-search-query-params.ts#L22-L25)

We can update the `searchBy` filter to have one of the possible values:
`{ searchBy: <null|creator|source|tag> }`. Then, this value would be used to
construct the API query.

#### Update the `searchBy` filter

The `searchBy` filter will be used to determine the shape of the API query.
While currently these parameters will be mutually exclusive (we can only search
by one of them), we might want to allow searching by multiple parameters in the
future.

For other filters, we only use `toggle` method to update the value. However, for
`searchBy`, we need to be able to check one of the `searchBy` parameters, and
uncheck the others. To enable that, we should add a new `search` store method.

This change should also update `prepare-search-query-params` to use the
`searchBy` filter value to construct the API query:

```typescript
const prepareSearchQuery = (
  searchParams: Record<string, string>,
  mediaType: SupportedMediaType
) => {
  if (searchParams.searchBy) {
    if (searchBy === "creator") {
      // the name of the source is stored in the `<mediaType>Provider` filter
      return {
        creator: searchTerm,
        source: searchParams[`${mediaType}Provider`],
      }
    } else if (searchBy === "source") {
      return { source: searchParams[`${mediaType}Provider`] }
    } else if (searchBy === "tag") {
      // The parameter is plural in the API
      return { tags: searchTerm }
    }
  } else {
    // Current search query transform
  }
}
```

### Page changes

#### Create a page for `tag` / `creator` /`source` collections.

Nuxt allows creating nested dynamic routes like
`/pages/_collection/_mediaType/_term`.

Here, the collection can be `tag`, `creator` or `source`. `mediaType` can be one
of the supported media types (currently, `image` and `audio`). `term` refers to
the actual value of the tag, creator or source name.

This page should use the
[`validate` method](https://v2.nuxt.com/docs/components-glossary/validate/) to
make sure that the `collection`, `mediaType` and `term` `params` are valid.

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
using `mediaStore`'s `fetchMedia` method in the `useFetch` hook. Since it is not
possible to change the path or query parameters from this page client-side,
fetching can be much simpler than on the current search page (that has to watch
for changes in the route and fetch if necessary).

This page should have the common header (title, button - link to the source
external URL or the creator URL, and the summary of item counts in the
collection), and a nested component: the image grid or the audio collection.

### New and updated components

#### Extract the `VAudioCollection` component

Currently, it is not possible to reuse the audio collection from the audio
search result page because it is a part of the `audio.vue` page. We should
extract the part that shows the loading skeleton, the column of `VAudioTrack`
rows and the Load more section. This component will be reused in the audio
search page and on the Additional search views. One thing that I'm not sure
about here is whether the analytics events should stay the same and be sent from
all pages - or if we should somehow differentiate the events coming from
different search views.

#### Add a `VCollectionHeader` component

Figma links:

- creator
  [desktop](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-56323&mode=design&t=pN0PPAzlKQEKT9tJ-4)
  and
  [mobile](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-56362&mode=design&t=suLIyJHNmZrM0mPH-4)
- source
  [desktop](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-56381&mode=design&t=suLIyJHNmZrM0mPH-4)
  and
  [mobile](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-56421&mode=design&t=suLIyJHNmZrM0mPH-4)
- tag
  [desktop](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1216-58402&mode=design&t=suLIyJHNmZrM0mPH-4)
  and
  [mobile](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-56457&mode=design&t=suLIyJHNmZrM0mPH-4)

The header should have an icon (tag, creator or source), the name of the
tag/creator/source. For source and the creator, there should be an external link
button.

The header should also display the number of results, "251 audio files with the
selected tag", "604 images provided by this source", "37 images by this creator
in Hirshhorn Museum and Sculpture Garden".

Note: There are sources that only have works by one creator. In this case, we
should probably still have two separate pages for the source and the creator,
but we might want to add a note that the creator is the only one associated with
this source.

#### Add `VCollectionLink` component and update the title and links container

The "by creator" line under the main item on the single result page should be
replaced with a section that has two buttons: one for a creator link and a
source link. These links should be `VButtons` with `as="VLink"` and should link
to the localized page for the creator or the source pages. This section should
be horizontally scrollable on mobile. It should implement a scroll-snap
(example: https://play.tailwindcss.com/AbfA33Za50)

#### Update `VMediaTag` component to be a `VButton` wrapping a `VLink`

The
[`VMediaTag` component](https://github.com/WordPress/openverse/blob/c7b76139d5a001ce43bde27805be5394e5732d1a/frontend/src/components/VMediaTag/VMediaTag.vue)
should be updated to be a `VButton` wrapping a `VLink`, and should match the
design in the
[Figma mockups](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-56515&mode=design&t=nCX20BtJYqMOFAQm-4).
The component should link to the localized page for the tag collection.

### Other interface changes

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

### Analytics changes

The views can be tracked as page views, so no separate event is necessary. The
only way to access the pages is directly or via links on the single results,
which will all be captured by standard page visits.

Clicking on the items will be tracked as `SELECT_SEARCH_RESULT` events. These
events can be narrowed by pathname (`/search` or `/tag\*`, for example) to
determine where the event occurred.

Two analytics events should be added:

- The clicks on external creator link in the `VCollectionHeader` should be
  tracked as `VISIT_CREATOR_LINK` events.

- We should also a special event for visiting source `VISIT_SOURCE_LINK`,
  similar to `VISIT_CREATOR_LINK`.

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

The work on components (`VCollectionLink`, `VMediaTag`), and on the search store
changes can be parallelized.

We should create a `additional_search_views` feature flag for this work because
adding the links to the collection pages on the single result pages
(`VCollectionLink`, `VMediaTag`) before the collection pages are ready is not
possible.

## Blockers

<!-- What hard blockers exist which might prevent further work on this project? -->

The main blocker could be the maintainer capacity.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

We should make sure that the search titles are accessible, and the pages clearly
indicate the change of context.

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

To rollback the changes, we would need to set the feature flag to `OFF`.

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

The biggest risk I see is that this project might be seen as an "invitation" to
scraping. Hopefully, frontend rate limiting and the work on providing the
dataset would minimize such risks.

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->
