# 2023-04-11 Project Proposal: Sensitive content report moderation: initial practices

**Author**: @sarayourfriend

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @zackkrida
- [x] @olgabulat

## Project summary

<!-- A brief one or two sentence summary of the project's features -->

While Openverse supports reporting results as mature, we do not have a process
for handling these reports. Likewise, there are significant gaps in our
infrastructure that make it difficult to respond to these reports or to lean on
contributors outside the core maintainers for help processing them. This project
will address these gaps, make it possible to easily and safely respond to
content reports, and develop a baseline process for moderating content based on
reports. It will also rename the "mature content" reports to "sensitive content"
reports. This project is not the end-all, be-all for content report moderation
in Openverse. The assumption should be that future iterations will occur. This
project will establish the baseline practices that we will iterate on. It will
not address or even mention every current or future improvement possible or
required. It is necessary to constrain the scope in this way, otherwise this
project would simply have no ending. In the same vein as "improve search" will
always be an aspect of our ongoing projects, so will "improve content safety".

In addition to the previous broad qualification, this project explicitly does
not cover the following with the understanding that future projects will:

- Sensitive content disputes: allowing users to dispute if they disagree with
  moderation decisions, especially allowing creators to dispute their works
  marked as sensitive.
- A process for reviewing DMCA reports. There is significant overlap in the
  changes to the reports queue, but this project will not address how to handle
  these reports, only sensitive content ones.

## Goals

<!-- Which yearly goal does this project advance? -->

Content safety and moderation.

## Requirements

<!-- Detailed descriptions of the features required for the project. Include user stories if you feel they'd be helpful, but focus on describing a specification for how the feature would work with an eye towards edge cases. -->

Requirements are outlined here, with further details below. Each of these
roughly correspond to a single implementation plan. Requested plans are
[covered in detail below](#required-implementation-plans).

1. Language is updated to use "sensitive" or "sensitive content" rather than
   "mature" where possible.
1. Volunteers outside the core maintainers can access content reports in Django
   admin and work through a queue of pending reports.
1. Bulk actions can be taken to deindex or mark sensitive many results.
1. Use a computer vision API to analyse images on a report to give hints to
   moderators about the contents of the image so that they can safely triage the
   report. Images are blurred in Django admin.
1. Results with confirmed reports are excluded from non-sensitive API queries.
1. If volunteer moderators are identified, work with them to establish an
   initial goal for report response time.

This project does not deal with addressing DMCA reports, though there will
inevitably be some tooling overlap.

### Update copy to use the more general "sensitive" language (requirement 1)

This will be done in code, Django admin copy, and frontend copy only. The
related database tables and columns for existing and future reports should
remain unchanged. While the existing data is small and could be trivially
transferred to new tables with better names, we can avoid that complication for
now and defer that as a potential future improvement. We will also update the
"reason" for reports from `mature` to `sensitive_content`.

```{note}
Design changes should be limited exclusively to copy updates. We will not be adding any new frontend features (like additional requests for information in the report modal) at this time.
```

### Volunteer moderator Django admin tools and access control (requirement 2)

Django admin already includes granular access control tools. We'll need to scope
out the creation of a new Django user group with appropriate permissions, the
management of the users in that group, and how to get volunteer moderators
through Cloudflare Access. One suggested implementation is to add a new
`WordPress/openverse-content-moderators` GitHub group able to access Django
admin. A new GitHub group would have the additional benefit of allowing
discussions about iterations to the moderation processes and tools to include
everyone actually doing the moderation.

The content report admin views already exist, but need some upgrades to improve
moderator quality of life:

- Moderator notes, for moderators to supply an explanatory note for their
  decision. This should be a separate column to the content report description.
- Improved table organisation by displaying the report ID and making that the
  clickable column rather than the status (which is confusing). Improved sorting
  capabilities as well.
- Create a "decision" page that displays all pending and historical reports for
  a given result. Decisions should update all "pending" reports with the new
  status and any explanatory notes. Query the
  [`LogEntry`](https://docs.djangoproject.com/en/4.2/ref/contrib/admin/#logentry-objects)
  for historical decisions to indicate the moderator that made the previous
  decision, if any.
- Run report descriptions through Akismet[^akismet] to flag potentially spammy
  reports.
- Display the following result information (at least) on the decision page:
  - Title
  - Description
  - Image (if any exist)
  - Tags
- Decision page images must be blurred by default. Moderators should be able to
  turn of blurring by default.

[^akismet]:
    We do not currently use Akismet for Openverse, but in writing this it
    occurred to me that we could use it to analyse result descriptions during
    catalog ingestion to evaluate the "usefulness" of a description and develop
    a score to help increase or reduce descriptions that may not be as useful.
    This could be expanded to use bigger NLP APIs or text comparison/analysis
    methods to find other qualities that could factor into the "usefulness" of a
    description.
    [I opened this discussion to further explore these ideas](https://github.com/WordPress/openverse/discussions/1175).

Computer vision based enhancements to Django admin are covered in a
[subsequent section](#computer-vision-based-moderator-safety-tools-requirement-4)
as it is sufficiently complicated to warrant its own set of considerations.

### Bulk moderation actions (requirement 3)

It is occasionally necessary to apply bulk actions to many results, whether the
action is deindexing or marking as sensitive. For example, if a spammy Flickr
user is indexed that only posts ads to pornography websites (before Flickr
moderates them)[^actual-example], we need to be able to deindex or at least mark
all the results for that creator as sensitive.

[^actual-example]:
    This is something that Openverse has actually seen. In other words, this is
    not an imagined scenario. We need to be able to perform these kinds of bulk
    actions.

There are two aspects of this that are worth covering in the baseline admin
improvements:

1. Bulk actions for a specific creator
1. Bulk actions for a set of results selected via a Django admin list view
   retrieved based on search terms

To accomplish this, we'll create a new abstract base-model to capture the
history of bulk moderation actions performed. The base class will require the
user who performed the action, the date of the action, the type of the action
(described below), and required notes describing why the action was taken. The
possible actions are:

- Deindex
- Mark sensitive
- Reindex
- Undo mark sensitive

The last two actions are necessary for "undoing" the first two.

Subclasses must implement a method that returns the list of result identifiers
to take the action for. Each of the actions will trigger the creation or
deletion of corresponding `AbstractDeletedMedia` or `AbstractSensitiveMedia`
(renamed as part of requirement 1 from `AbstractMatureMedia`) for each work
returned by the subclass method. The subclasses must also implement some way of
tracking all the works affected by the action.

For the bulk actions list view, the subclass should have a related join table
tying the bulk action instance identifier to the result identifiers. For the
creator actions, the subclass only needs to indicate the identifier for the
creator. Note that disambiguated creator identification must include the
provider as the same username across different providers may be used by
different distinct creators.

### Computer vision based moderator safety tools (requirement 4)

We will use a computer vision tool to provide additional information about
images to moderators. The intention of this tool is to provide moderators with
as much information as possible about any images for the result so they can have
as much context as possible before deciding to unblur the image. Even if a
moderator has turned off blurring by default, we will still provide (and cache)
the computer vision derived metadata as it may be used by other moderators for
the same or future decisions.

There are many computer vision options that could be evaluated by the
implementation plan. AWS Rekognition, Google Vision API, Azure Computer Vision,
and more. Essentially all the ones I've seen are affordable to us at our current
planned utilisation levels. However, AWS Rekognition is the only one that makes
sense for us to use, because:

- We are already planning to use existing Rekognition data as part of the
  [Rekognition data incorporation](https://github.com/WordPress/openverse/issues/431)
  project later this year.
- Building upon that work, we can cache responses procured during moderation and
  plan to use those as a starting point for a rolling integration of Rekognition
  data as part of
  [using computer vision to further our detection of sensitive content](https://github.com/WordPress/openverse/issues/422)
  and as starting point data for the project to
  [back propagate data from the API into the catalog](https://github.com/WordPress/openverse/issues/420).
- Billing and account management is already worked out for AWS and any other
  provider would require more work in the infrastructure repository to set up
  configuration management and more places to track billing.
- From an ethical perspective, essentially all the major computer vision APIs
  have similar problems, so AWS Rekognition isn't an especially heinous choice.

The implementation plan writer is welcome to explore other options they think
might make sense in spite of those reasons listed above. However, Rekognition
should be considered the "default" option unless another one provides a
substantial benefit that invalidates those reasons.

### Cache management (requirement 5)

There are two aspects to cache management that need to be updated.

1. We need to be able to invalidate cached responses that include results that
   have been deindexed or marked sensitive. This is necessary to ensure that
   sensitive or deindexed results do not continue to appear in Openverse after
   they've been moderated.
2. We need similarly to be able to invalidate cached response for the single
   results, thumbnails, and related results endpoints. This is necessary to
   ensure that links to results that have been deindexed no longer work and that
   links to results that have been marked sensitive are updated to reflect the
   new classification.

Our current caching strategy for the search endpoint is to cache responses at
the Cloudflare level for 1 month based on query params. While this roughly works
for our existing needs, it is incompatible with the first requirement of this
section. Any Cloudflare cache features that would enable granular cache
invalidation on the level of significant query params, like custom cache keys or
cache tags, are all enterprise only features and are not accessible to
Openverse.

On the other hand, all the other endpoints are not query param based and can
easily be purged from Cloudflare's cache by using
[this Cloudflare API endpoint to validate cached pages by URL](https://developers.cloudflare.com/api/operations/zone-purge#purge-cached-content-by-url).

The implementation plan must include a determination for each route relevant to
a particular result for whether it can continue to use Cloudflare's cache or
whether it needs to use the Redis based cache invalidation strategy outlined
below.

```{note}
This change to API cache management does not necessarily entirely preclude the use of Cloudflare's cache for other endpoints. We would need to make significant changes to the TTL of the Cloudflare cache for the endpoints addressed in this requirement if we continued to use it to appropriately reflect the need to have cache changes appear in a timely manner. The implementation plan must include a proposal for whether and to what extent we will continue to use Cloudflare's cache and what benefit we hope to see from it if we do.
```

#### Redis based cache invalidation strategy

In order to invalidate search query responses that include a certain result, we
need to maintain a reverse index of `result indentifier -> cache keys`. When a
given result is marked as sensitive or deindexed due to a report, we need to
bust the cached responses for the keys stored under that result's identifier.
Cache keys also need to be invalidated based on the response cache timeout.
Redis does not support expiring set elements, but we can use a sorted set where
the score is the unix timestamp of the expiration time. To expire cache keys in
sorted sets that have expired cache keys, we can trigger a cache clean up
function periodically during the regular request lifecycle[^workaround-kudos].

[^workaround-kudos]:
    Kudos to
    [this old Google Groups discussion](https://web.archive.org/web/20211205091916/https://groups.google.com/g/redis-db/c/rXXMCLNkNSs)
    for the sorted set workaround.

Django's built in `cache_page` implementation does not work for our purposes out
of the box as it naively caches responses without providing any utility for
custom cache keys or to retrieve the cache key in downstream middleware. There
are two potential approaches an implementation plan could take: we could
implement our own caching middleware entirely that also maintains the reverse
index; or we could monkey patch the `learn_cache_key` function used by the
caching middlewares to attach the cache key on the request context to make it
accessible to downstream middleware that manages the reverse index. The
implementation plan should explore both options and make a determination of
which to pursue.

#### Cloudflare based cache invalidation strategy

We need to be able to invalidate cached responses for pages that will continue
to be cached exclusively in Cloudflare. The implementation plan must describe
how this would be handled when moderators take actions in the Django API.
Cloudflare's cache invalidation endpoints have daily rate limits and the
implementation plan must account for this.

### Moderation response times (requirement 6, optional)

If we are able to identify volunteers to moderate Openverse's content report
queue, we can work with them to establish expectations about response times. To
have insight into the process, we'll need a reporting mechanism that tracks the
number of resolved reports, average response time, and number of open reports on
an ongoing basis.

This requirement is entirely contingent on having found a group of moderators to
advise us on what kinds of response times we should expect.

## Success

<!-- How do we measure the success of the project? How do we know our ideas worked? -->

## Participants and stakeholders

<!-- Who is working on the project and who are the external stakeholders, if any? Consider the lead, implementers, designers, and other stakeholders who have a say in how the project goes. -->

- Lead: @sarayourfriend
- Implementers: @sarayourfriend and others TBD
- Design: @panchovm to
  [assist and confirm copy changes to the frontend](#update-copy-to-use-the-more-general-sensitive-language-requirement-1);
  all other changes are internal and do not need special input from design.
- Stakeholders: TBD; we do not yet know who will be available to volunteer as a
  moderator. Once we do know, the early group of moderators will be consulted
  for advice about process proposals.

## Infrastructure

<!-- What infrastructural considerations need to be made for this project? If there are none, say so explicitly rather than deleting the section. -->

Moderators will need to be able to get through the Cloudflare Access portal. We
will create a new GitHub group `WordPress/openverse-content-moderators` to
enable starting discussions with moderators. This group will be granted access
to the Django admin. Ongoing management of the users in the group should be done
via Terraform.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this project? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

New UI built in Django admin should follow basic accessibility requirements and
be keyboard-navigable. Due to the visual nature of content moderation, it's
unlikely that we'll need to extensively test for screen reader accessibility.
Nonetheless, basic best-practices should be followed.

## Marketing

<!-- Are there potential marketing opportunities that we'd need to coordinate with the community to accomplish? If there are none, say so explicitly rather than deleting the section. -->

Most of the actual changes are internal, but we could market for this project
along the following lines:

- Further discussions about the use of the term "sensitive" rather than "mature"
  and how Openverse is committed to considering all forms of accessibility and
  inclusiveness.
- Announce the start of our use of Rekognition to get more image metadata that
  will eventually be used to improve search relevancy.
- Highlighting the volunteers that choose to work with Openverse to manage our
  content report queue.
- Co-market with Akismet (Automattic) about our integration (unsure about this
  one).

## Required implementation plans

<!-- What are the required implementation plans? Consider if they should be split per level of the stack or per feature. -->

The following implementation plans are requested, split into three streams of
work.

- Copy updates to use "sensitive" rather than "mature"
  - Requirement 1
  - Single item stream
- Response cache management
  - Requirement 5
  - Single item stream
- Django admin improvements
  1. Moderator access control
     - Requirement 2
  1. Content report admin view upgrades
     - Requirement 2
  1. Computer vision API integration for image content safety metadata
     - Requirement 4
     - Must include plans to save responses in a way that could be
       [back propagated to the catalog in the future](https://github.com/WordPress/openverse/issues/420).
       This should be kept simple and should not make finalizing decisions about
       how the data would be stored long term. Storing the responses in Redis
       and using a stable key (result identifier) should be sufficient.
  1. Bulk moderation actions
     - Requirement 3
     - Can be planned concurrently with the previous two plans
  1. Moderation queue progress insights
     - Optional: may be deferred if we haven't found a group of volunteers by
       the time implementation of the other three IPs is finished
     - Requirement 6

The diagram below helps visualise the flow of the work streams.

```{mermaid}
flowchart TD
    subgraph copyUpdates ["Copy updates\n(Requirement 1)"]
    end
    subgraph cache ["Response cache\nmanagement\n(Requirement 5)"]
    end
    subgraph django [Django admin improvements]
    AC["Moderator access control\n(Requirement 2)"]
    VU["Content report admin view upgrades\n(Requirement 2)"]
    CV["Computer vision API integration for\nimage content safety metadata\n(Requirement 4)"]
    Bulk["Bulk moderation actions\n(Requirement 3)"]
    Ins["Moderation queue progress insights\n(Requirement 6)"]

    AC --> VU --> CV
    AC --> Bulk
    CV --> Ins
    Bulk --> Ins
    end
```
