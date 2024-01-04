# Yearly Planning: Process Outline

This document describes the process that the Openverse team strives to follow
when planning which projects will be worked on in the next calendar year.

```{note}
Many of the steps below reference resources that may only be accessible by maintainers.
The purpose of this document is primarily to share our process in a way that might be
useful for other projects, teams, or organizations. If you're interested in becoming a
maintainer, please check out our [welcome page](/general/quickstart.md)
for how to begin getting involved.
```

## Outcome

The outcome of the yearly planning should be a prioritized list of
[project threads in GitHub](https://github.com/WordPress/openverse/blob/main/.github/ISSUE_TEMPLATE/project_thread.md)
which are reflected on the
[project tracking board](/meta/project_boards/projects.md).

## Outline

Each step in the outline below includes a week estimate for how long this
process is expected to take between ~8 maintainers asynchronously across
multiple timezones.

### (Optional) Brainstorm project themes/categories (1 week)

```{note}
See: [Project Themes](/projects/yearly_planning/project_themes.md)
```

- Notes:
  - Consider WordPress Foundation goals to ensure Openverse's project themes are
    aligned.
- Process:
  1.  Each maintainer writes a 3-4 item list of ideas for project themes.
  2.  Team comes together, shares their lists, and identify the similarities and
      shared ideas to develop a set of themes/categories.
      - This can be done using stickies that are then grouped together, similar
        to a retrospective process.
- Stipulations:
  - Themes should be written in the imperative sense.
  - These themes/categories can help shape project ideas, but should not prevent
    any project ideas from being raised if they exist outside the existing
    themes/categories.
- Outcomes:
  - List of themes written in the imperative sense

### Describe ideas for next year's projects (4 weeks)

- Notes:
  - Include rollover from previous year and add or update descriptions for
    rolled over projects.
  - Find existing backlog issues that can be grouped into "projects" of related
    issues.
- Process:
  1.  Create the post on the
      [Make WordPress Blog](https://make.wordpress.org/openverse/) to solicit
      ideas from the community.
      - Additionally, set up a Google form to encourage better
        descriptions/organisation and make it more shareable outside the
        WordPress Community.
  2.  (2 weeks) Each maintainer individually describes project ideas in their
      own document. The team rep will seed community ideas to maintainers who
      are best equipped to flesh out those specific descriptions. Descriptions
      should define the scope of the project and the benefit. Describing
      projects on our own, without collaborating right away, helps to identify
      shared project ideas as well as potentially different ideas of very
      similar projects. These "duplicate" descriptions will uncover assumptions
      and nuances. Each idea should have the following:
      - Title
      - Summary
      - Description
      - Applicable project theme
      - Expected implementation plans
  3.  (1 week) Maintainers review each other's ideas and ask for clarification.
      - Point out similar ideas and explicitly label differences in project
        descriptions.
      - Identify connective themes across maintainers' documents.
  4.  (1 week) Team rep combines the ideas into a single document with similar
      ideas/descriptions side-by-side or combined.
  5.  Individually review the combined document and ask for clarifications if
      needed.
- Outcome:
  - List of clarified project summaries/titles with descriptions the intention

### Vote on the effort and impact of each project idea (3 weeks)

[graph_project_voting]:
  https://github.com/WordPress/openverse/tree/main/utilities/project_planning#graph-project-voting

- Notes:
  - Code: [Graph Project Voting][graph_project_voting]
  - Example spreadsheet: TODO
  - Fibonacci's numbers are used here instead of linear sequence: 2, 3, 5, 8, 13
    instead of 1, 2, 3, 4, 5. This helps communicate the big difference between
    a "huge project" and a "very small" project.
  - Maintainer's _confidence_ when voting is also recorded, on a scale of 1-3.
    This is useful in the analysis after-the-fact for showing which projects
    maintainers felt less confident about assessing.
  - This step is used as reference when voting during steps that follow.
- Process:
  1.  Create a spreadsheet of the projects with spaces for effort and impact
      with formatting options to record confidence for each vote.
  2.  Provide each maintainer with a tab within the spreadsheet and privately
      add votes, including confidence.
  3.  Generate the box-charts view of the combined votes with confidence using
      the [graphing script][graph_project_voting].
  4.  Review as a team, document impressions, and clarify discrepancies.
- Outcomes:
  - Box plots of effort and impact per-project, colored by average confidence.

### Estimate total available weeks of effort for the team for the next year (1 week)

[available_weeks_script]:
  https://github.com/WordPress/openverse/blob/main/utilities/project_planning/calculate_available_weeks.py

- Notes:
  - Code: [Calculate available weeks][available_weeks_script]
  - This step can occur concurrently with other steps.
- Process:
  1. Update the [script for calculating available weeks][available_weeks_script]
     with maintainers, conferences, and availability that match the upcoming
     year.
  2. Run the script and record the output for later steps.

### Vote on weeks of work for each project (1 week)

[calculate_average_weeks]:
  https://github.com/WordPress/openverse/tree/main/utilities/project_planning#average-weeks-of-work-calculation

- Notes:
  - Code: [Calculate average weeks per-project][calculate_average_weeks]
  - Example spreadsheet: TODO
  - The effort & impact graphs from the previous step can be used by each
    maintainer when estimating weeks.
  - Confidence should also be recorded here for later use.
  - Maintainers should only be voting on weeks of implementation work. Weeks
    required for the project planning & implementation plans should
    automatically be included using: 2 project plan weeks + (2 weeks \* \# of
    implementation plans).
- Process:
  1. Create a spreadsheet of the projects with a count of the number of
     implementation plans each project requires. Automatically deduce the total
     number of weeks with a formula by combining voted implementation time with
     the implementation plans per the formula above.
  2. Provide each maintainer with a tab within the spreadsheet and privately add
     votes, including confidence.
  3. Run the [script for calculating average weeks][calculate_average_weeks] to
     compute both average weeks of work and weighted average weeks (based on
     confidence votes).
  4. Record these values for the next step.
- ## Outcomes:

### Prioritise the ideas and identify dependencies (4 weeks)

- Notes:
  - This step revolves around deciding which projects "fit" into the next year
    based on weeks-of-effort estimates and the overall week availability of the
    team from the previous step

2.  In deciding the project list, ensure a balance between feature and internal
    work
3.  Process: 2. Create a spreadsheet of the projects with their combined
    weeks-of-work estimates with a method for marking projects for inclusion in
    the year. Copy the spreadsheet for each team member who privately decides on
    a list of projects to fill the available weeks of effort for the year. In
    other words, each person decides on a list of projects to propose for
    priority for 2024 that add up to the available weeks of effort for the
    year. 3. Combine those lists as follows: 1. Identify the projects everyone
    had on their final list 2. Identify the projects a majority had on their
    list 3. Identify the projects that few people had on their lists 4. Fill up
    a final list of projects collectively, starting first with the ones everyone
    agreed on, then the ones most agreed on, and then if there's still room,
    pick from the final list of projects that only a few people had on their
    lists.

### Create the projects list with project threads (1 week)

1.  P2 page for the team
2.  Make post describing the plan and linking to the project board
3.  Vote on which projects folks would be interested in/comfortable leading
4.  Process:
    1.  Delegate projects from the list to team members to create project
        threads and include the descriptions we created earlier in the process
    2.  Team lead writes the P2 page and make post?
    3.  Using created project threads, set up a spreadsheet for folks to vote on
        which projects they'd want to lead. This doesn't mean the person _will_
        be leading that effort, but it can be used to determine who might be
        interested when a new project is slated

### Retrospective on 2024 planning
