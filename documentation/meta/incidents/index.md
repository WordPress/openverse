# Responding to Incidents

```{note}
Currently experiencing an issue with Openverse? For maintainers, please jump to the [Incident Response Runbook](/meta/incidents/runbooks/incident_response_runbook). Otherwise,
please [file a bug report](https://github.com/WordPress/openverse/issues/new?template=bug_report.md&title=Production+Incident:+Describe+the+incident) in GitHub or send a message in the
[Making WordPress Chat](https://make.wordpress.org/chat/), to the `#openverse`
channel.
```

This document defines the policy for handling technical production incidents
that occur within Openverse. The goal is to ensure that user-facing service
disruptions are handled promptly, efficiently, and effectively, mitigating
impact on our users and maintaining the highest level of service availability
possible.

## What is an incident?

An **incident** in the context of these documents is any event which affects the
ability of Openverse to behave normally in a way that is depended on or expected
by regular users. This document and the referenced runbooks refer to incidents
as technical problems with our services (Openverse.org, the Openverse API, and
"official" integrations like the WP core integration and pattern directory
integrations). Here are some example incidents:

- The API is serving slower-than-typical responses which occasionally time out
- Openverse.org has a critical bug preventing search for mobile users using RTL
  languages maintainer
- Openverse.org is completely offline
- Production resource usage is skyrocketing and could lead to downtime, but
  users are not impacted yet

```{note}
There may be other issues that Openverse and its maintainers face that are of a public relations or community nature.
Those issues require a different approach which is not described in the scope of this document.
```

It is crucial to be proactive here; if something _might_ be an incident, but
you’re not certain, it is better to record it than to ignore it. Do not assume
"someone else" is handling an incident unless they have explicitly recorded it
using the process defined here.

## How do we _identify_ incidents?

Incidents can be detected through various channels such as automated alerts,
user reports, or through manual checks by maintainers. The Mini Support Rotation
(MSR) runner makes these checks as part of their daily responsibilities.

While the MSR runner should be monitoring our communication channels closely,
**any online maintainer who sees something that might be an incident should
follow the incident recording process outlined here.** This does not mean that
the reporting maintainer is responsible for stabilizing the incident or acting
as the incident lead. It simply means that they are responsible for making the
initial report on the incident.

## How do we _classify_ incidents?

Incidents are classified in two ways:

- **Severity** - How impactful the incident is
- **Status** - The current state of the incident

### Severity

Incidents should be classified using one of three levels of severity. It is
important to note that regardless of severity, working to stabilize services (or
whatever harm mitigation is relevant for the incident) always **takes priority
over regular project work and MSR duties.** Once service is stabilized, any
ongoing investigations, preventative measures, or documentation changes will be
prioritized by the team alongside our other work.

This severity scale is intentionally distinct from our GitHub priority scale.
Any GitHub issues created to _stabilize_ a Severity 1 or Severity 2 incident
should be marked as "critical" in GitHub. Other issues should be prioritized at
your own discretion.

- **Severity 1**: Critical issue affecting all/most users and all/most
  functionalities of Openverse.
- **Severity 2**: Major issue affecting a large number of users or critical
  functionality of Openverse.
- **Severity 3**: Minor issue affecting a limited number of users or
  non-critical functionality of Openverse.

### Status

- **Stabilization pending** - The incident is actively disrupting service
- **Stabilized** - The incident is no longer directly disrupting service. Root
  causes may still be unknown.
- **Under investigation** - The root causes of the incident are being
  researched. Stabilized but not yet resolved.
- **Resolved** - The incident is stable, and long-term fixes to prevent future
  occurrences or other mitigations have been identified.
- **Reviewed** - A retrospective has been completed for the incident.

As you might expect, incidents can be _destabilized_ if they reoccur, and the
state should roll back to "Stabilization pending". Some incidents may not
require further investigation once they are stabilized and can be immediately
resolved.

```{mermaid}
graph LR
    A[Stabilization pending]
    B[Stabilized]
    C[Under investigation]
    D[Resolved]

    A --> B
    B --> C
    B --> A
    C --> A
    C --> D
    B --> D
    D --> A
```

## How do we _handle_ incidents?

```{warning}
Dealing with an incident now? Go to the [Incident Response Runbook](/meta/incidents/runbooks/incident_response_runbook).
```

This section addresses the philosophy of our approach to incident management and
explanation behind the steps in the
[runbook](/meta/incidents/runbooks/incident_response_runbook).

There are four main steps to handling production incidents:

<!-- prettier-ignore -->
| # | Name        | Goal                                                                                                                                                                                             | Tag                     | Status After                                         |
|---|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------|------------------------------------------------------|
| 1 | Record      | Visibly acknowledge the incident and create the communication threads necessary for ongoing discussion and investigation. Understand how bad the situation is based on our severity definitions. | `#status-recorded`      | Stabilization pending OR Stabilized (as appropriate) |
| 2 | Stabilize   | If there is a total or partial outage, identify service stabilization options and action them.                                                                                                   | `#status-stabilized`    | Stabilized                                           |
| 3 | Investigate | Identify outstanding improvements to the service that would mitigate the issue in the future and create tickets to implement.                                                                    | `#status-investigating` | Under investigation OR Resolved (as appropriate)     |
| 4 | Resolve     | Complete the immediately necessary work to prevent this issue from recurring in the future.                                                                                                      | `#status-resolved`      | Review (if needed)                                   |
| 4 | Review      | Identify process improvements. If the underlying cause is still unknown, identify further steps to resolve or continue investigation of the issue via 5-whys.                                    | `#status-reviewed`      | |

All maintainers are required to record incidents they encounter. **Crucially,
maintainers who record incidents are not _inherently_ responsible for
stabilizing them.** Their only required job is to record the incident.
Additionally, maintainers who stabilize services may not be the ones to perform
the investigation after stabilization has been reached. Every incident has a
**Lead** who is the person responsible for providing updates on the incident and
delegating tasks. The Lead is also responsible for hosting the retrospective
after the incident is resolved.

### How do we determine the lead?

By default, this is the week’s MSR runner. If it is outside the MSR runner’s
working hours, or they are unresponsive (with later explanation, ideally)
someone else will need to be the lead. It is the recorder’s job to find this
lead or act as this lead; although for incidents that have a severity <= 2,
stabilizing the service may be the highest priority and take precedence over
finding a lead. Factors which should be considered in finding a lead are
availability and expertise. Is anyone online uniquely qualified to take this
work on? Alternatively, has one person been handling most incidents and this
time, someone new should take on? Consulting the threads for past incidents will
make it easier to see the distribution of incident leadership so we can easily
find who hasn’t done it recently.

We can use our discretion in making these decisions, and if we find that the
distribution of Lead responsibilities is inequitably distributed we can consider
formal processes for finding them.

## Runbooks

```{toctree}
:titlesonly:

runbooks/index
```
