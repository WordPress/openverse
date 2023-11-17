# Responding to Incidents

```{note}
Currently experiencing an issue with Openverse? For maintainers, please jump to the [Incident Response Runbook](/meta/incidents/runbooks/incident_response_runbook). Otherwise,
please [file a bug report](https://github.com/WordPress/openverse/issues/new?template=bug_report.md&title=Production+Incident:+Describe+the+incident) in GitHub or send a message in the
[Making WordPress Chat](https://make.wordpress.org/chat/), to the `#openverse`
channel.
```

This document defines the policy for handling production incidents that occur
within Openverse. The goal is to ensure that user-facing service disruptions are
handled promptly, efficiently, and effectively, mitigating impact on our users
and maintaining the highest level of service availability possible.

## What is an incident?

An **incident** is any event which compromises or could compromise the goals of
the Openverse project. While commonly technical problems with our services
(Openverse.org, the Openverse API, and "official" integrations like the WP core
integration and pattern directory integrations) these can also be incidents of a
public relations or community nature. Here are some example incidents:

- The API is serving slower-than-typical responses which occasionally time out
- Openverse.org has a critical bug preventing search for mobile users using RTL
  languages
- A user has posted public comments using hateful language towards an Openverse
  maintainer
- Openverse.org is completely offline
- Production resource usage is skyrocketing and could lead to downtime, but
  users are not impacted yet

All of these scenarios suggest that **Openverse behavior normally depended on or
expected by regular users is not behaving as it should.**

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
- **Stabilized** - The incident is no longer directly disrupting service. root
  causes may
- **Under investigation** - The root causes of the incident are being
  researched. Stabilized but not yet resolved
- **Resolved** - The incident is stable, and long-term fixes to prevent future
  occurrences or other mitigations have been identified.

As you might expect, incidents can be _destabilized_ if they reoccur, and the
state should rollback to "Stabilization pending":

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
| # | Name | Goal | Status After |
|---|------|------|--------------|
| 1 | Record | Visibly acknowledge the incident and create the communication threads necessary for ongoing discussion and investigation. Understand how bad the situation is based on our severity definitions. | Stabilization pending OR Stabilized (as appropriate)
| 2 | Stabilize |<p>If there is a total or partial outage, identify service stabilization options and action them. | Stabilized |
| 3 | Resolve | Identify outstanding improvements to the service that would mitigate the issue in the future and create tickets to implement. | Under investigation |
| 4 | Review | Identify process improvements. If the underlying cause is still unknown, identify further steps to resolve or continue investigation of the issue via 5-whys. | Under investigation OR Resolved (as appropriate) |

All maintainers are required to record incidents they encounter. **Crucially,
maintainers who record incidents are not _inherently_ responsible for
stabilizing them.** Their only required job is to record the incident. Every
incident has a **Lead** who is the person responsible for providing updates on
the incident and delegating tasks. The Lead is also responsible for hosting the
retrospective after the incident is resolved.

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
