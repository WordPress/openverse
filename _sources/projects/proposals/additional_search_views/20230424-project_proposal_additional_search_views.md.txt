# 2023-04-24 Project Proposal: Additional search views

**Author**: @fcoveram

## Reviewers

- [x] @obulat
- [x] @krysal

## Project summary

The Openverse team has decided to enhance the browsing experience by
incorporating new content views for providers, tags, and creators. This feature
will allow users to share collections detached of individual searches.

## Goals

Search Experience

## Requirements

The project adds three additional views for the Nuxt frontend where users
interact in the following ways.

### Results by tag

Users land on the tag results page by clicking on the tag in the single result
page or by opening a tag results link (for instance,
[www.openverse.org/tags/image/cat](https://www.openverse.org/tags/image/cat)).

The results page shows the name of the tag and all the items of the selected
media type that have this exact tag applied. The items are sorted by
`ingested_on` field in descending order.

For instance, the `cat` tag page will show only images that have the `cat` tag,
not items tagged with `cats` .

### Results by source

Users land on the source results page by clicking on the source name in the
single result page or by opening a source results link (for instance,
[http://www.openverse.org/providers/wikimedia/image/](https://www.openverse.org/providers/wikimedia/image/))

The results page shows the name of the source and all the items from this source
in the selected media type. The items are sorted by `ingested_on` field in
descending order.

### Results by creator

Users land on the creator results page by clicking on the creator’s name in the
single result page or by opening a creator results link (for instance,
[http://www.openverse.org/creators/cat_flickr](https://www.openverse.org/creators/cat_flickr))

The results page shows the creator’s name and the source where the content comes
from, and all items in the selected media type. The items are sorted by
`ingested_on` field in descending order.

### Changes

The three pages described above will require changes to:

- Nuxt frontend: Adding pages for the specific views by reusing the current
  result layouts for each media type. The pages will only show the results,
  without the ability to search within them. Because of that, the views will use
  the "content" header (without the search bar, search type selection or filters
  button) and will not have a filter sidebar.
- API: adding `filter` parameters that would enable retrieving all items of a
  certain media type that have the specific property (tag/provider/creator and
  source pair). These will work similarly to the way filter parameters such as
  `license` work now, returning only the items with the specific filter.
  Searching within the filtered items is not in scope of this project.

## Success

The project will be considered successful when:

- Each tag, provider, and creator has a standalone and shareable page.
- Page uses are tracked by derivating data from existing events.

## Participants and stakeholders

- Design: @panchovm
- Implementation:

## Infrastructure

No infrastructure changes are required.

## Required implementation plans

- API
- Frontend
- Design issue
