# 2024-03-13 Project Proposal

**Author**: @fcoveram

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @obulat
- [x] @zackkrida

## Project summary

<!-- A brief one or two sentence summary of the project's features -->

Include a feature that changes the UI from light to a dark color scheme.

### Motivation

Dark mode is a customization level that is in the spirit of adapting the UI to
user's contexts. The benefits span a11y, personal preferences set on the
devices, energy efficiency in devices, and an alternative browsing experience of
visual content due to the background contrast.

## Goals

<!-- Which yearly goal does this project advance? -->

Refine Search Experience

## Requirements

<!-- Detailed descriptions of the features required for the project. Include user stories if you feel they'd be helpful, but focus on describing a specification for how the feature would work with an eye towards edge cases. -->

1. Add the dark theme to the site and set the Light theme as default. The reason
   comes from not changing the site settings without user consent through an
   action.
2. Introduce the feature to users on the site once deployed.
3. Allow visitors to change the UI in an reachable manner from the whole site
   through three options: Light theme, Dark theme, or follow device setting.
4. Design a dark theme preserving the brand identity.
5. Design a dark theme that meet the color contrast requirements pointed out in
   the accessibility section below.
6. Document the design of pages and UI components in the Design Library and any
   other additional Figma files.
7. Document the dark variant of every UI element on Storybook.
8. Document the transition from current to new frontend implementation.
9. Include an analytic event to record how users utilize the functionality.

## Success

<!-- How do we measure the success of the project? How do we know our ideas worked? -->

- The use of this feature will be recorded and analyzed to assess its success.
- Evaluate the color contrast with an automated tool and a revision from
  contributors.

## Participants and stakeholders

<!-- Who is working on the project and who are the external stakeholders, if any? Consider the lead, implementers, designers, and other stakeholders who have a say in how the project goes. -->

- Lead: @fcoveram
- Design: @fcoveram
- Implementation: @obulat

## Infrastructure

<!-- What infrastructural considerations need to be made for this project? If there are none, say so explicitly rather than deleting the section. -->

This project only concerns frontend user interface code, and swapping colors. It
should not require any changes to our infrastructure.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this project? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

Shifting the UI theme should be actioned through a mix of one or more of the
following current elements:

- VCheckbox
- VRadio
- VItemGroup
- VSelectField
- VPopover
- VButton
- VIconButton

The designs of pages and components need to meet the contrast color requirements
described in WCAG 2.2 to meet AA. See the
[Perceivable section](https://www.w3.org/WAI/WCAG22/quickref/?currentsidebar=%23col_overview&levels=aaa&showtechniques=321#principle1)
of the guideline for more context.

## Marketing

<!-- Are there potential marketing opportunities that we'd need to coordinate with the community to accomplish? If there are none, say so explicitly rather than deleting the section.-->

An announcement showing the functionality will be created in conjunction with
marketing team based on their existing workflows.

## Required implementation plans

<!-- What are the required implementation plans? Consider if they should be split per level of the stack or per feature. -->

Frontend implementation plan.
