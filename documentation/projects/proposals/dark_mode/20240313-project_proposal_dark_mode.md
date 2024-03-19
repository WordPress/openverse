# 2024-03-13 Project Proposal

**Author**: @fcoveram

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [ ] @obulat
- [ ] @zackkrida

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

1. Add the dark theme to the site and set the Light theme as default.
2. Allow visitors to change the UI in an reachable manner from the whole site
   through three options: Light theme, Dark theme, or follow device setting.
3. Design a dark theme preserving the brand identity.
4. Design a dark theme that meet the color contrast requirements pointed out in
   the accessibility section below.
5. Document the design of pages and UI components in the Design Library and any
   other additional Figma files.
6. Document the dark variant of every UI element on Storybook.
7. Document the transition from current to new frontend implementation.

## Success

<!-- How do we measure the success of the project? How do we know our ideas worked? -->

## Participants and stakeholders

<!-- Who is working on the project and who are the external stakeholders, if any? Consider the lead, implementers, designers, and other stakeholders who have a say in how the project goes. -->

- Lead: @fcoveram
- Design: @fcoveram
- Implementation: TBD

## Infrastructure

<!-- What infrastructural considerations need to be made for this project? If there are none, say so explicitly rather than deleting the section. -->

This project only concerns frontend user interface code, and swapping colors. It
should not require any changes to our infrastructure.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this project? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

- Follow the advisor of WCAG 2.2 to meet AA. Put special attention to the
  [Perceivable section](https://www.w3.org/WAI/WCAG22/quickref/?currentsidebar=%23col_overview&levels=aaa&showtechniques=321#principle1).

## Marketing

<!-- Are there potential marketing opportunities that we'd need to coordinate with the community to accomplish? If there are none, say so explicitly rather than deleting the section. -->

Since the project involves visual changes across the site, there is a marketing
opportunity to introduce the benefits of the UI’s dark theme.

## Required implementation plans

<!-- What are the required implementation plans? Consider if they should be split per level of the stack or per feature. -->

Frontend implementation plan.
