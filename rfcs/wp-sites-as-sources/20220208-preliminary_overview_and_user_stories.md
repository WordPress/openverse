# WordPress Sites as Openverse Sources: preliminary overview and exploration

This document seeks to explore a major expansion of the functionality of
Openverse: namely, allowing the direct inclusion of media from sites across the
internet into Openverse. Instead of creators and authors uploading their works
to an existing search engine indexed by Openverse, creators can self-host their
works and express their intent to share them to Openverse programatically.

The first implementation of this protocol would be to create a mechanism for
WordPress sites to use this protocol through their admin panels. Much like
[responsive image syntax](https://make.wordpress.org/core/2015/09/30/responsive-images-merge-proposal/)
was adopted by WordPress and thusly propogated across the web, here we aim to
use WordPress as a first, powerful distribution mechanism for sites to brodcast
their openly-licensed media.

This is a large and multi-layered initiative.

## Prior Art

- [ccREL: The Creative Commons Rights Expression Language](https://www.w3.org/Submission/ccREL/)
  was a proposal submitted to the World Wide Web Consortium (W3C) back in May
  of 2008. It aimed to create a standard syntax for expressing Creative Commons
  structured data in an HTML page, whic would allow users to mark their sites,
  and content on their sites, as CC-licensed. This solution was envisioned at
  the height of the Web 3.0 (not web3) or
  [semantic web](https://en.wikipedia.org/wiki/Semantic_Web) movement, which was
  primarily the idea that web pages would communicate with each other through
  semantic information derived from rich textual medata encoded into the page
  markup itself. While this grand vision for the web, and specific ccRel
  implementation, didn't fully take off, it's still the fundamental principle we
  may use to add open-license metadata to sites for inclusion in Openverse.

## Stories

### User Groups

The following groups were identified:

- [Authors/Creators](#authorscreators)
- [Content Moderators](#content-moderators)
- [Openverse users](#openverse-users)
- [Commons Stewards](#commons-stewards)
- [Openverse contributors](#openverse-contributors)
- [Openverse Maintainers](#openverse-maintainers)

### Authors/Creators

- As a creator, I do not want to accidentally share private photos to a public
  search engine
- As a creator, I want to license some of my not-the-best photos under a CC
  license so that people can find me and license my other better, proprietary
  photos.
- As a creator, I want to upload my images to Openverse so I can avoid having to
  create a custom page/post type for every single image or can avoid having to
  pay for bandwidth/hosting costs for users downloading my works
- As a creator, I want my media in Openverse to link to my custom post type for
  individual works, where I show a download button but also the option to buy
  prints of my images, so I can make sales.
- As a creator, I only want to share images which have appeared on a publicly
  accessible page of my website, to ensure I am not sharing private works
  erroneously.
- As a creator, when sharing my works under a CC license, I want to also make it
  SEO friendly and have all the attribution and descriptions required for
  accessibility.
- As a creator, I do not want my works to be incorrectly licensed under an open
  license because CC licenses are “irrevocable” and my work should not be
  available in Openverse
- As a creator, I want that when I indicate an image should appear in Openverse,
  it should become available quickly if not immediately
- As an author/editor, I want to be able to add media in the editor and mark its
  specific license so that I do not have to manually do it at a different stage
- As an author/creator, I want to be able to retire my uploaded images from
  appearing in Openverse search results to avoid excessive exposure
- As a creator, I want a clear distinction between what media I can add to
  Openverse and what media I should not (e.g. something I downloaded from Google
  images) so that I do not erroneously license something inappropriately
- As a creator, I want to view data about how many times my images have been
  viewed in Openverse
- As an author/creator, I want to be able to add metadata about my media, like a
  title, alt text, tags, etc, to make it easier to find.
- As a creator, I want to be able to proactively mark my images as potentially
  sensitive for content moderation purposes
- As a creator, I want to be able to add specific content warnings to media so
  that the ‘sensitive’ nature of it is qualified and so that my work is as
  accessible as possible
- As a creator, I want to have a list of potential content warning tags or
  templates I can choose from so that I do not have to think of all the possible
  things that might make a specific piece of media ‘sensitive’ to one group or
  another (and all of this so that my work is as accessible as possible)
- As a creator, I would like to specify which media may be mature when adding it
  to Openverse so that it does not show up in the non-mature search
- As a creator, I want to be able to bulk-upload images under a particular
  license via the media library so that I do not have to upload individual
  images and individually select the license
- As an author/creator, I want a place to look at all my images/media available
  in Openverse
- As a creator, I want to be able to bulk modify the licenses of previously
  closed-licensed works to open licenses so that I do not have to manually
  backfill an open license to images
- As a creator I want to be able to license my work under a pseudonym that has
  no relation to my legal name or the name of my site.
- As a creator, I want my images to be removed from Openverse if I delete them
  on the source site.
- As a creator, I want to have a single page for media that can host the highest
  quality version of the media along with a standard description and title so
  that people using my media will know what my ideas about the work I created
  are.
- As a creator, I want to be able to update tags or other metadata and see these
  updates reflected in Openverse in a timely manner.
- As a creator, I want to know what metadata I need to provide about the image
  so that it can appear higher in the result page.
- As a creator, I want all the items that were uploaded to Openverse clearly
  marked so that I can see at a glance what I shared.
- As a creator of copyrighted works, I want to completely and clearly prevent
  anyone from indexing my works and set a ‘Do Not Index’ marker on my site,
- As a creator, I want guidance as to which license to choose so that I can make
  an informed decision.
- As a creator, I want to add the attribution information inside my image file
  (as CCRel) so that it’s easier to track my media.
- As a creator, I want a single form for editing the metadata for my images that
  will also populate the JSON-LD image metadata to my page for search engines,
  and the alt text and caption.
- As a creator, I want to know when my media was uploaded and started showing on
  Openverse.
- As a long-term creator with a lot of existing original work, I want to batch
  apply a license (CC or copyrighted) on all existing content.
- As a creator, I want to know statistics of how my content was doing as to how
  many impressions, clicks and usages it has received and its relevance and
  quality metrics.
- As a creator, I want to automatically show the license (and attribution?) for
  my images when it is inserted onto a post or page
- As an author of text works, I want to license entire posts and pages as CC
  licensed. This is different from uploading media under a license to a page,
  this is about licensing the page itself.
- As a creator, I want to be clearly informed about the irreversibility of CC
  licenses so that I don’t apply it accidentally.
- As a creator, I want to clearly know the conditions of what my content will be
  under, so then I will not be surprised of seeing my content used somewhere
  else.
- As a creator, I want to distinguish which content from my library is currently
  in the commons, so I know what modifications or any other change I can make.
- As a creator, I want to see my creation linked correctly to my source of
  truth, so I can see the value of attribution and provenance of releasing
  content under an open license.
- As a creator, I want to have a combobox with a default value for the ‘creator’
  and ‘creator_url’.

### Content Moderators

- As a content moderator I want to be able to remove all media from a certain
  WordPress site which may be malicious/sensitive/incorrectly licensed so that
  Openverse does not contain this content.
- As a content moderator I want to be able to detect repeat infractions from a
  particular source
- As a moderator, I want to categorize entire sites with sensitive content under
  a particular type of sensitivity so that all media coming from it has that tag
  and I don’t repeatedly have to tag every upload from it.
- As a content moderator I want to be able to inform a WordPress site why their
  content was denied from inclusion in Openverse, so they can avoid/change the
  type of content they are trying to upload.
- As a content moderator, I want to know if an image is already included in
  Openverse, to avoid duplicates

### Openverse users

- As an Openverse user, I want to easily see all the images from uploaded by a
  WordPress site so that I can find content I might enjoy from the
  creator/creators without having to view each post on their WordPress site
- As an Openverse user, I want to filter searches on Openverse by the creator
  and/or their site (which is already somewhat possible) so that I can find
  CC-licensed work from a particular creator that I like.
- As an Openverse user, I want to find images from small independent creators so
  I can avoid using the ‘same old’ stock photography that’s already all over the
  web
- As an Openverse user, I want to be able to land on a single page for a
  WordPress site hosted piece of media so that I have an original place to
  download the work at its highest quality
- As an Openverse user, I do not want to filter images by an endless list of
  hundreds/thousands of individual creators, so that I’m able to also find
  images from high-quality, authoritative sources like museums.
- As an Openverse user, I want to access the WordPress site where the content is
  easily, so I do not need to create an account or figure out how to use the
  content by either downloading it or embedding it in my site.
- As an Openverse user, I want to access an openly-licensed content all the
  time, so the content piece does not disappear when I go back to see it after a
  while.

### Commons Stewards

- As a steward, I want the license field to restrict users from making invalid
  modifications such as changing an image that was once CC licensed (and is
  benefitting from increased exposure) to now from going to a more restricted
  license.
- As a commons steward, I want to ensure sites are using the latest versions of
  open licenses, to keep up to date with changes in technology and best
  practices.
- As a steward, I want to make sure AI-generated works are not incorrectly
  licensed or added to the commons
- As an aggressive steward, I want to nudge/influence users to use CC licensed
  works over copyrighted ones using certain UX/UI dark patterns.
- As a steward of the commons, I want CC licensed works to be perpetually
  available and distributed by some mechanism so that link rot, financial
  instability, etc, do not make the original source unavailable and render the
  work lost to history
- As a steward, I want that WordPress admins clearly know they can not revoke
  the license of a media, so we reduce the chances of copyright or any other
  ownership complaints.
- As a steward, I want to highlight to WordPress admins and creators the
  benefits of open licenses, so we open advocators boost the creation value of
  commons.

### Openverse contributors

- As a contributor, I want to have clear guides of how I can contribute with
  media content to Openverse (WP Photo directory, my own WP site, 3rd party
  source host site, anything else?)

### Openverse Maintainers

- As a maintainer, I want to see ingestion information on new WordPress sites so
  that we can detect anomalies during ingestion
- As a maintainer, I want to detect if the new media is a duplicate of the one
  we already have so that I could flag it as a possible infringement.
- As a maintainer, I want the media to have full metadata that describes the
  data well so that it’s easy to use it in search (relevancy).
- As a maintainer, I want WordPress sites to have a manageable number of DAG
  tasks so that the process can be finished and repeated
- As a maintainer, I want WordPress sites to have a standard presentation of the
  openly licensed works via some mechanism (API, machine-readable data on a
  page) so that our catalogue is able to automatically and maintainable ingest
  works from WordPress sites
- As a maintainer, I want versioned APIs on the sites providing CC licensed
  works so that if we improve the plugin in future versions (to add new licenses
  or support new media types) we can continue to index and read from sites that
  have not been updated.
- As a maintainer, I want to know the statistics of how many users upload their
  media, how many media items they upload, which users share the most popular on
  Openverse to be able to share the success on social media.
