# 2024-03-25 Implementation Plan: Dark Mode

**Author**: @zackkrida

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @obulat
- [x] @sarayourfriend

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/3592)
- [Project Proposal](./20240313-project_proposal_dark_mode.md)

## Overview

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

This dark mode implementation plan is comprised of three work streams:

- Color management in Tailwind and Vue frontend components
- Toggling dark mode (new UI and dark mode detection logic)
- Visual regression tests and feature flagging

Most of these work streams can happen in parallel which I will elaborate on in
the ["Implementation"](#implementation) section.

### Design Philosophy

Understanding the way @fcoveram has designed the color system for dark mode is
crucial to understanding this implementation. Quite simply and elegantly, the
designs use a "palette swap" approach in which each color has a 1:1 replacement
from light mode to dark mode.

![Openverse.org dark mode color palette](/_static/dark_mode_palette_example.png)

While we _will_ include easy mechanisms for exceptions to this rule, they do not
appear to be necessary based on the designs. Implementing our dark mode, then,
should allow component authors to write components _once_, using semantic color
names, that will automatically switch between their light and dark mode
counterparts.

### Implementation

We will switch our color names defined in the tailwind configuration to use
semantic names, for example replacing "pink" with "primary" and "yellow" with
"complementary". Instead of hardcoding these colors in the Tailwind
configuration, the tailwind configuration will _reference_ CSS variables defined
in our root css file. The value of the CSS variables will be switched based on a
dark mode CSS class added to the HTML root when dark mode is enabled and the
`prefers-color-scheme` media query.

Tailwind's built in `dark:` modifier can be used for any styles which need to
override the default behavior or add dark-mode specific styles beyond the core
palette swap. We will inform tailwind of our dark mode setup using the Tailwind
configuration's [`darkMode` property](https://tailwindcss.com/docs/dark-mode).

Here are simplified examples of this setup. All the logic is correct and
suitable for production but the actual variables are illustrative only.

In our primary CSS file, we define CSS variables and redefine them to use our
dark mode values in two scenarios:

1. When the `.dark-mode` class is present
2. when the user's preferred color scheme is dark, and the `.light-mode` class
   is _not_ present.

```css
:root,
:is(.light-mode *) {
  --color-primary: black;
  --color-secondary: white;
}

:is(.dark-mode *) {
  --color-primary: white;
  --color-secondary: black;
}

@media (prefers-color-scheme: dark) {
  :not(.light-mode *) {
    --color-primary: white;
    --color-secondary: black;
  }
}
```

In our Tailwind configuration, we reference these variables like so:

```js
const config = {
  theme: {
    colors: {
      primary: "var(--color-primary)",
      secondary: "var(--color-secondary)",
    },
  },
}
```

In a component, we use one Tailwind class to implement the correct color in
light and dark modes:

```html
<template>
  <!-- This will be black in light mode and white in dark mode -->
  <p class="text-primary">Hello World</p>
</template>
```

Finally, if we ever need an "escape hatch" to make sure, a component is, for
example, _always_ black _regardless_ of dark mode:

```html
<template>
  <!-- This will be black in light mode and black in dark mode -->
  <p class="text-primary dark:text-secondary">Hello World</p>
</template>
```

The escape hatch requires the following Tailwind configuration:

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: [
    "variant",
    [
      "@media (prefers-color-scheme: dark) { &:not(.light-mode *) }",
      "&:is(.dark-mode *)", // :is is so the specificity matches and there's not unexpected behavior
    ],
  ],
  // ...
}
```

You can learn more about this configuration in the
[Tailwind docs](https://tailwindcss.com/docs/dark-mode#using-multiple-selectors).

### Rejected alternative approach

Using the `dark:` modifier _exclusively_ for dark mode styling. This is more
explicit, but much, much more verbose, and would require extensive edits to
every single component we have written. Instead of writing `bg-background`, for
example, we would have to write `bg-white dark:bg-black` all throughout the
codebase.

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

- Users can switch between available color schemes in Openverse.
- Openverse displays the correct color scheme for the user:
  - Render Dark mode for:
    - Users with no theme selected from our UI and `prefers-color-scheme: dark`
    - Users who previously selected "Dark" in our UI and
      `prefers-color-scheme: dark`
    - Users who previously selected "Dark" in our UI and
      `prefers-color-scheme: light`
  - Render Light mode for:
    - Users with no theme selected from our UI and `prefers-color-scheme: light`
    - Users who previously selected "Light in our UI" and
      `prefers-color-scheme: light`
    - Users who previously selected "Light in our UI" and
      `prefers-color-scheme: dark`
- Opvenverse does not display a
  ["Flash of inAccurate Color Scheme (FART)"](https://css-tricks.com/flash-of-inaccurate-color-theme-fart/)

Secondarily, there are additional devex outcomes worth mentioning:

- Users writing components will have a "dark mode compatible by default"
  experience. By default, they will not need to think much about dark mode.
- Color names in the codebase will be replaced with semantic names.
- Frontend developers will have easy tools to visually test components in light
  and dark mode.

## Step-by-step implementation plan

<!--
List the ordered steps of the plan in the form of imperative-tone issue titles.

The goal of this section is to give a high-level view of the order of implementation any relationships like
blockages or other dependencies that exist between steps of the plan. Link each step to the step description
in the following section.

If special deployments are required between steps, explicitly note them here. Additionally, highlight key
milestones like when a feature flag could be made available in a particular environment.
-->

The following plan requires approved designs and semantic color names. Each task
is a discrete issue and pull request. The top-level "Work Streams" can be
completed in parallel.

1. **Work Stream A**: Implement the new color palette.

   1. Create a `FORCE_DARK_MODE` feature flag which is "off" by default and
      "switchable" in our staging environment. Add a `dark-mode` class to the
      root HTML tag when this flag is enabled, and a `light-mode` class which is
      set by default. This will not result in any visual changes.
   2. The following steps can take place in parallel:

      1. Rename all colors in the Tailwind configuration and the frontend
         components to use new, semantic names (specific names TBD). This will
         not result in any visual changes. **This is likely to be the largest PR
         to review as it is a global find/replace across the entire frontend.**

         1. Replace the "hardcoded" color values in the Tailwind configuration
            file with css variables defined in the "base" layer of the
            `tailwind.css` file. This will not result in any visual changes.

      2. Add the dark mode colors as CSS variable definitions, nested under the
         `.dark-mode` CSS class, in the "base" layer of the `tailwind.css` file.
         This will not result in any visual changes, _except when
         `FORCE_DARK_MODE` is enabled._

      3. Visual Regression tests. Update
         `frontend/test/playwright/utils/breakpoints.ts` so that each breakpoint
         produces and expects a dark mode screenshot to pass as well as the
         existing light mode screenshot. **This will also be a significant diff,
         as at the time of writing it will create 293 new screenshots to review.
         This is also the point of the process where @fcoveram and
         @wordpress/openverse-frontend should review the full dark mode
         appearance for correctness and sufficient color contrast (see the
         ["Accessibility"](#accessibility) section for more details.** Existing
         screenshots should be renamed to `<snapshot_name>_light` and the new
         dark mode screenshots should be named `<snapshot_name>_dark`.

2. **Work Stream B**: Toggling dark mode

   1. Create a `DARK_MODE_UI_TOGGLE` feature flag which is off by default and
      switchable in staging.
   2. Implement logic for calculating a current "color mode" with the following
      state:

      ```ts
      interface ColorMode {
        preference: "dark" | "light" | "system" // Defaults to "system"
        systemValue: "light" | "dark" // Readonly representation of the system value
      }
      ```

      The color mode should be stored in a cookie so that a previously-selected
      user choice can be used when rendering via SSR and prevent a visual flash
      of the incorrect color mode. The "system" value is the default.

   3. Behind the feature flag, add the new user interface element which toggles
      dark mode (exact design TBD, but it will be comprised of existing UI
      components). Supports choosing between "dark", "light", and "system"
      modes, with "system" as the default. The "dark" and "light" options will
      set a `.dark-mode` or `.light-mode` class on the HTML element of the site.
      The default "system" choice does not add a class to the HTML element. When
      there is no HTML `.{color}-mode` class present, the site will default to
      the `prefers-color-scheme` media query value.
      1. Add a `TOGGLE_COLOR_SCHEME` analytics event with a playload including
         the color mode preference chosen by the user.
      2. Update our Cloudflare static page caching rule for the frontend in with
         a Cookie bypass rule (in pseudocode, something like `and not
         http.cookie contains "openverse_color_scheme"))

### Launch plan

> See the ["Rollback"](#rollback) section for details on how to revert this
> deployment.

1. Set the `DARK_MODE_UI_TOGGLE` feature flag to "on" in all environments.
2. Test and verify the staging deploy was successful and that dark mode:
   1. Looks correct
   2. The toggle works correctly (chosen settings persist, the control works
      with keyboard, etc.)
3. Deploy the production frontend and verify proper behavior after deployment.
4. Make a post on make.wordpress.org/openverse announcing the new dark mode.
5. Create a
   ["Request for Amplification"](https://github.com/WordPress/Marketing-Team/issues/new/choose)
   with the WordPress marketing team.

## Infrastructure

<!-- Describe any infrastructure that will need to be provisioned or modified. In particular, identify associated potential cost changes. -->

We will need one infrastructure pull request to update our Cloudflare frontend
caching. Specifically, we need to update our cache rule called "Cache static
pages" to bypass the cache when the color scheme cookie is present.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

The majority of accessibility considerations should have already been addressed
in the design stage. When implementing dark mode the main priority is
maintaining sufficient color contrast.

The actual UI toggle for dark mode should be written accessibly using our
existing components.

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

This can be rolled back in a critical scenario by hiding the UI control for dark
mode and hardcoding the "color mode" to `light` for all users. The later step
must be taken to guarantee that any previously-set user color preferences are
ignored.

Finally, in the event of a full rollback we would:

- Remove the dark mode CSS variables from the base CSS file
- Remove the test utility and feature flags
- Delete the dark mode visual regression test screenshots
- Delete or revise any marketing content
- Delete the cookie detection logic from our static page caching rule

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

This plan is designed to limit risk intentionally. One potential risk is that
our dark mode could evolve significantly over time, making the "palette swap"
strategy less effective due to numerous exceptions to the rule. If this were to
occur the approach chosen here would become inconvenient and verbose.
