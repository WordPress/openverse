# 2024-10-28 Project Proposal: Relicensing

**Author**: @dhruvkb

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @krysal
- [x] @obulat

## Project summary

<!-- A brief one or two sentence summary of the project's features -->

This project aims to change the license of the code in the Openverse monorepo to
better align with the
[GPL license used by WordPress](https://wordpress.org/about/license/) itself and
other projects associated with WordPress.

## Goals

<!-- Which yearly goal does this project advance? -->

This project aligns Openverse with the WordPress project. It also updates
Openverse to use a stronger copyleft license from the GNU family of licenses
instead of the MIT license which has fewer protections.

## Requirements

<!-- Detailed descriptions of the features required for the project. Include user stories if you feel they'd be helpful, but focus on describing a specification for how the feature would work with an eye towards edge cases. -->

The project requires a comparison of various licenses to identify the best
possible license for different blocks in the monorepo. The project also requires
an understanding of various licenses and the implications the choice of license
would have on the project itself and on integrations using the Openverse data
via the API.

## Success

<!-- How do we measure the success of the project? How do we know our ideas worked? -->

The project can be considered both shipped and immediately successful after each
individual component of the monorepo has completely moved to the new proposed
licenses.

## Participants and stakeholders

<!-- Who is working on the project and who are the external stakeholders, if any? Consider the lead, implementers, designers, and other stakeholders who have a say in how the project goes. -->

Essentially every contributor who has ever submitted a patch to Openverse will
be a stakeholder in this project.

The project would also affect existing integrations so we will need to notify
the maintainers of these integrations about the change to the license.

## Infrastructure

<!-- What infrastructural considerations need to be made for this project? If there are none, say so explicitly rather than deleting the section. -->

Change to the license would not involve any infrastructure changes.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this project? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

Change to the license would not involve any accessibility changes.

## Marketing

<!-- Are there potential marketing opportunities that we'd need to coordinate with the community to accomplish? If there are none, say so explicitly rather than deleting the section. -->

We should broadcast the change in license because of the following reasons.

- Openverse would now use a GNU license which aligns with WordPress.
- Openverse would be be covered by stronger copyleft protections.

## Required implementation plans

<!-- What are the required implementation plans? Consider if they should be split per level of the stack or per feature. -->

One
[implementation plan](/projects/proposals/relicensing/20241028-implementation_plan_relicensing.md)
is required to arrive at the ideal license and document a process for
conversion.
