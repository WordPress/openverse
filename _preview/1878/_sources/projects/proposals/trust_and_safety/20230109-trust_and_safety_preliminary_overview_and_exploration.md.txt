# 2023-01-09 Project Proposal

This document seeks to explore the facets of Trust and Safety that Openverse
needs to consider as we undertake the important work of building systems and
tools for content moderation. The bulk of this practice is a list of user
stories and accompanying assumptions and technical and process requirements
needed to meet the assumptions.

## General considerations

### Accessibility

While considering the user stories and accompanying requirements and
assumptions, keep in mind that content moderation is not just about keeping
Openverse legal. It is also about accessibility. If Openverse users are
confronted with sensitive materials without their consent, then Openverse is not
an accessible platform. Likewise, Openverse is used by a diverse set of people,
including children in educational environments. Consider that the age and other
intersectionalities of a user will influence how they're affected by content
moderation policies (both successes and failures).

### The relevance of scanning for known illegal materials

Note that a distinct feature of Openverse _as it exists today, in early 2023_ is
that there is no method for anyone to upload content directly to us. Every
single provider is manually added to the catalogue. We currently rely heavily on
the fact that our content providers have their own content moderation policies
and procedures. The majority of our content providers (to the best of our
knowledge) that have user generated content automatically scan that content for
illegal materials. The other providers are either unlikely to ever include
illegal materials (GLAM institutions) or manually review each submission by hand
(WordPress Photo Directory). This may not always be the case. One of the future
goals for Openverse is for websites (and WordPress sites, in particular) to be
able to automatically add themselves as providers of openly licensed content.
Once that is possible, then it will become even more imperative that Openverse
scans materials for illegal materials. Even before then, however, I think it is
prudent for us to consider doing it earlier because running the risk of
distributing illegal content (which is also universally heinous content) is not
something Openverse ever wants to be involved in, even if it is only because one
of our upstream content providers made a mistake.

### Openverse as a content "host"

While Openverse does not, to a meaningful extent, "host" the original content
ingested from providers, it does have specially cached resources that, if not
appropriately managed, could persist, even if a result is removed. For example,
our thumbnails are heavily cached on infrastructure that we control (or, more
accurately, infrastructure that exists under a PaaS account we're responsible
for). Removing a result from showing in search is not sufficient for completely
removing it from Openverse's distribution of the content. A particularly
difficult corner case for this is if a result is removed from the upstream
provider for content moderation reasons and then removed from our catalogue upon
re-ingestion, the cached thumbnail persists in the current implementation.
Maintaining the thumbnail cache is a critical aspect of ensuring that Openverse
does not continue to accidentally be a distributor of content we do not wish
to/have a legal obligation not to. Several of the technical requirements
mentioned below involve juggling various important, interconnected, and
interrelated caches: caches of image classification data obtained at search
time, link status caches, and thumbnail caches.

### GLAM institutions and the relationship of historical collections to sensitive visual and textual materials

Museum and library collections often include historical material with sensitive
content. For example, a museum may hold, catalogue, and distribute a photograph
with its original caption even if the caption describes the subject in an
offensive or inaccurate way. Especially common examples of this are images of
racialised people with original captions that use slurs or other derogatory
language to describe the subject. I (Sara) do not know if this is something that
currently exists in Openverse, but it is something we could discuss with
providers if we discovered it to ensure that we are capturing the relevant
metadata. For example, some providers may include a note clarifying that a
caption or title of a work is "from the original source" rather than the
museum's own description of a collection item. In these cases, it would be
imperative for Openverse to also include that information if we surface the
relevant text fields because it may serve double duty of giving historical
context for a potentially sensitive and controversial cultural artefact _and_ as
a manually attached content warning. Once Openverse has a way of scanning our
catalogue for sensitive textual material, if we discover any of it to be coming
from GLAM institutions, we should keep this in mind and work with the
institution to understand how we can appropriately represent these sensitive
historical materials.

### The difference between offensive, sensitive, and illegal

Openverse could choose to take different approaches to material that is
considered to be variously offensive, sensitive, or illegal. For illegal
materials, we should just remove it as much as possible and prevent its
accidental reinclusion. This is clear and is not just a legal requirement but is
also a baseline responsibility that we should consider. However, the definition
of illegal probably depends somewhat (though not entirely, as there are certain
classes of illegal materials that are essentially universally agreed upon) on
what jurisdictions we need to abide by. Certain classifications of "illegal"
material may not correspond to Openverse's priorities, for example, if a state
entity attempts to use "illegality" to censor criticism. Luckily, Openverse does
not need to make a distinct decision in this case as we can fall back to the
WordPress Foundation's policies in this regard.

When it comes to offensive and sensitive materials, however, the issue is more
complicated. There are probably certain sensitive materials which are not
illegal but that Openverse does not want to distribute. The WordPress Foundation
probably already has a position on this kind of thing, and we should lean on
pre-existing definitions and policies in that regard. For everything else,
however, we'll need to make our own decisions about how to represent the
material. One option is to generously blur visual content that may be offensive
or otherwise sensitive. Additionally, adding content warnings as much as
possible, both for visual and textual material.

## Process user stories

1. As an Openverse user, I expect results that are removed from upstream
   providers due to containing illegal materials will be automatically removed
   from Openverse so that Openverse does not accidentally continue to distribute
   materials that have been removed from the provider
1. As an Openverse content moderator, I want to be able to queue the removal of
   a result from the index without a prior report existing so that I can skip
   the report generation step
1. As an Openverse content moderator, I want to be able to prevent results from
   showing for a search so that searches do not include results that may not
   follow Openverse's content policies
1. As an Openverse content moderator, I can review pending media reports and
   make documented decisions about the validity and needed action for a report
   so that manual or automated systems know what to do with a particular
   reported result
1. As an Openverse content moderator or user, I expect that a result that has
   been removed from Openverse will not re-appear even if uploaded by a
   different user so that duplicate uploads will not cause already removed
   results from re-appearing
1. As an Openverse content moderator, I expect that a result marked for removal
   will also remove any other results that may be duplicates of the removed
   result so that I do not have to manually remove results that have similar
   perceptual hashes
1. As an Openverse content moderator, I want a clear definition of what is and
   is not allowed to exist within Openverse so that I can take decisive action
   on content reports
1. As an Openverse developer, I want a clear definition for what is and is not
   allowed to exist within Openverse so that I can build tools that identify
   results that should not be accessible in Openverse without them needing to be
   discovered by a content moderator or user
1. As an Openverse user, I want results with sensitive content to require an
   explicit opt-in to view so that I am not exposed to sensitive content without
   my consent
1. As an Openverse user, I want to know why a result is marked as "sensitive"
   without needing to view the result itself so that I can make an informed
   decision about whether a sensitive (but not policy-violating) result is
   relevant to what I am searching for
1. As an Openverse content moderator, I want to be able to bulk remove results
   from a given search so that a search that has mixed material (results that
   follow and results that do not follow Openverse's content policies) can be
   easily dealt with
1. As an Openverse content moderator, I want to be able to remove all results
   from a particular creator so that if a problematic creator is discovered and
   all (or practically all, or mostly all) their content does not follow
   Openverse's content policies, they can be easily removed
1. As an Openverse content moderator, I want to be able to mark all results from
   a creator as needing review so that if a problematic creator is discovered we
   don't need to manually mark each result for review (or removal, depending on
   the severity of the creator's issues)
1. As an Openverse content moderator, I want to be able to upstream moderation
   decisions to providers when appropriate so that Openverse can be a good
   steward of the commons and also help improve the quality of providers'
   content
1. As an Openverse user, I expect that Openverse will never include material
   already known to be illegal because Openverse is not a place for distribution
   of illegal materials
1. As an Openverse content moderator, I expect that results with sensitive
   textual material will be automatically raised for review so that I can
   quickly identify results that may need moderation action without a user
   needing to file a report or a content moderator searching them out
1. As an Openverse user, I expect that sensitive textual material has a useful
   content warning so that I can make an informed decision about whether I want
   to read a piece of text
1. As an Openverse user, I expect to be able to clearly understand what content
   on the Openverse website is from Openverse and what content is from the
   providers so that I understand whether I need to make upstream reports of
   creators or specific content to providers or to Openverse
1. As a creator, I want to be able to obtain the rationale behind one or many of
   my works being removed from Openverse
1. As a creator, I want to be able to mark my own content with specific content
   warnings so that I can make my content more accessible
1. As a user, I want to be able to mark or suggest content warnings for results
   so that I can help make Openverse catalogued content more accessible

- Assumptions:
  - Upon reingestion from a provider, the catalogue is able to note when results
    have been removed from upstream providers and eagerly remove them from the
    Openverse API without needing a full data refresh to occur
  - Providers that do not fully reingest each time have a way of detecting
    results that have been removed from the upstream
  - There exists a "content moderator" role that has access to the Django Admin
  - There exists a way to mark results for removal (this already exists)
  - A removed result will no longer be accessible at the single result page
  - A removed result will no longer appear in search
  - We know the policies for each content provider
  - For providers that want to work with us, we have a mechanism to upstream
    content reports
  - Openverse scans results for known sensitive/illegal materials and
    automatically excludes them from the catalogue, raises a flag on the
    creator, and enables content moderators to send reports about the illegal
    content to the provider for review
  - A bulk result remove tool exists
  - Openverse has indexable hashes for results that can be searched with a
    "match tolerance" so that results do not have to _exactly_ match, at least
    for images but ideally also for audio
  - Openverse has clear content policies
  - Openverse has a way of detecting sensitive textual material
  - Openverse has a definition of "sensitive textual material"
  - Openverse has a way of hiding sensitive visual and textual material
  - Openverse has a way of attaching generated and manually created content
    warnings for individual results
  - Openverse has a way of detecting sensitive visual material
  - There is a way to see the results for a given search in Django admin and
    those results can have bulk actions taken
  - We can take bulk actions for the results for a particular creator in Django
    admin
  - Creators are "entities" in the Django admin that have their own pages and
    list of actions including bulk removal and export of all removal reasons
  - Users have a way to submit content warnings
  - Openverse does not store the actual material for a result aside from
    thumbnail caches (that is, we do not have internal places where we need to
    purge materials found to be in violation of our content policies)
- Process requirements to meet the assumptions:
  - We need to develop content policies (discuss and potentially adopt the
    content policies of other WordPress Foundation projects like image
    directory)
  - We need to have documentation and technical training material available for
    people who want to be content moderators for Openverse
  - We need to find a group of people willing to do content moderation for
    Openverse
- Technical requirements to meet the assumptions:
  - New Django auth role "content moderator" with access to reports and cache
    management tools
  - Perceptual hash of images; some other kind of hash for audio: when results
    clash with an existing hash they're flagged, if a result clashes with a
    result that has been removed then it is automatically excluded
  - The catalogue is able to know that a result is removed
  - A removed result will eventually be removed from the ES index
  - Updates to the ES index also clear dead link masks for any query hashes that
    included the result
  - Dead link mask is updated to be a general "hidden result mask" with distinct
    reasons for why a result is hidden (because the link is dead, because it was
    automatically removed due to sensitive content, because it was manually
    marked as sensitive, because it violated DMCA, etc)
  - We can relatively painlessly update hidden result masks
  - Hidden link masks reasons have individual TTLs:
    - Sensitive content: never expires
    - Dead link: maintain existing expiry timeouts
  - Results are only ever scanned a single time for sensitive content (unless
    definitions change, either on our end or on any image classification API's
    end); that is, results are not unnecessarily re-scanned
  - We need to find an image classification API that we're comfortable using
    that can detect specific categories of sensitive material
  - We are able to attach multiple content warnings for a result
  - We can remove content warnings for a result if they're manually audited and
    found to be inaccurate (and an audit trail exists for this action so that if
    is not done appropriately we can understand how to improve the process to
    prevent incorrect usage of it)
  - The catalogue is able to extract content warnings from the API whether
    they're automatically generated or user/moderator created
  - The frontend can display blurred images, likely through a thumbnail endpoint
    that is able to blur images so that OpenGraph embeds are also blurred
  - Blurred images include accessible text that note that the image is blurred,
    both as alt text and as a visual indicator on the blurred image itself.
  - The thumbnail endpoint blurs images marked as sensitive by default and a
    query parameter can be passed to retrieve the unblurred image
  - We have a way of programmatically interacting with Cloudflare's cache to
    automatically remove cached pages that include content newly marked as
    sensitive
    - This includes the following API endpoints:
      - Thumbnail (so that if an image is newly marked as sensitive, the default
        thumbnail will be blurred instead of the cached unblurred version)
      - Search results
      - Single results
  - The list of results returned for a query hash is accessible and can be
    easily iterated through in order to remove dead link masks for queries that
    have newly removed results
    - We may also need a reverse index this: result id -> list of reversible
      query hashes. Needed to be able to easily bust cached pages to exclude the
      result.
  - Query hashes should be reversible (as in, we can derive the query parameters
    from the hash or we maintain a mapping of hash -> query paramters) so that
    we can bust caches for a query hash
  - The HTTP cache for relevant searches and single results (currently
    Cloudflare) are automatically updated when a result is removed
  - The frontend is able to submit content warning suggestions for individual
    results
