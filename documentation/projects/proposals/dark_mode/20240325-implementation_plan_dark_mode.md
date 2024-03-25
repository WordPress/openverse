# 2024-03-25 Implementation Plan: Dark Mode

**Author**: @zackkrida

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [ ] @obulat
- [ ] @sarayourfriend

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/3592)
- [Project Proposal](./20240313-project_proposal_dark_mode.md)

## Overview

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

This implementation plan focuses on the three key aspects of the dark mode
implementation:

- Color management in Tailwind and Vue frontend components
- Toggling dark mode (new UI and dark mode detection logic)
- Supporting code for visual regression tests and feature flagging

### Philosophy

The way @fcoveram has designed the color system for dark mode is crucial to
understanding the implementation here. This project uses a "palette swap" where
each color has a 1:1 replacement from light mode to dark mode. While we _will_
include easy mechanisms for exceptions to this rule, they do not appear to be
necessary based on the designs. Implementing our dark mode, then, should allow
component authors to write the component once, using semantic color names, that
will automatically switch between their light and dark mode counterparts.

### Implementation

We will switch our color names defined in the tailwind configuration to use
semantic names, for example replacing "pink" with "primary" and "yellow" with
"complement". Instead of hardcoding these colors in the tailwind configuration,
the tailwind configuration will refer to CSS variables defined in our root css
file. The value of the CSS variables will be switched based on a dark mode CSS
class added to the HTML root when dark mode is enabled.

Tailwind's built in `dark:` modifier can be used for any styles which need to
override the default behavior or add dark-mode specific styles beyond the core
palette swap.

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

- Users writing components will have a "dark mode compatible by default"
  experience. By default, they will not need to think much about dark mode.
- Color names in the codebase will be replaced with semantic names.
- Frontend developers will have easy tools to visually test components in light
  and dark mode.

## Rejected alternate approaches

- Using the `dark:` modifier _exclusively_ for dark mode styling. This is more
  explicit, but much, much more verbose, and would require extensive edits to
  every single component we have written. Instead of writing `bg-background`,
  for example, we would have to write `bg-white dark:bg-black` all throughout
  the codebase.

## Step-by-step plan

<!--
List the ordered steps of the plan in the form of imperative-tone issue titles.

The goal of this section is to give a high-level view of the order of implementation any relationships like
blockages or other dependencies that exist between steps of the plan. Link each step to the step description
in the following section.

If special deployments are required between steps, explicitly note them here. Additionally, highlight key
milestones like when a feature flag could be made available in a particular environment.
-->

The following plan requires approved designs and semantic color names.

1. Parallel Work Stream "A": Implement the new color palette
   1. Create a `FORCE_DARK_MODE` feature flag which is disabled by default and
      available in every environment. Add logic to add a `dark-mode` class to
      the root HTML tag when this flag is enabled and a `light-mode` class when
      disabled.
   2. Rename all colors in the tailwind config and the frontend components to
      use new, semantic names.
   3. Replace "hardcoded" color values in the tailwind configuration file with
      css variables defined in the "base" layer of the `tailwind.css` file.
   4. Add the dark mode colors in the form of additional css variable
      definitions, nested under the `.dark-mode` css class, in the "base" layer
      of the `tailwind.css` file. **At this point, the full dark mode appearance
      should be able to be tested manually by @fcoveram and
      @wordpress/openverse-frontend for any inconsistiencies or problems**.
2. Parallel Work Stream "B": Toggling dark mode

   1. Create a `SHOW_DARK_MODE_TOGGLE` feature flag which is disabled by default
      and available in every environment.
   2. Implement logic for calculating a current "color mode" with the following
      state:

      ```ts
      interface ColorMode {
        preference: "dark" | "light" | "system" // Defaults to "light"
        systemValue: "light" | "dark" // Readonly representation of the system value
      }
      ```

      The color mode should be stored in a cookie so that a previous user choice
      can be used when rendering via SSR and avoiding a flash of light mode
      styles for dark mode users.

      _TODO: I need to decide if we should just use v2 of the official "nuxt
      color mode" plugin, which seems pretty drop-in and straightforward, or
      write a custom implementation_.

   3. Behind the feature flag, Add the new user interface element which toggles
      dark mode. Default to "light" mode but support choosing between "dark",
      "light", and "system".

## Step details

<!--
Describe all of the implementation steps listed in the "step-by-step plan" in detail.

For each step description, ensure the heading includes an obvious reference to the step as described in the
"step-by-step plan" section above.
-->

## Dependencies

### Feature flags

<!-- List feature flags/environment variables that will be utilised in the development of this plan. -->

### Infrastructure

<!-- Describe any infrastructure that will need to be provisioned or modified. In particular, identify associated potential cost changes. -->

This will not require any infrastructure changes.

### Tools & packages

<!-- Describe any tools or packages which this work might be dependent on. If multiple options are available, try to list as many as are reasonable with your own recommendation. -->

### Other projects or work

<!-- Note any projects this plan is dependent on. -->

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

This can be easily be rolled back in a critical scenario by hiding the UI
control for dark mode and hardcoding the "color mode" to `light` for all users.

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->
