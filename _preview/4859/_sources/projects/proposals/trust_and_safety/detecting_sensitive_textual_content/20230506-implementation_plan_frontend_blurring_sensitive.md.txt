# 2023-05-06 Implementation Plan: Fetching, blurring sensitive results

**Author**: @dhruvkb

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @sarayourfriend
- [x] @zackkrida

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/377)
- [Project Proposal](/projects/proposals/trust_and_safety/detecting_sensitive_textual_content/20230309-project_proposal_detecting_sensitive_textual_content.md)
- [API IP](/projects/proposals/trust_and_safety/detecting_sensitive_textual_content/20230330-implementation_plan_filtering_and_designating_results_with_sensitive_textual_content.md)

## Scope

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

This plan describes the approach, particularly pertaining to the frontend, for
blurring sensitive content.

The content safety project has an API side, that is covered in the
[project proposal](/projects/proposals/trust_and_safety/detecting_sensitive_textual_content/20230309-project_proposal_detecting_sensitive_textual_content.md#api)
and
[implementation plan](/projects/proposals/trust_and_safety/detecting_sensitive_textual_content/20230330-implementation_plan_filtering_and_designating_results_with_sensitive_textual_content.md),
and therefore, out of the scope for this IP. For now, we document what the
frontend needs and assume that these needs will be met by the API.

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

The frontend should not show the user any sensitive material unless the user has
explicitly consented to be exposed to it. Exposure to sensitive material will be
opt-in, meaning that it will be concealed by default.

## Outlined Steps

<!-- Describe the implementation step necessary for completion. -->

### Step 1: Frontend components/features

The implementation would require the following frontend components to be
developed.

- Sidebar component

  - Two toggle switches
    - Fetch sensitive content
    - Blur sensitive content

- Blurrable search result components

  - image cell
  - audio (box and row layouts)

- Single result page

  - Content safety wall
  - Hide content button

- Additional pages

  - Sensitivity documentation page

#### Blur mechanism

For the purposes of faster development, we will go with a CSS blur based
approach for this implementation plan. It has the distinct advantage over all
other approaches of being super generalised meaning that it will satisfy the
blurring needs of images (blurring the image), audio (blurring the title) and
even future media types like 3D models (blurring the JS-based preview).

### Step 2: Feature flag system enhancements

The feature flag + preferences mechanism will need some new features to support
some of the new use cases proposed for this feature.

- Ability to store and retrieve preferences from `sessionStorage` instead of
  `localStorage`.
- Option to not support `ff_` query parameters for a particular flag.

These features are needed to support the new feature flag
[`fetch_sensitive`](#fetch_sensitive).

### Step 3: New feature flags

```{caution}
Observe the difference between on/off and enabled/disabled. The former refers to
the position/value of the toggle, while the latter refers to whether the toggle
can be interacted with and flipped.
```

Two feature flags need to be developed for this feature. One related feature
flag, `fake_sensitive`, already exists.

#### `fetch_sensitive`

This is not technically a feature flag, but rather a preference, which is
internally the same API. As a preference, it will always be set to 'switchable'
in all environments, defaulting to 'off', and will be controlled by the user via
the switches in the search results sidebar.

This flag will not support the use of `ff_` query parameters, to prevent
URL-based malicious action.

#### `sensitive_content`

This is the main, real feature flag that enables the entire feature of being
able to get (or avoid) mature content and then see or blur it. This flag will
determine whether the two switches even appear in the sidebar.

It will be set to 'enabled' in development, 'switchable' in staging and
'disabled' in production till launch, post which it will be 'enabled'
everywhere.

#### What about the blur toggle?

The second toggle in the mockups that determines whether to blur the sensitive
results (let's refer to as `blur_sensitive`) is an ephemeral toggle that is
off + disabled when `fetch_sensitive` is off and enabled only when
`fetch_sensitive` is on.

It will be stored in Pinia so that it can be accessed by the components of
search result cells and blur button in single result view. The UI store would be
a good place to store the value of this toggle. However, unlike other values in
the UI store, it would not be persisted to a cookie and instead would be reset
on a hard refresh.

Note that the hide button that appears on an unblurred single result page is
gone if the user has completely disabled blurring from the search sidebar.

### Step 3: Updating search store

In this step we will update the search mechanism to add support for the
`include_sensitive_results` parameter, which supersedes the existing `mature`
parameter. The list of search results will include mature content if this is set
to `true`.

Since the API will also send the `sensitivity` field, the types for media items
will need to be updated to account for that. This field will compute two values:

- a boolean for whether the media is sensitive and needs to be blurred
- the message to show to the user to help them know why a media is blurred (to
  help them decide whether to unblur it)

### Step 4: Blurring in search results

The approaches to concealment of sensitive content in the search result page is
specific to the media type. For image results, the image itself is blurred; for
audio results, the title is blurred.

The cell components for search results, i.e. image cell and two layouts (box and
row) of the audio track will be updated to automatically blur the right parts of
the UI, based on the store state of the
[`blur_sensitive` toggle](#what-about-the-blur-toggle) and the `is_sensitive`
value for their respective media item.

We are currently going with the CSS blur approach.

### Step 5: Blurring in single result pages

The single result page will be updated to render a safety wall when the media
item is sensitive. The safety wall will be a full page overlay that will conceal
the entire content of the page.

It will have a button that will allow the user to proceed to see the content or
to go to a default page.

There is a difference in the behaviour of this page based on whether the user
has arrived to it from a search result page or directly. In the former case, the
preference for the [`blur_sensitive` toggle](#what-about-the-blur-toggle) will
be carried over to the single result page (as they will be in the same session),
and if the user has opted to see sensitive content unblurred, the wall will not
be shown to them.

Care must be taken to not show the content at all unless we have the information
about the sensitivity of the media item. A flash of clearly visible sensitive
content before the wall appears will be jarring and will defeat the purpose of
the wall.

### Step 6: Sensitivity documentation

Based on the contents of the `sensitivity` array, the single result page
content-safety wall shows a message to the user to explain why the result is
hidden and to help them decide whether to proceed or not.

This message contains terms like "sensitive" (from the source), and "sensitive
textual content" whose meaning may not be immediately clear. They should link to
a page explaining our process and that it's currently imperfect and that we are
actively working on improving it.

## Design

<!-- Note any design requirements for this plan. -->

The necessary designs for this plan were proposed and extensively iterated in
[WordPress/openverse#791](https://github.com/WordPress/openverse/issues/791).

The finalised designs can be found in Figma document for
[Safe content browsing flow mockups](https://www.figma.com/file/bDTfGzBit8rGRPktOR1cu4/Safe-content-browsing-flow?type=design&node-id=0-1).

As of writing the document, the design work has been completed.

## Parallelizable streams

<!-- What, if any, work within this plan can be parallelized? -->

The development of the required components can be parallelized. The last step,
which will be bringing all the code together (to put the sensitive content
behind the wall when the user has not opted, or opted out, of seeing sensitive
material) is the one that will be blocked till all the pieces have come
together.

## Blockers

<!-- What hard blockers exist which might prevent further work on this project? -->

There is no blocker for development, we can use the unstable form of the
`include_sensitive_results` parameter for development and there is already a
[PR for the API changes](https://github.com/WordPress/openverse/pull/2057).

We would ideally want the parameter to be stable before promoting the feature to
GA in production, but since we manage both the API and the frontend, we can
coordinate any breaking changes.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

While blurring is purely a visual effect, we are taking it in a more general
sense here that takes into account needs of users who will be using visual aids
like screen-readers. Content-masking would be a more appropriate term for this
and the frontend copy should reflect that.

While content is blurred visually, it will also not be read to the
screen-readers. In it's place a placeholder text like "Sensitive image" or
"Sensitive audio" can be used.

Other than the above mentioned, I do not foresee any accessibility concerns
because all other components have clear, well-defined interactions using
standard HTML components.

## Analytics

The proposal suggests
[4 analytics events](/projects/proposals/trust_and_safety/detecting_sensitive_textual_content/20230309-project_proposal_detecting_sensitive_textual_content.md#frontend-1)
to help us understand the impact and utility of these safety features.

The first two are sent by the respective toggle buttons in the search sidebar.
Statistics from them will give us an insight into the users preferences for
accessing and viewing (respectively) sensitive content.

The other two are sent from the single result page, which gives us an idea of
how suggestive/informative the blurred images are when the user has not opted to
see sensitive content from the search results. They will not appear unless the
user has blurred images in search results and then chosen to visit a sensitive
image. The latter two will also give us insight about shared links which lead to
sensitive content.

| Event                      | Component                               |
| -------------------------- | --------------------------------------- |
| `TOGGLE_SENSITIVE_RESULTS` | `fetch_sensitive` toggle                |
| `TOGGLE_DO_NOT_BLUR`       | `blur_sensitive` toggle                 |
| `UNBLUR_SENSITIVE_RESULT`  | Content safety wall, unblur button      |
| `REBLUR_SENSITIVE_RESULT`  | Single result page, hide content button |

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

Since the work will be behind a feature flag, rollback can be achieved by
disabling the feature.

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->

The project proposal from @sarayourfriend is very comprehensive and already
covers a lot of potential pitfalls.
