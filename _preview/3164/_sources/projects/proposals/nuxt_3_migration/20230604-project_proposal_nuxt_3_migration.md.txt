# 2023-06-02 Project Proposal

**Author**: @olgabulat

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @zackkrida - for previous experience of migrating the project to Nuxt
- [x] @sarayourfriend - for extensive experience on the frontend

## Project summary

<!-- A brief one or two sentence summary of the project's features -->

Openverse should migrate from Nuxt 2, which is about to reach end-of-life, to
Nuxt 3.

## Goals

<!-- Which yearly goal does this project advance? -->

Developer experience

## Requirements

<!-- Detailed descriptions of the features required for the project. Include user stories if you feel they'd be helpful, but focus on describing a specification for how the feature would work with an eye towards edge cases. -->

- Openverse should run on Nuxt 3.
- All the current functionality should work as expected.
- All the dependencies should be either updated to latest versions that support
  Nuxt 3 or replaced with the ones that support Nuxt 3.

- Nuxt app should migrate from node version 16 to the active LTS version 18 (or
  the current version 20, which will become active LTS on 2023-10-24).
- (Optional) Nuxt app should migrate to pnpm version 8

## Success

<!-- How do we measure the success of the project? How do we know our ideas worked? -->

Openverse uses Nuxt 3, the end-users see no regressions, and the developer
experience is improved due to faster build times.

## Participants and stakeholders

<!-- Who is working on the project and who are the external stakeholders, if any? Consider the lead, implementers, designers, and other stakeholders who have a say in how the project goes. -->

Lead: @obulat Implementation: @obulat, TBD Stakeholders: Openverse team

## Infrastructure

<!-- What infrastructural considerations need to be made for this project? If there are none, say so explicitly rather than deleting the section. -->

There should be no infrastructure changes.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this project? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

Updating to Nuxt 3 could improve the accessibility for slow internet/low-spec
devices by improving the app performance. There should be no changes in terms of
accessibility for screen-reader and keyboard users.

## Marketing

<!-- Are there potential marketing opportunities that we'd need to coordinate with the community to accomplish? If there are none, say so explicitly rather than deleting the section. -->

We could share a post on Make WordPress about the Nuxt 3 migration.

## Required implementation plans

<!-- What are the required implementation plans? Consider if they should be split per level of the stack or per feature. -->

Frontend implementation plan.
