# Responding to Incidents

```{note}
Currently experiencing an issue with Openverse? For maintainers, please jump to the [Incident Response Runbook](/meta/incidents/runbooks/incident_response_runbook). Otherwise,
please [file a bug report](https://github.com/WordPress/openverse/issues/new?template=bug_report.md&title=Production+Incident:+Describe+the+incident) in GitHub,
[submit a security advisory](https://github.com/WordPress/openverse/security/advisories/new), or send a message in the
[Making WordPress Chat](https://make.wordpress.org/chat/), to the `#openverse`
channel.
```

This document defines the policy for handling technical production incidents
that occur within Openverse. The goal is to ensure that user-facing service
disruptions are handled promptly, efficiently, and effectively, mitigating
impact on our users and maintaining the highest level of service availability
possible.

## What is an incident?

This document and the referenced runbooks refer to incidents as technical
problems with our services (Openverse.org, the Openverse API, and "official"
integrations like the WP core integration and pattern directory integrations).
Here are some example incidents:

- The API is serving slower-than-typical responses which occasionally time out
- Openverse.org has a critical bug preventing search for mobile users using RTL
  languages
- Openverse.org is completely offline
- Production resource usage is skyrocketing and could lead to downtime, but
  users are not impacted yet

```{note}
There may be other issues that Openverse and its maintainers face related to its reputation or the community.
Those issues require a different approach which is not covered in the scope of this document.
```

It is crucial to be proactive here; if something _might_ be an incident, but
you’re not certain, it is better to record it than to ignore it. Do not assume
"someone else" is handling an incident unless they have explicitly recorded it
using the process defined here.

## How do we _identify_ incidents?

Incidents are detected through various channels such as automated alerts, user
reports, or through manual checks by maintainers. The Mini Support Rotation
(MSR) runner makes these checks as part of their daily responsibilities.

While the MSR runner monitors our communication channels closely, **any online
maintainer who sees something that might be an incident should follow the
incident recording process outlined here.** This does not mean that the
reporting maintainer is inherently responsible for stabilizing the incident or
investigating the root cause. It only means that they are responsible for making
the initial report on the incident. Additionally, maintainers who stabilize
services may not be the ones to perform the investigation after stabilization
has been reached. Every incident has a [**Lead**](#how-do-we-determine-the-lead)
who is the person responsible for providing updates on the incident and
delegating tasks. The Lead is also responsible for hosting the retrospective
after the incident is resolved.

## How do we _classify_ incidents?

Incidents are classified in two ways:

- **Severity** - The impact of the incident
- **Status** - The current state of the incident

### Severity

Incidents are classified using one of three levels of severity. It is important
to note that regardless of severity, working to stabilize services (or whatever
harm mitigation is relevant for the incident) always **takes priority over
regular project work and MSR duties.** Once services are stabilized, any ongoing
investigations, preventative measures, or documentation changes will be
prioritized by the team alongside our other work.

This severity scale is intentionally distinct from our GitHub priority scale.
Any GitHub issues created to _stabilize_ a Severity 1 or Severity 2 incident are
marked as "critical" in GitHub. Other issues are prioritized at your own
discretion.

- **Severity 1**: Critical issue affecting all/most users and all/most
  functionalities of Openverse.
- **Severity 2**: Major issue affecting a large number of users or critical
  functionality of Openverse.
- **Severity 3**: Minor issue affecting a limited number of users or
  non-critical functionality of Openverse.

### Status

- **Stabilization pending** - The incident is actively disrupting service.
- **Stabilized** - The incident is no longer directly disrupting service. Root
  causes may still be unknown.
- **Under investigation** - The root causes of the incident are being
  researched. Stabilized but not yet resolved. Fixes may be identified but not
  yet implemented.
- **Resolved** - The incident is stable, and short-term/immediate fixes to
  prevent future occurrences have been implemented. Long-term fixes and
  improvements may still be open for work to be prioritized along with all other
  work.
- **Reviewed** - A retrospective has been completed for the incident.

As you might expect, incidents can be _destabilized_ if they reoccur, and the
state should roll back to "Stabilization pending". Some incidents may not
require further investigation once they are stabilized and can be immediately
resolved. If more than 48 hours have elapsed from the resolution of an incident
and it recurs, a new incident should be created.

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

There are five main steps to handling production incidents:

<!-- prettier-ignore -->
| # | Name        | Goal                                                                                                                                                                                             | Tag                     | Status After                                         |
|---|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------|------------------------------------------------------|
| 1 | Record      | Visibly acknowledge the incident and create the communication threads necessary for ongoing discussion and investigation. Understand how bad the situation is based on our severity definitions. | `#status-recorded`      | Stabilization pending OR Stabilized (as appropriate) |
| 2 | Stabilize   | If there is a total or partial outage, identify service stabilization options and action them.                                                                                                   | `#status-stabilized`    | Stabilized                                           |
| 3 | Investigate | Identify outstanding improvements to the service that would mitigate the issue in the future and create tickets to implement.                                                                    | `#status-investigating` | Under investigation OR Resolved (as appropriate)     |
| 4 | Resolve     | Complete the immediately necessary work to prevent this issue from recurring in the future.                                                                                                      | `#status-resolved`      | Review (if needed)                                   |
| 5 | Review      | Identify process improvements. If the underlying cause is still unknown, identify further steps to resolve or continue investigation of the issue via 5-whys.                                    | `#status-reviewed`      | |

### How do we determine the lead?

The current MSR runner is the default incident lead. If it is outside the MSR
runner’s working hours, or they are unable to lead the incident response, then
someone else will need to be the lead. It is the recorder’s job to find this
lead or act as this lead; for incidents that are severity 1 or 2, stabilizing
the service may be the highest priority and take precedence over finding a lead.
Factors which should be considered in finding a lead are:

- Availability
  - Has one person been handling most incidents and this time, someone new
    should take on?
  - Consult threads for past incidents to see the distribution of recent
    incident leadership and find someone who hasn’t recently lead an incident.
- Expertise. Is anyone online uniquely qualified to guide the resolution?

This process is intentionally flexible to allow for the rapidly evolving nature
of incidents and to avoid too much rigidity. If the distribution of lead
responsibilities is inequitably distributed, we will develop alternative
processes for assigning leads.

## Runbooks

```{toctree}
:titlesonly:

runbooks/index
```
