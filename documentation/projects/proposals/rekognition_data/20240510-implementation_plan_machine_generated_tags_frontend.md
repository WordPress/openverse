# 2024-05-08 Implementation Plan: Machine-generated tags in the frontend

**Author**: @obulat

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @zackkrida
- [x] @AetherUnbound

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/431)
- [Project Proposal](/projects/proposals/rekognition_data/20240320-project_proposal_rekognition_data.md)

## Overview

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

This implementation plan will describe how we plan to display the
machine-generated tags separately from the source tags on the single result
page. All tags will be clickable and lead to a collection view by the selected
tag. The tag collection view will not be affected as we will not show different
results for a machine-generated tag than the source tag.

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

When this work is completed, the single result page will display
machine-generated tags separately from the source tags. For machine-generated
tags, we will also display the tag provider and its accuracy.

## Step-by-step plan

<!--
List the ordered steps of the plan in the form of imperative-tone issue titles.

The goal of this section is to give a high-level view of the order of implementation any relationships like
blockages or other dependencies that exist between steps of the plan. Link each step to the step description
in the following section.

If special deployments are required between steps, explicitly note them here. Additionally, highlight key
milestones like when a feature flag could be made available in a particular environment.
-->

1. [Create a wrapper component that displays the tags in two sections: source-provided and machine generated](#create-a-wrapper-vmediatags-component)
2. [Add a page that describes the machine-generated and source tags.](#add-about-tags-description-page)

## Step details

<!--
Describe all of the implementation steps listed in the "step-by-step plan" in detail.

For each step description, ensure the heading includes an obvious reference to the step as described in the
"step-by-step plan" section above.
-->

### Create a wrapper `VMediaTags` component

This component will handle filtering the tags into two sets: machine-generated
and source-provided. It will also display the headings and the link to the
"About tags" page. A new child component, `VCollapsibleTagSection`, will handle
displaying of the tags in several rows, collapsing them if there are more than
three rows of tags.

Currently, we deduplicate all tags to only display unique tags. When we display
the tags by generation type, there will probably be duplicates between the
source and the generated tags. However, each section individually will still be
normalized to prevent duplicates.

The generated tags section will have a link to the "About tags" page.

There is no need to create a separate component for machine-generated tags, the
slot in the `VTag` component will enable us to display the additional accuracy
information.

### Add "About tags" description page

We should add a page to explain the users the difference between where the
Openverse tags come from, the difference between the source and generated tags,
and a short description of the machine-generated tag providers. This page should
be linked from the Generated tags section. This page will not be added to the
header navigation.

## Dependencies

This project needs the API to add the `unstable__provider` property to tags in
media responses, which was implemented in
[Expose provider in the API tags response #4280](https://github.com/WordPress/openverse/pull/4280)

### Feature flags

<!-- List feature flags/environment variables that will be utilised in the development of this plan. -->

The project will contain at most 2 PRs that can be reverted, so the feature
flags are not necessary.

### Infrastructure

<!-- Describe any infrastructure that will need to be provisioned or modified. In particular, identify associated potential cost changes. -->

No infrastructure changes will be necessary, we will only update the single
result pages of the Nuxt frontend.

## Alternatives

<!-- Describe any alternatives considered and why they were not chosen or recommended. -->

This project states that it is important to clearly distinguish the
source-generated tags from the machine-generated tags.

In addition to tag name, the machine-generated tags provide additional data
points: their provider (currently, it will be "clarifai" and "rekognition") and
their accuracy. This project aims to describe this data in a technical way on
the "About tags" page, without displaying each individual tag's additional data,
to prevent from overloading the users with too much information. Once we have
more user data on how users relate to machine-generated tags, we will reconsider
displaying this data on the single result page.

Two other options were considered for displaying the machine-generated tags, but
were discarded as they would be less user-friendly.

1. Display the tag's provider and accuracy in a tooltip. This option would
   provide the user all the information about the tag without cluttering the UI.
   However, this option is not good for accessibility. Different browsers and
   screen readers treat the tooltips differently.
2. Display one section per each machine-generated tag provider, and label
   sections with relevant heading, e.g. "Machine-Generated Tags: Rekognition".
   Each provider section would sort the tags in the order of their accuracy, and
   each tag would display the tag name and the tag accuracy. This way, the user
   would see the data without additional actions such as hovering. We have
   enough room on the page to display this data in full. As a bonus, if a tag is
   generated by multiple providers, the users would be able to see that
   different providers generate the same tag, and the difference in accuracy
   between the providers. This option wasn't selected because we don't yet have
   enough user data to know if the users would find this information useful
   instead of overwhelming.

## Design

<!-- Note any design requirements for this plan. -->

The first iteration of the designs that use the first alternative option is
ready:
[Displaying machine-generated content](https://github.com/WordPress/openverse/issues/4192)
If we decide to go with the third alternative option, we will need to add the
provider headings and the accuracy to the tags.

## Blockers

<!-- What hard blockers exist that prevent further work on this project? -->

Since we already have machine-generated tags available in the API, there are no
blockers for this work.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

Adding the "Source tags" and "Generated tags" headings is good for the
accessibility of the tag list. Both the sighted and the screen reader users will
understand what the list is for. It is always desirable to have visible label
next to a list of elements.

The display of generated tags' provider and accuracy is, on the other hand, a
challenging problem from accessibility standpoint. Tooltips proposed in the
second alternative option are often described as inaccessible for mobile users
who do not have a hover action. MDN's section on tooltip best practices suggests
providing "clear labels and sufficient body text" instead of tooltips that hide
important information.

If we decide to display the accuracy on the tag together with its name (option 2
above), it is important to separate the tag name and its accuracy (with an
invisible, `sr-only`, dot, for instance) to make the screen readers add a pause
between them.

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

We can roll back this solution by reverting the PRs implementing this.

## Localization

<!-- Any translation or regional requirements? Any differing legal requirements based on user location? -->

The tag headings will be translated as usual. For the "About page" it is
important to split the text into shorter chunks to make them easier to handle
for translators. The eslint rule will make sure that this is done properly.
