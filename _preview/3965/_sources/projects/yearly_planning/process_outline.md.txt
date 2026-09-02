# Yearly Planning: Process Outline

[project_thread_template]:
  https://github.com/WordPress/openverse/blob/main/.github/ISSUE_TEMPLATE/project_thread.md
[project_tracking_board]: /meta/project_boards/projects.md
[team_rep]:
  https://make.wordpress.org/training/handbook/training-team-how-to-guides/team-roles/team-rep/

This document describes the process that the Openverse team strives to follow
when planning which projects will be worked on in the next calendar year.

```{note}
Some of the steps below reference resources that may only be accessible by maintainers.
The purpose of this document is primarily to share our process in a way that might be
useful for other projects, teams, or organizations. If you're interested in becoming a
maintainer, please check out our [welcome page](/general/quickstart.md)
for how to begin getting involved.
```

## Outcome

The outcome of the yearly planning should be a prioritized list of [project
threads in GitHub][project_thread_template] for the next year which are
reflected on the [project tracking board][project_tracking_board].

## Steps

Each step in the outline below includes an estimate for how many weeks that step
is expected to take between ~8 maintainers asynchronously across multiple
timezones. In total, the yearly planning process is expected to take between 12
and 13 weeks.

The steps below include the following:

- **Code**: Any associated code for the step, if necessary.
- **Example spreadsheet**: Any reference spreadsheets for the step, if
  necessary. These may require maintainer-provided access to view.
- **Notes**: Intentions for the step and important aspects to consider.
- **Process**: An ordered set of actions to take for completing the step.
- **Outcome(s)**: Any tangible deliverables from the step.

### (Optional) Brainstorm project themes/categories (1 week)

```{tip}
See: [Project Themes](/projects/yearly_planning/project_themes.md)
```

- **Notes**:
  - Consider WordPress Foundation goals to ensure Openverse's project themes are
    aligned.
  - Themes should be written in the imperative sense.
  - These themes/categories can help shape project ideas, but should not prevent
    any project ideas from being raised if they exist outside the existing
    themes/categories.
- **Process**:
  1.  Each maintainer writes a 3-4 item list of ideas for project themes.
  2.  The maintainers come together, share their lists, and identify the
      similarities and shared ideas to develop a set of themes/categories.
      - This can be done using stickies that are then grouped together, similar
        to the [retrospective process](#retrospective).
- **Outcome**: A list of themes written in the imperative sense.

### Describe ideas for next year's projects (4 weeks)

- **Notes**:
  - Include projects which should be rolled over from the previous year and add
    or update descriptions for said projects.
  - Find existing backlog issues that can be grouped into "projects" of related
    issues.
- **Process**:
  1.  Create a post on the
      [Make WordPress Blog](https://make.wordpress.org/openverse/) to solicit
      ideas from the community.
      - Additionally, set up a Google form to encourage better
        descriptions/organisation and make it more shareable outside the
        WordPress Community.
  2.  (2 weeks) Each maintainer individually describes project ideas in their
      own document. The [team rep][team_rep] will seed community ideas to
      maintainers who are best equipped to flesh out those specific
      descriptions. Descriptions should define the scope of the project and the
      benefit. Describing projects on our own, without collaborating right away,
      helps to identify shared project ideas as well as potentially different
      ideas of similar projects. These "duplicate" descriptions will uncover
      assumptions and nuances. Each project idea should have the following:
      - Title
      - Summary
      - Description
      - Applicable project theme(s)
      - Anticipated implementation plans
  3.  (1 week) Maintainers review each other's ideas and ask for clarification.
      - Point out similar ideas and explicitly label differences in project
        descriptions.
      - Identify projects which might need more explicit scoping.
  4.  (1 week) [Team rep][team_rep] combines the ideas into a single document
      with similar ideas/descriptions side-by-side or combined.
  5.  Individually review the combined document and ask for additional
      clarifications if needed.
- **Outcome**: A list of clarified project summaries/titles with descriptions
  and projected implementation plans in a single document.

### Vote on the effort and impact of each project idea (3 weeks)

[graph_project_voting]:
  https://github.com/WordPress/openverse/tree/main/utilities/project_planning#graph-project-voting

- **Code**: [Graph Project Voting][graph_project_voting]
- **Example spreadsheet**:
  [Project Ideas Effort & Impact Voting](https://docs.google.com/spreadsheets/d/1a_xBQvgirYF7Tzmbr5bbfvxaV0RKyBmoJ3FvCVs5zG8/edit?usp=sharing)
- **Notes**:
  <!-- "very" is intentional in "very small" to emphasise the intentional imprecision of this scale. -->
  <!-- vale proselint.Very = NO -->
  - Fibonacci's numbers are used here instead of linear sequence: 2, 3, 5, 8, 13
  instead of 1, 2, 3, 4, 5. This helps communicate the big difference between a
  "huge project" and a "very small" project.
  <!-- vale proselint.Very = YES -->
  - Maintainer's _confidence_ when voting is also recorded, on a scale of 1-3.
    This is useful in the analysis after-the-fact for showing which projects
    maintainers felt less confident about assessing.
  - This step is used as reference when voting during steps that follow.
- **Process**:
  1.  Create a spreadsheet of the projects with spaces for effort and impact
      with an additional column to record confidence for each vote.
  2.  Provide each maintainer with a tab within the spreadsheet and privately
      add votes, including confidence.
  3.  Generate the box-charts view of the combined votes with confidence using
      the [graphing script][graph_project_voting].
  4.  Review as a team, document impressions, and clarify discrepancies.
- **Outcome**: Box plots of effort and impact per-project, colored by average
  confidence.

### Estimate total available weeks of effort for the team for the next year

[available_weeks_script]:
  https://github.com/WordPress/openverse/blob/main/utilities/project_planning/calculate_available_weeks.py

- **Code**: [Calculate available weeks][available_weeks_script]
- **Notes**:
  - This step can occur concurrently with other steps and should not take
    additional time.
- **Process**:
  1. Update the [script for calculating available weeks][available_weeks_script]
     with maintainers, conferences, and availability that match the upcoming
     year.
  2. Run the script and record the output for later steps.
- **Outcome**: A single number representing the estimated available weeks for
  work for the next year.

### Vote on weeks of work for each project (1 week)

[calculate_average_weeks]:
  https://github.com/WordPress/openverse/tree/main/utilities/project_planning#average-weeks-of-work-calculation

- **Code**: [Calculate average weeks per-project][calculate_average_weeks]
- **Example spreadsheet**:
  [Project Weeks Of Work Voting](https://docs.google.com/spreadsheets/d/1duRS489QMnQKaXjDq4BjEhyEUPQXs7GeMKNWhCLeE1s/edit?usp=sharing)
- **Notes**:
  - The effort & impact graphs from the previous step can be used by each
    maintainer when estimating weeks.
  - Confidence should also be recorded here for later use.
  - Maintainers should only be voting on weeks of implementation work. Weeks
    required for the project planning & implementation plans should
    automatically be included using: `2 project plan weeks` + (`2 weeks` x
    `# of anticipated implementation plans`).
- **Process**:
  1. Create a spreadsheet of the projects with a count of the number of
     implementation plans each project requires. Automatically compute the total
     number of weeks with a formula by combining voted implementation time with
     the implementation plans per the formula above.
  2. Provide each maintainer with a tab within the spreadsheet and privately add
     estimations, including confidence.
  3. Run the [script for calculating average weeks][calculate_average_weeks] to
     compute both average weeks of work and weighted average weeks (based on
     confidence votes).
  4. Record these values for the next step.
- **Outcome**: Average and weighted average weeks of work for each project.

### Vote on project inclusion for next year (1 week)

[sum_selection_votes]:
  https://github.com/WordPress/openverse/tree/main/utilities/project_planning#project-selection

- **Code**: [Project selection aggregation][sum_selection_votes]
- **Example spreadsheet**:
  [Project Selection Voting](https://docs.google.com/spreadsheets/d/1OA6fptxMyvAQvJ0U_G9f-oVt_Emdx2gA1VM68WI3hUg/edit?usp=sharing)
- **Notes**:
  - This step revolves around deciding which projects "fit" into the next year
    based on weeks-of-effort estimates and the overall week availability of the
    team from the previous step.
  - The assumption is that, at this point, there will be a surpless of projects
    and a restriction based on how many hours were computed as available in a
    previous step.
- **Process**:
  1. Create a spreadsheet of the projects with the average and weighted average
     weeks of work per project. Include as input the available weeks of work
     computed in a previous step. Allow maintainers to either exclude or include
     projects for the next year, and automatically subtract the weeks that
     project will occupy from the remaining available weeks.
  2. Provide each maintainer with a tab within the spreadsheet and privately add
     selections.
  3. Run the [script for grouping the selected projects][sum_selection_votes].
  4. Record these values for the next step.
- **Outcome**: A list of projects binned by the groups described [in the
  selection script][sum_selection_votes].

### Prioritise the ideas and identify dependencies (2 weeks)

- **Notes**:
  - This step will require discussion among maintainers to determine a final,
    conclusive list of which projects should be included for the next year.
  - Further assessment, clarification, and refining of projects may be necessary
    during or after this step.
  - If possible, a synchronous discussion might be best for quickly iterating
    over the list of projects.
  - It may be easiest for the [team rep][team_rep] to dictate _prioritization_
    of the selected projects throughout the year, considering impact, spread of
    work (features vs. maintenance), and community events.
- **Process**:
  1. Share and discuss the binned projects determined from the previous step.
  2. Create a new tab in the previous project selection spreadsheet for
     recording team votes.
  3. Fill up a final list of projects collectively, starting first with the ones
     everyone agreed on, then the ones most agreed on, and then if there's still
     room, pick from the final list of projects that only a few people had on
     their lists.
  4. Prioritize those projects by order of which projects should be completed
     throughout the year (this may be done individually by the [team
     rep][team_rep]).
- **Outcome**: A canonical list of projects ordered by priority for the next
  year.

### Create the projects list with project threads (1 week)

- **Example spreadsheet**:
  [Project Lead Interest Voting](https://docs.google.com/spreadsheets/d/13mYbcc61ZMHQA8qiuX4IStVr1fYQeVQBenTMucK_ki8/edit?usp=sharing)
- **Notes**:
  - The project threads are made using the [project thread issue
    template][project_thread_template] in GitHub.
- **Process**:
  1. The [team rep][team_rep] should prepare the [project tracking
     board][project_tracking_board] in GitHub by archiving the previous year's
     completed project threads and removing any projects which were not
     completed and not scoped for the next year.
  2. Delegate projects from the canonical list to maintainers to create project
     threads, using the descriptions created earlier in the process.
  3. Using created project threads, set up a spreadsheet for maintainers to vote
     on which projects they would want to lead. This doesn't mean the maintainer
     _will_ be leading that effort, but it can be used to determine who might be
     interested when a new project is slated for work
- **Outcomes**:
  - A list of project threads in GitHub associated with the [project
    tracker][project_tracking_board].
  - A list of potential project leads for each project.

### Retrospective

- **Notes**:
  - Once the planning is complete, it's useful for the maintainers to set aside
    time to review how the planning process went and what improvements can be
    made.
  - There are many example resources for how to run this retrospective,
    including
    [resources from Atlassian](https://www.atlassian.com/team-playbook/plays/retrospective).
- **Process**:
  1. Each maintainer should make notes for what worked, what could have gone
     better, and process improvements/experiments.
  2. Either synchronously or asynchronously, group the notes together under
     shared concepts/ideas.
  3. Extract action items from the notes and insuing discussion to apply to next
     year's planning.
- **Outcome**: Actionable steps, if any, to take before planning begins for the
  next year.
