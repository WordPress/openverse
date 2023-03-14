# Implementation Plan: Managing A Sensitive Terms List

> **Content Warning**
>
> This document **does not** include sensitive content or direct links to
> sensitive content. It _does_ discuss different sub-categorizations of
> sensitive content at times.
>
> This document should not be considered sensitive but please view at your own
> discretion, regardless.

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [ ] @sarayourfriend
- [ ] @dhruvkb

The Openverse project
[Filter and blur sensitive results by term matching #377](https://github.com/orgs/WordPress/projects/70?query=is%3Aopen+sort%3Aupdated-desc&pane=issue&itemId=19530115)
requires that we compare the textual contents of Openverse media against a
denylist of sensitive terms. We use this list to identify media that should be
marked as "sensitive," which means they should not be displayed to users by
default, but only with their explicit consent. Importantly, this list is not
used to censor or deny access to specific works, but to enable opt-in access.

The list must be accessible to contributors who need to modify it, but not so
public that it could be seen by users who would rather not be exposed to it. We
recognize that the list itself is sensitive content, and it needs to be treated
with care.

To create and manage this list I reccommend the following guidelines.

## Outline of the approach

The Openverse team will maintain a standalone public repository which contains
an English-language list of sensitive terms. This term list is a living document
which accepts community revisions for adding and removing new terms. The
contents of the list will initially be based on an existing public list,
modified at the discretion of Openverse maintainers interested in contributing.
The list will be iterated on and refined as we develop community standards
around what constitutes "sensitive content" for Openverse users.

### Anticipated questions

1.  Why is the list in a standalone repository, instead of the
    https://github.com/wordPress/openverse?

    The main reason to keep the list seperate is contributor safety. The list is
    kept independently from the codebase so that users must explicitly consent
    to viewing and downloading it. Additionally, there are Search Engine
    Optimization and blocklist considerations with public GitHub repositories.

    We do not, for example, want students to be unable to access our repository
    and contribute to it because it is blocked by a school administration's web
    filter.

2.  Why is the list only in English?

    At the time of writing Openverse doesn't do any translation of the textual
    contents of indexed media. We also do not translate user-submitted searches.
    The vast majority of indexed works are in English. Additionally, it would be
    difficult to validate suggestions for terms in languages not spoken by
    Openverse maintainers, which to my current knowledge includes English,
    Spanish, Brazilian Portugese, Turkish, and Russian. English is the only
    language used by all maintainers.

3.  On what basis will Openverse maintainers use their "discretion" to create
    this list?

    Until our community has developed its own standards around sensitivity, we
    can use a few existing documents in the WordPress and user-submitted content
    ecosystem to guide us:

    - WordPress's page on [etiquette](https://wordpress.org/about/etiquette/) in
      the project.
    - WordPress's
      [code of conduct](https://make.wordpress.org/community/handbook/wordcamp-organizer/planning-details/code-of-conduct/)
      for in-person events.
    - YouTube's
      [community guidelines](https://www.youtube.com/howyoutubeworks/policies/community-guidelines/)
      offers a decent list of categories for unacceptable types of content. For
      example, their
      [thumbnail policy](https://support.google.com/youtube/answer/9229980?hl=en&ref_topic=9282679#zippy=%2Cage-restricted-thumbnails-and-thumbnail-removal)
      includes some information on types of sexual and violent content that
      either can't be used or can be used behind a flag comparable to ours.
      - Additionally, see the [#this-will-not-be-perfect](#this-wont-be-perfect)
        section for additional

## Implementation Plan

1. Ping a WordPress GitHub account maintainer to request that they create the
   `WordPress/openverse-sensitive-terms` repository.
2. Initialize the repository with a `README.md` and a blank
   `sensitive-terms.txt` file.
3. Create a PR which initializes the sensitive terms list by copying all terms
   in the "List of Dirty, Naughty, Obscene, and Otherwise Bad Words" repository.
   _I am not including the link here to prevent accidental viewing of the
   repository, but feel free to find it within the GitHub organization
   "LDNOOBW"._
4. Identify willing reviewers from the `@WordPress/openverse-maintainers` group
   who are comfortable with looking at the list and reviewing the PR, looking
   for terms which should be removed or missing terms which should be added.
5. Merge the PR, and now the list is available for use in Openverse projects.
6. Publish a "Make" post about the creation of the list and its purpose.

## This Will Not Be Perfect

By default, we accept that this list and its usage will not be perfect. At times
we may accidentally include terms which inadvertently cause harm to groups or
individuals. We may also accidentally expose users to undesired content in the
implementation of this list. Despite the potential for these transgressions this
work will always be based on the following assumptions:

1. Safety first. Given the choice, we would prefer to incorrectly restrict
   non-sensitive content rather than accidentally show sensitive content.
2. Avoid censorship. This list will not be used to block or deny access to
   content, rather to make the viewing of content opt-in. The Openverse project
   will use other means to explicitly block or remove content. Removing
   sensitive content can, in many cases, be its own form of harm. A quote From
   the research paper "On the Dangers of Stochastic Parrots: Can Language Models
   Be Too Big? 🦜"[1] illustrates this well:

   “If we filter out the discourse of marginalized populations, we fail to
   provide training data that reclaims slurs and otherwise describes
   marginalized identities in a positive light”

3. Encourage feedback. We will request and monitor community feedback on the
   terms in this list (without inadvertently exposing anyone to the list) to
   make sure it meets the expectations of our users.

## Open questions for reviewers

- Within the Openverse maintainers; who has to view this list? Can anyone opt
  out?
- With what frequency and urgency will community suggestions for the list be
  reviewed, and by whom?

## Appendix A: Guidelines for using the list in Openverse projects

1. Never use terms from the list in Openverse repositories (issues, discussions,
   or code itself), chats, or communications of any time, outside of the
   sensitive terms repository.
2. Do not link directly to the list file itself; always reference the
   repository. The README will provide important context towards consenting to
   viewing the list.
3. Always use the most up-to-date version of the sensitive terms list when
   filtering and marking media as sensitive in Openverse projects.

## Credits

Many of the term lists I evaluated in considering this work came from a
[Wired article](https://www.wired.com/story/ai-list-dirty-naughty-obscene-bad-words/)
entitled "AI and the List of Dirty, Naughty, Obscene, and Otherwise Bad Words".
That article discusses the limits of this kind of text matching in-depth and is
an excellent read for anyone working on content safety in Openverse.

[^1]: https://dl.acm.org/doi/10.1145/3442188.3445922
