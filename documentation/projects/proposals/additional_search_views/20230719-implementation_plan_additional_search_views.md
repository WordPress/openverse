2023-07-20 Implementation Plan: Additional Search Views

**Author**: @obulat

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [ ] TBD
- [ ] TBD

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
- items by the selected creator. The pages re-use the existing image grid and
  audio collection views and can load more images or audio items on the Load
  more button click. The single result pages are updated to add the links to
  these pages, as seen in the Figma mockups: [link to Figma mockup]

## Outlined Steps

<!-- Describe the implementation step necessary for completion. -->

### Page changes

#### Create a page for `tag` / `creator` /`source` collections.

Nuxt allows creating nested dynamic routes like
`/pages/_collection/_mediaType/_term`.

Here, the collection can be `tag`, `creator` or `source`. `mediaType` can be one
of the supported media types (currently, `image` and `audio`). `term` refers to
the actual value of the tag, creator or source name.

This page should use the
[`validate` method](https://v2.nuxt.com/docs/components-glossary/validate/) to
make sure that the `collection`, `searchType` and `term` `params` are valid.

```
`validate({ params, $pinia }): {
const { collection, searchType, term } = params
```

This page should also update the state (`searchType`, `searchTerm` and
`searchBy` filter) in the `search` store and handle fetching using
`mediaStore`'s `fetchMedia` method in the `useFetch` hook. Since it is not
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
[creator desktop](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-56323&mode=design&t=pN0PPAzlKQEKT9tJ-4),
[creator mobile](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-56362&mode=design&t=suLIyJHNmZrM0mPH-4),
[source desktop](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-56381&mode=design&t=suLIyJHNmZrM0mPH-4),
[source mobile](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-56421&mode=design&t=suLIyJHNmZrM0mPH-4),
[tag desktop](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1216-58402&mode=design&t=suLIyJHNmZrM0mPH-4),
[tag mobile](https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-56457&mode=design&t=suLIyJHNmZrM0mPH-4)

The header should have an icon (tag, creator or source), the name of the
tag/creator/source. For source and the creator, there should be an external link
button.

The header should also display the number of results, "251 audio files with the
selected tag", "604 images provided by this source", "37 images by this creator
in Hirshhorn Museum and Sculpture Garden".

#### Add VCreatorLink component

The "by creator" line under the main item on the single result page should be
replaced with a `VCreatorLink` component - a wrapper over `VButton` with a link
to the localized "creator" collection page.

#### Add VSourceLink component

Both the source and the provider should be replaced with `VSourceLink` component
that links to the `source` page. This component is also a wrapper over `VButton`
component.

#### Update VMediaTag component to be a `VButton` wrapping a `VLink`

Each `VMediaTag` should be a `VButton` with `as="VLink"` and should link to the
localized page for the tag collection. Figma link:
https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?type=design&node-id=1200-56515&mode=design&t=nCX20BtJYqMOFAQm-4
[VMediaTag component](https://github.com/WordPress/openverse/blob/c7b76139d5a001ce43bde27805be5394e5732d1a/frontend/src/components/VMediaTag/VMediaTag.vue)
`<VButton variant="filled-gray" size="small" class="label-bold" as="VLink" href="href">{{tag}}</VButton>`.
It should accept `href` as a prop.

### Other interface changes

#### Update the "by" area of the single result page

The "by creator" line should be replaced with a section that is
horizontally-scrollable on mobile, and contains the `VCreatorLink` and
`VSourceLink` components.

#### Update links in the "information" section

Add external link icon to the provider link; add creator link with external link
icon The links to creator in the image and audio single result pages should have
an "external link" icon.
[image creator link](https://github.com/WordPress/openverse/blob/35f08e5710d59f6c10f0cf54103fcce151adfefe/frontend/src/pages/image/_id/index.vue#L62-L73)
and
[audio creator link](https://github.com/WordPress/openverse/blob/35f08e5710d59f6c10f0cf54103fcce151adfefe/frontend/src/components/VAudioTrack/layouts/VFullLayout.vue#L32-L41).
Audio creator link should also be updated to match the image creator link. It
should be a conditional component: `VLink` if the `creator_url` is truthy and
`span` if the `creator_url` is falsy.

Currently, the `foreign_landing_url` is linked to the "source" in the image page
and "provider" in the audio page. The audio page should be updated to match the
image page: the `foreign_landing_url` link should be added to the "source", not
provider.
[Audio provider link](https://github.com/WordPress/openverse/blob/35f08e5710d59f6c10f0cf54103fcce151adfefe/frontend/src/components/VAudioDetails/VAudioDetails.vue#L61C1-L63),
[image source link](https://github.com/WordPress/openverse/blob/35f08e5710d59f6c10f0cf54103fcce151adfefe/frontend/src/components/VImageDetails/VImageDetails.vue#L26-L28)

### Store changes

#### Update the `searchBy` filter in the `search` store

Currently, this filter is shaped as other filters: it is a list of objects with
`code`, `name` and `checked` properties. This is a possible value now: `{
searchBy: { code: "creator", name: "filters.searchBy.creator", checked: true }}.

Since this filter is mutually exclusive (you cannot search by both the creator
and the tag, for example), this shape is very difficult to update.

It is better to set the `searchBy` filter to have one of the possible values:
`{ searchBy: <null|creator|source|tag> }`.

We should also create a new method, `setSearchBy`, in the `search` store, that
would allow directly set the `searchBy` filter value.

### Analytics changes

I am not sure what events we want to add, if any. Should we add `<VIEW>_CLICKED`
events for the new views, or would page views be sufficient?

Should we add a new `SELECT_COLLECTION_ITEM` event similar to
`SELECT_SEARCH_RESULT`?

The clicks on external creator link in the `VCollectionHeader` should be tracked
as `VISIT_CREATOR_LINK` events. We don't have a special event for visiting
source, should we add one, or should they be tracked as generic
`VISIT_EXTERNAL_LINK`?

### Tests

We should add visual-regression tests for the new views. To minimize flakiness
due to slow loading of the images, we should probably use the
`{ filter: brightness(0%); }` trick for the images on the page.

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

## Design

<!-- Note any design requirements for this plan. -->

Figma designs in the dev mode:
https://www.figma.com/file/niWnCgB7K0Y4e4mgxMrnRC/Additional-search-views?node-id=22%3A13656&mode=dev

## Parallelizable streams

<!-- What, if any, work within this plan can be parallelized? -->

The work on components (`VCreatorLink`, `VSourceLink`, `VMediaTag`), and on the
search store changes can be parallelized.

We should create a separate branch for this work because adding the links to the
collection pages on the single result pages (`VCreatorLink`, `VSourceLink`,
`VMediaTag`) before the collection pages are ready is not possible.

## Blockers

<!-- What hard blockers exist which might prevent further work on this project? -->

The main blocker could be the maintainer capacity. If the "creator" API call is
not easy to construct (since we need to combine both the creator and the
provider), this might also be a blocker.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

We should make sure that the search titles are accessible, and the pages clearly
indicate the change of context.

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

If we work on a separate branch, it would be easy to rollback by reverting the
branch merge commit.

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

The biggest risk I see is that this project might be seen as an "invitation" to
scraping. Hopefully, the work on providing the dataset would minimize such
risks.

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->
