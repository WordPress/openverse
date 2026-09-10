# 2023-09-13 Project proposal: Project board improvements

**Author**: @dhruvkb

## Reviewers

- [x] @AetherUnbound
- [x] @obulat

## Project summary

The end-goal of this project is to have a comprehensive set of boards where one
can track all aspects of work being done in Openverse. This includes issues, PRs
and project discussions. These boards should have lots of different views, for
different purposes, and these views should be standardised and documented.

Each of these projects should be highly automated, where minimal effort is
needed to keep these boards synced to reality. Most human actions should be
complemented by automations that can sync the effects of the event to the board.
These should be a combination of built-in and custom workflows, where custom
workflows are consistent, well-tested and maintainable.

## Goals

This project should do both of the following things:

- enhance our productivity by reducing a lot of work required to keep these
  projects up to date
- increase our accountability by helping us stay on top of our work and also
  being aware of what others in the team are working on

## Requirements and success

The following are requirements & success criteria for the project automations:

- all issues and PRs are automatically added to the relevant project boards
- all cards are in the right columns as per their status
- rarely, if ever, do we need to manually move cards to the right columns
  (except for moving cards from "📋 Backlog" to "📅 To do" to prioritise them)
- all custom automations are in a single place and are easy to maintain
- all automations are documented

The following are requirements & success criteria for the project views:

- views are created based on clear utility in helping maintainers track work
- views are clearly labelled, and it's known which view to use for what purpose
- all views, and their utilities, are documented

## Participants

The boards are primarily an internal tool for maintainers and to some extent, an
external tools for contributors (to find potential inroads to contribute) and
project leadership (to gauge activity and progress).

### Expectation for maintainers

- Knowing what issues everyone, including themselves, is working on at a given
  time.
- Having a clear idea of what issues need to be worked on after the current
  issues on hand are resolved.
- Being able to find critical or high priority issues that haven't been
  addressed.
- Knowing the status of their own PRs.
- Identifying PRs that require additional reviews.

### Expectation for contributors

- Finding help wanted or good first issues that are not already assigned or
  being worked on by someone else.
- Knowing that their PRs will be noticed, reviewed and merged in a timely
  manner.

### Expectation for project leadership

- While project leadership are not directly concerned with the day-to-day issues
  and PRs, they should be able to see a steady movement of cards from
  left-to-right.
- The project discussion boards are more relevant to the leadership.

## Miscellaneous

This project should not have any components related to infrastructure, a11y or
marketing as it is internal. Several new workflows will be defined which will be
executed on GitHub Actions.

## Required implementation plans

The following implementation plans would be required:

1. improvements to existing, restoration of previous and creation of new
   automations
   ([plan](/projects/proposals/project_improvement/20230914-implementation_plan_project_automations.md))
2. documentation of existing and creation of new useful views for project boards
   (plan)
3. discussion of ideas related to the project and discussion boards as that has
   not been covered in #1.
