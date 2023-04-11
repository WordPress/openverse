# 2023-04-11 Project Proposal

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [ ] @zackkrida
- [ ] @olgabulat

## Project summary

<!-- A brief one or two sentence summary of the project's features -->

While Openverse supports reporting results as mature, we do not have a process
of handling these reports. Likewise, there are significant gaps in our
infrastructure that make it difficult to respond to these reports or to lean on
contributors outside the core maintainers for help processing them. This project
will address these gaps, make it possible to easily and safely respond to
content reports, and develop a baseline process for moderating content based on
reports. It will also rename the "mature content" reports to "sensitive content"
reports. This project is not the end-all, be-all for content report moderation in Openverse. The assumption should be that future iterations will occur. This project will establish the baseline practices that we will iterate on. It will not address, explore, or even mention _every_ current or future improvement required. It is necessary to constrain the scope in this way, otherwise this project would simply have no ending. In the same vein as "improve search" will always be an aspect of our ongoing projects, so should "improve content safety".

In addition to the previous broad qualification, this project explicitly does not cover the following with the understanding that future projects will:

- Sensitive content disputes: allowing users to dispute if they disagree with
  moderation decisions, especially allowing creators to dispute their works
  marked as sensitive.
- DMCA reports, though there will inevitably be some overlap with the tools
  being created, especially for cache management.

## Goals

<!-- Which yearly goal does this project advance? -->

Content safety and moderation.

## Requirements

<!-- Detailed descriptions of the features required for the project. Include user stories if you feel they'd be helpful, but focus on describing a specification for how the feature would work with an eye towards edge cases. -->

Requirements are outlined here, with further details below.

1. Language is updated to use "sensitive" or "sensitive content" rather than
   "mature" where possible.
1. Volunteers outside the core maintainers can access content reports in Django
   admin and work through a queue of pending reports.
1. Bulk actions can be taken to deindex or mark sensitive many results. It is not overwhelmingly cumbersome to do so.
1. Use a computer vision API to analyse images on a report to give hints to
   moderators about the contents of the image so that they can safely triage the
   report. Images are blurred in Django admin.
1. Results with confirmed reports are quickly updated to be excluded from
   non-sensitive API queries.
1. If volunteer moderators are identified, work with them to establish an
   initial goal for report response time.

This project does not deal with addressing DMCA reports, though there will
inevitably be some tooling overlap.

### Rename update database schema to use new "sensitive" language (requirement 1)

This will be done in code, Django admin copy, and frontend copy only. The
related database tables and columns for existing and future reports should
remain unchanged. While the existing data is small and could be trivially
transferred to new tables with better names, we can avoid that complication for
now and defer that as a potential future improvement. We will also update the
"reason" for reports from `mature` to `sensitive_content`.

### Volunteer moderator Django admin tools and access control (requirement 2)

Django admin already includes granular access control tools. We'll need to scope
out the creation of a new Django user group with appropriate permissions, the
management of the users in that group, and how to get volunteer moderators
through Cloudflare Access. One suggested implementation is to add a new
`WordPress/openverse-content-moderators` GitHub group to access Django admin. A
new GitHub group would have the additional benefit of allowing discussions about
iterations to the moderation processes and tools to include everyone actually
doing the moderation.

The content report admin views already exist, but need some upgrades to improve
moderator quality of life:

- Moderator notes, if moderators want to supply an explanatory note for their
  decision.
- Improved table organisation by displaying the report ID and making that the
  clickable column rather than the status (which is confusing).
- Create a "decision" page that displays all pending and historical reports for
  a given result. Decisions should update all "pending" reports with the new
  status and any explanatory notes. Query the
  [`LogEntry`](https://docs.djangoproject.com/en/4.2/ref/contrib/admin/#logentry-objects)
  for historical decisions to indicate the moderator that made the previous
  decision, if any.
- Run report descriptions through Akismet to flag potentially spammy reports.
- Display result information (title, description, etc) on the decision page.

Computer vision based safety tools are covered in the next section as they're
sufficiently complicated to warrant their own set of considerations.

### Bulk moderation actions (requirement 3)

It is occasionally necessary to apply bulk actions to many results, whether the action is deindexing or marking as sensitive. For example, if a spammy Flickr user is indexed that only posts ads to pornography websites (before Flickr moderates them)[^actual-example], we need to be able to deindex or at least mark all the results for that creator as sensitive.

[^actual-example]: This is something that Openverse has actually seen. In other words, this is not an imagined scenario. We need to be able to perform these kinds of bulk actions.

There are two aspects of this that are worth covering in the baseline admin improvements:

1. Bulk actions for a specific creator
1. Bulk actions for a set of results selected via a Django admin list view retrieved based on search terms

To accomplish this, we'll create a new abstract base-model to capture the history of bulk moderation actions performed. The base class will require the user who performed the action, the date of the action, the type of the action (described below), and required notes describing why the action was taken. The possible actions are:

- Deindex
- Mark sensitive
- Reindex
- Undo mark sensitive

Subclasses must implement a method that returns the list of result identifiers to take the action for. Each of the actions will trigger the creation or deletion of corresponding `AbstractDeletedMedia` or `AbstractSensitiveMedia` (renamed as part of requirement 1 from `AbstractMatureMedia`) for each work returned by the `get_result_identifier` methods. The subclasses must also implement some way of tracking all the works affected by the action.

For the bulk actions list view, the subclass should have a related join table tying the bulk action instance identifier to the result identifiers. For the creator actions, the subclass only needs to indicate the identifier for the creator. Note that disambiguated creator identification must include the provider as the same username across different providers may be used by different distinct creators.

### Computer vision based moderator safety tools (requirement 4)

There are many computer vision options that could be evaluated by the
implementation plan. AWS Rekognition, Google Vision API, Azure Computer Vision,
and more. Essentially all the ones I've seen are affordable to us at our current
planned utilisation levels. However, AWS Rekognition is the only one that makes
sense for us to use, because:

- We are already planning to use existing Rekognition data as part of the
  [Rekognition data incorporation](https://github.com/WordPress/openverse/issues/431)
  project later this year.
- We can cache responses procured during moderation and plan to use those as a
  starting point for a rolling integration of Rekognition data.
- Billing and account management is already worked out for AWS and any other
  provider would require more work in the infrastructure repository to set up
  configuration management and more places to track billing.
- From an ethical perspective, essentially all the major computer vision APIs
  have the same problems, so AWS Rekognition isn't an especially heinous choice.

The implementation plan writer is welcome to explore other options they think
might make sense in spite of those reasons listed above. However, Rekognition
should be considered the "default" option unless another one provides a
substantial benefit that invalidates those reasons.

### Cache management (requirement 5)

Our current caching strategy is to cache responses at the Cloudflare level for 1
month based on query params. While this roughly works for our existing needs, it
will not be workable for content moderation due to the inability to granularly
invalidate cached pages via query params. Any Cloudflare cache features that
would enable this like custom cache keys or cache tags, are all enterprise only
features and are not accessible to Openverse.

In order to invalidate responses that include a certain result, we need a
reverse index of `result ID -> cache keys`. When a given result is marked as
sensitive due to a report, we need to bust the cache keys under that result ID.
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
accessible to downstream middleware that manages the reverse index.

### Moderation response times (requirement 6, optional)

If we are able to identify volunteers to moderate Openverse's content report
queue, we can work with them to establish expectations about reponse times. To
have insight into the process, we'll need a reporting mechanism that tracks the
number of resolved reports, average response time, and number of open reports on
an ongoing basis.

## Success

<!-- How do we measure the success of the project? How do we know our ideas worked? -->

## Participants and stakeholders

<!-- Who is working on the project and who are the external stakeholders, if any? Consider the lead, implementers, designers, and other stakeholders who have a say in how the project goes. -->

- Lead: @sarayourfriend
- Implementers: @sarayourfriend and others TBD
- Design: Not needed for this project
- Stakeholders: TBD; we do not yet know who will be available to volunteer as a
  moderator. Once we do know, the early group of moderators will be consulted
  for advice about process proposals.

## Infrastructure

<!-- What infrastructural considerations need to be made for this project? If there are none, say so explicitly rather than deleting the section. -->

Moderators will need to be able to get through the Cloudflare Access portal. We
will create a new GitHub group `WordPress/openverse-content-moderators` to
enable starting discussions with moderators. This group will be granted access
to the Django admin. Ongoing management of the users in the group should be done
via terraform.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this project? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

New UI built in Django admin should follow basic accessibility requirements and
be keyboard-navigable. Due to the visual nature of content moderation, it's
unlikely that we'll need to extensively test for screen reader accessibility.
Nonetheless, basic best-practices should be followed.

## Marketing

<!-- Are there potential marketing opportunities that we'd need to coordinate with the community to accomplish? If there are none, say so explicitly rather than deleting the section. -->

Maybe introducing content moderators? Making noise about how we're working on
improving Openverse in this way?

## Required implementation plans

<!-- What are the required implementation plans? Consider if they should be split per level of the stack or per feature. -->

In no particular order, the following implementation plans are requested:

- Response cache management
  - Requirement 5
- Moderator access control, Django admin improvements, and "mature" to
  "sensitive" language updates
  - Requirements 1 and 2
- Computer vision API integration for image content safety metadata
  - Requirement 4
  - Must include plans to cache responses in a way that could be upstreamed to
    the catalogue in the future
- Moderation queue progress insights
  - Optional: may be deferred if we haven't found a group of volunteers by the
    time implementation of the other three IPs is finished
  - Requirement 6

The computer vision API IP should be written after the Django admin improvements
IP, only to make it easier to understand the context of the "decision page" and
how the computer vision API information would be displayed.
