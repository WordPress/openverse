# Implementation Plan: Update Staging Database

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [ ] @stacimc
- [ ] @krysal

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/392)
- [Project Proposal]() _TBD_

## Overview

<!-- A brief one or two sentence overview of the implementation being described. -->

This document describes how we will implement a mechanism for updating the
staging database with the latest data from the production database.

## Outlined Steps

<!-- Describe the implementation step necessary for completion. -->

The final product of this plan will be a DAG (scheduled for `@monthly`) which
will recreate the staging database from the most recent snapshot of the
production API database. This will be accomplished by:

1.

## Dependencies

### Tools & packages

<!-- Describe any tools or packages which this work might be dependent on. If multiple options are available, try to list as many as are reasonable with your own recommendation. -->

### Other projects or work

<!-- Note any projects this plan is dependent on. -->

## Design

<!-- Note any design requirements for this plan. -->

## Parallelizable streams

<!-- What, if any, work within this plan can be parallelized? -->

## Blockers

<!-- What hard blockers exist which might prevent further work on this project? -->

## API version changes

<!-- Explore or mention any changes to the API versioning scheme. -->

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

## Privacy

<!-- How does this approach protect users' privacy? -->

## Localization

<!-- Any translation or regional requirements? Any differing legal requirements based on user location? -->

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->
