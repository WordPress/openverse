# 2023-06-06 Implementation Plan: Baseline Alarms for ECS Services

**Author**: @sarayourfriend

```{note}
This implementation plan is not associated with a specific project plan.
It was requested as a result of various discussions between maintainers
reflecting on recent incidents. While there were some open issues to add
monitors and alarms for specific things, without a cohesive implementation
plan to describe the general approach, these continued to fall to the
wayside. We need to establish a general approach for the initial set of
monitors and alarms that can be built and iterated upon as the project evolves.
```

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [ ] TBD
- [ ] TBD

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- Milestone (TBD)

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

The Django API and Nuxt frontend have a reasonable set of baseline alarms. The
specific outcome should be a set of unstable alerts that can be iterated on and
later stabilised, once we have had time to tweak the specific settings. We
should not expect that the initial implementation of alarms will be sufficient.
We will need to iterate on the settings over time for them to become stable,
reliable alarms.

## Goals

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

This implementation plan has the following goals:

1. Establish a baseline approach for maintaining and configuring monitors and
   alarms through Terraform.
2. Propose an initial set of unstable alerts for our ECS services and describe
   their implementation details.
3. Describe a plan for stabilising new alarms that includes creating and
   iterating on run books for each alarm.

## Prior Art

Previous planning occurred for a monitoring project. The only document for that
[is here](/projects/proposals/monitoring/20220307-project_proposal.md). However,
that document was written before we had migrated the frontend and API to ECS. It
also assumes that we would be able to move all our monitoring infrastructure to
Grafana, Prometheus, and other non-AWS tools. That has not been the case,
however. For now, until we are able to prioritise setting up our own monitoring
infrastructure, we will need to accept our reliance on AWS tools.

## Tools

- [AWS CloudWatch Alarms](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html)
- [AWS Simple Notification Service (SNS)](https://docs.aws.amazon.com/sns/?id=docs_gateway/)

We will continue to use the SNS Email alerts tool. This is a cheap and easy way
to send alerts to our notification channels.

We've discussed using EventBridge to identify unhealthy task instances, but the
ELB "UnHealthyHostCount" metric should be sufficient for our initial
implementation. Working with EventBridge is sufficiently different from
CloudWatch metrics such that it would significantly increase the complexity of
this implementation plan.

## Terms

This list of terms attempts to match AWS's own terminology. Personally I find
some of these confusing, but in the interest of reducing the cognitive overhead
of switching between our documentation and CloudWatch, I've chosen to use these
terms anyway. Others (like an alarm "going off") may be somewhat colloquial or
casual jargon, but they are commonly used in the field.

- "Alarm": Something that actively monitors a metric or set of metrics. Alarms
  have explicit conditions that codify when the relevant metrics are not in an
  acceptable state.
- "Metric": Data generated from services or their infrastructure that can be
  used by alarms to evaluate alarm conditions.
- "Condition": The observable state of an alarm's metrics that cause it to enter
  into an "alarm" state.
- "In alarm": The state of an alarm whose metrics have met the alarm conditions.
- "Alarming" and "going off": Used to describe an alarm "in alarm".
- "Alert": A notification sent as a result of an alarm entering into a state of
  alarm.
- "Run book": Documentation describing a set of steps followed to respond to an
  alert. Run book details may be general (shared between all alerts) or specific
  to the alert in question. All possible alerts have run books.

```{note}
I use "alarm" throughout this document as a synonym for "alarms that send alerts".
This nuance is necessary because not all alarms individually send alerts, as
composite alarms may group multiple individual alarms to reduce noise or duplication.

Alarms can also be used to trigger actions other than alerts. While this isn't something
we take advantage of in this implementation plan, it is important to keep in mind, especially
with respect to the focus of run books and stabilisation (all covered in detail here).
```

## Overview

### Terraform Configuration

Alarms must be considered per-environment and per-service. It is highly unlikely
that alarm configuration can be shared between environments or services. Even if
it were possible, it would be undesirable as it would reduce flexibility in the
face of future changes to metric characteristics. In light of this, alarms will
be configured in a new monitoring namespace in the `next/modules` directory
within the concrete modules for services as internal submodules. For example,
Django API monitoring configuration would go in
`/modules/monitoring/production-api` and be instantiated in the production root
module in `api.tf`:

```terraform
module "api-monitoring" {
   source = "../modules/monitoring/production-api"
}
```

New modules for each service/environment help to prevent an increase in root
module complexity.

I also considered using nested internal modules. In that form, production Django
API alarms would be configured in
`/modules/concrete/api/modules/production-monitoring/main.tf`. The concrete
service modules would use `count` on the module block (a recently available
Terraform feature) to instantiate the correct monitoring block for the
environment:

```terraform
// /modules/concrete/<service>/main.tf

module "production-monitoring" {
   source = "./modules/production-monitoring"
   count = var.environment == "production" ? 1 : 0
}

module "staging-monitoring" {
   source = "./modules/staging-monitoring"
   count = var.environment == "staging" ? 1 : 0
}
```

Nesting the configuration in the concrete service module helps to further reduce
the complexity of the root modules. However, it may also inadvertently hide the
monitoring configuration for the module, which may in the end be more confusing
for maintainers.

We will need at least one new SNS topic for unstable alarms to send
notifications to a channel specific for unstable alarms. This helps maintainers
distinguish between the type of alerts they might be responding to. This should
be created in the `singleton` module and follow the existing pattern of
deferring management to the production environment by using a data resource in
staging.

```{note}
While this section mentions and creates guidelines for dealing with the fact that
monitoring configuration must be distinct per environment, this implementation plan
makes no proposals to monitor staging.
```

### Stable vs unstable alarms

As this project will add several new alarms, it is critical to understand the
distinction between stable and unstable ones. In particular, all maintainers
interacting with the new tools must understand what response and urgency is
appropriate for each instance. In this and other sections that discuss stable
and unstable alarms, I focus primarily on the alarms that send alerts aspect.
However, for composite alarms, the accuracy of the notifications is causes is
contingent on the alarms it responds to.

Alarms should be considered unstable if they regularly produce false positives.
That is to say, if we incorrectly send an alert, and this happens on a regular
basis, then the alarm is unstable. Stable alarms, on the other hand, should have
virtually no incidents of false positives. If an alarm configuration is stable,
when the alert is sent, it should be assumed that something is wrong that needs
to be addressed[^something-is-wrong]. If an alarm that is currently considered
unstable goes off, it should be investigated with urgency relative to the data
codified in the alarm's run book and the judgement of the person responding to
the alert.

[^something-is-wrong]:
    This says nothing to the severity of the issue, however, which may or may
    not be codified in alarms and alert configuration but is always up to the
    person responding to the alert to decide.

In our case, because all the alarms proposed in this plan are new and for
services that have never had alarms of this nature, all of them will begin their
life as unstable alarms. For each alarm, until it is deemed stable (after we
have observed for a sufficient period of time that it does not create false
positives), alarms will follow the process outlined below for "unstable alarm
response".

### Run books

Alert run books document the process for understanding a particular alert from
one or many alarms. Alert run books are not replacements for the general
incident response plan and maintainers must defer to the general process for
incidence response. Alert run books help maintainers identify the severity of an
issue. While an alarm is still unstable, the run book also serves to document
historical information relevant to identifying false positives or potential
tweaks to the underlying alarms that may help the alarm reach stability. Alert
run books should also document downtime.

Run books are critical to alarm development because they codify the general set
of steps to be taken in response to a particular alert. While some steps are
shared in common, details for specific alarms are still necessary. Every run
book should give guidelines for how to evaluate the severity of the issue and
how to identify false positives. Some alarms may share similar or exactly the
same steps for these. In those cases, we can develop documents that are linked
to from individual alert run books.

These run books must explicitly defer to the general incident response plan and
should complement it. Alert run books should describe how to follow the general
incident response plan for the specific alert in question.

```{note}
Run books are for _alerts_, not alarms. Alerts inform us of relevant alarm
states. Some alarms may go off for multiple states. For example, anomaly detection may use the same alarm to notify when a metric is too high or too low. Each is a separate "alert" and may require separate information to identify severity. Additional consideration may be necessary for alerts from composite alarms. These may require manually checking multiple alarms to help identify severity. It is
important to keep this in mind as it helps us focus each run book as much as possible so that responders know exactly where to look for any given alert.
```

Run books must include the following:

- Stability: whether the alert is considered stable or unstable
- Maintainer, if the alert is unstable
- Confidence, if the alert is unstable; notes to help communicate to anyone
  triaging the alert how to evaluate the accuracy of a specific notification
  - Collaborative but ultimately the responsibility of the unstable alert
    maintainer to update
- Instructions/guidelines to help identify the severity of the issue

Run books do not need to include anything about the general process of
responding to incidents. For example, they do not need to include how to triage
the issue once you understand the severity nor who will be responsible for
responding to the incident. As above, the run book is a supplement to the
general incident response plan and should not seek to replace it.

Every notification must include a link to the relevant run book.

### Stabilising Alarms

All unstable alarm should eventually be stabilised or deleted. No alarm should
indefinitely stay in the "unstable" category. Each alarm will be assigned to a
maintainer who will be responsible for investigating alarms that come from alarm
while it is unstable at a medium/high priority, depending on the context and
relative scepticism of the particular alarm. The maintainer assigned to
stabilise the alarm should not be solely responsible for identifying areas of
stability improvement. The development of automated monitoring tools is a
collaborative effort. However, by assigning each alarm to an individual
maintainer, we can increase accountability for particular alarms, ensuring that
none of them fall to the wayside. It also ensures that each alarm has someone
who understands the long-term context of the alarm, is aware of all of its
previous behaviour, and has paid consistent attention to it. Consider the
maintainer assigned to the alarm to have the same role as project leads do for
projects. A project lead is to a project as an alarm maintainer is to an
unstable alarm. The maintainer will create issues to iterate on the alarm and
its run book. Once the alarm is stabilised, there will no longer be a single
person assigned to it. Once the person responsible for stabilising the alarm has
reached a high level of confidence that the alarm will not regularly cause false
positives, the alarm should be stabilised and a run book should be added to the
documentation site for the alarm. To summarise the overall process:

1. Propose a new alarm
2. Implement the unstable version of the alarm required and create the initial
   run book and link it from the notification for the alarm
3. Evaluate the new alarm over time to ensure correctness
4. Iterate on the severity identification guide for alerts from the alarm based
   on experience evaluating the unstable alarm
5. Stabilise the alarm and change its notification channel

#### Strategies for Stabilisation

- Identify downtime periods
- Use a more flexible/broader period of time before the alarm goes off
- Use a composite alarm to compare the state of related alarms and only send an
  alert when a particular alarm configuration is present (e.g., don't alert if
  some other alarm is already sending alerts, etc.)

### Alarm Response Guidelines

#### Unstable Alarm Response

Unstable alarm response follows a gradient of urgency that depends on the level
of scepticism/confidence we have in the alarm so far. This information must be
recorded in the run book in the notification. Generally speaking, however,
alerts from unstable alarms should not immediately trigger urgent investigation.
The alarms should be triaged, reviewed by whomever notices them according to the
run book, and then assigned to whomever is the person in charge of stabilising
the alarm over time unless the person triaging notices that the outage severity
warrants immediate response. Unstable alarm are not _necessarily_ inaccurate.
They can and probably will send valid alerts, whether only occasionally or more
reliably. However, whether an unstable alarm should be treated with critical
urgency depends explicitly on the documented status of the alarm.

To say this another way and more explicitly: unstable alarm response requires a
nuanced and thoughtful approach to determine whether any given event is valid or
a false positive. In either instance, it must be documented and triaged to the
appropriate person according to the general incident response plan.

#### Stable Alarm Response

A stable alarm must be treated with critical urgency until severity is
determined. Because the goal of the general incident response plan is first and
foremost to stabilise the service and not to fix the problem, the run book
should draw a careful distinction between any advice it might contain for
stabilising the service in light of the alarm vs fixing the service. While some
alarms may point to issues with likely fixes, the primary focus should be to
give advice for stabilising the service. The incidence response afterwards will
focus on identifying the root cause and/or potential fixes. If it makes sense
for a run book to give advice for this, that's fine, but it should be clear
whether that advice is relevant for the initial response intended to stabilise
rather than fix.

### Uncertain Terms

Throughout the description above of the alarm creation process, I've mentioned a
handful of "uncertain" or "vague" terms. Specifically:

- "confidence" and "scepticism" towards/about an alarm
- a "regular", "frequent", or "infrequent" false positive frequency from an
  alarm
- "reliable" alarms

All of these generally refer to the same concept, which is that we need to reach
a level of confidence in any given alarm that when it sends a notification,
there truly is something to investigate. However, in a broad sense, these
concepts are impossible to define with specificity. That is, there is no
universal metric we can use to evaluate whether an alarm is "reliable". Each
alarm must have its own definitions of what an acceptable level of false
positives is. Certainly there are general thresholds and expectations we can
hold ourselves to. We should not accept daily false positives from an alarm, for
example. If such an alarm existed, it would need to be radically re-written to
solve this. While certain false positives may be unavoidable, it is still best
to weed out and prevent them, not least because it makes it easier to identify
the real incidents, but also because it makes it much less stressful for folks
triaging issues.

We must also keep in mind that inaccurate alarms may be _too quiet_ and not
alert when we want them to and that this can also introduce ambiguity,
especially if when it does alarm it does so with sporadic accuracy.

The long and short of it is, each alarm needs time, attention, and experience
from one or a handful of focused people for it to reach a state where we can be
sure that when it sends a notification, the vast majority of the time, it is
doing so for a good reason.

### Summary of new alarms

```{warning}
The periods and stats used in the example metric queries below are **not specific
recommendations**. During implementation, the implementer _must_ do further
research into each metric and decide what the appropriate starting period to
use will be and which statistical approach best interprets the metric to achieve
the goals of the alarm.
```

Each service should have a CloudWatch alarm that alerts if the Target Group
"UnHealthyHostCount" for each production service exceeds 0.

```json
{
  "metrics": [
    [
      "AWS/ApplicationELB",
      "UnHealthyHostCount",
      "TargetGroup",
      "targetgroup/production-api-tg/b2cc7a0e3cb2fd03",
      "LoadBalancer",
      "app/production-frontend-lb/91dbd299f89f6f14"
    ]
  ],
  "view": "timeSeries",
  "stacked": false,
  "region": "us-east-1",
  "stat": "Maximum",
  "period": 300
}
```

The following alerts will each require individual tuning and research to
determine appropriate thresholds, downtime, evaluation time periods, and
time-to-alarm.

Each service should have the following:

- Average response time anomaly
- Average response time over threshold
- p99 response time anomaly
- p99 response time over threshold
- Request count anomalous for time period
- 5xx count over time period over threshold
- 2xx count over time period under threshold

Each of these use metrics that are already used in the ECS service dashboards.
Implementers should reference the dashboard configuration for example queries
for these metrics.

All of these should alarm on "no data" except for 5xx response count which may
reach 0 without being an issue. If a service entirely stops responding then the
no data alarm condition on the total response count will be sufficient to
capture the event.

The anomaly-based alerts will almost certainly need downtime. In my experience,
anomaly detection is generally pretty flaky when services have significant
periods of low activity, which all of ours do. We should start without downtime
but anticipate the need for those alerts. Refer to
[CloudWatch documentation regarding "metric math functions" for examples of how to combine expressions based on date metrics to configure downtime for specific periods of time](https://aws.amazon.com/blogs/mt/enhance-cloudwatch-metrics-with-metric-math-functions/).

The response time anomaly should be configured only to alert when the response
time is outside the upper range of the anomaly, not below. Request count anomaly
should be configured to alert on both sides.

This list is not an exhaustive list of all possible useful alarms. It is a
starting point. We should and will add and remove

#### Route-specific alarms

I considered proposing that we start using Logs Insights to generate per-route
metrics for response time and status count. While I think this might be a good
idea in the future, there are cost considerations for using Logs Insights in
that way that I feel are beyond the scope of this baseline project. If we find
that the service level response time and status count alarms are not sufficient
to capture issues in particular features then we can start adding metrics for
those particular endpoints. I'm thinking of the thumbnails endpoint in
particular here, where endpoint specific monitoring of non-2xx responses and
response time would be highly valuable. If reviewers think we should go ahead
and develop those, the query to derive the data is relatively simple. At a
glance, I don't think the cost would be tremendous for the metric as our log
data each month is relatively low (<10 GB per month).

As I said, if reviewers think we should go ahead with this, I can develop the
query and add it to this implementation plan.

### Composite Alarms

Some of the alarms described above are likely to go off at the same time due to
their interrelated nature, like p99 and average response time anomalies for a
given route. This can be distressing. To prevent multiple, duplicative alarms
(without reducing alarm accuracy), we can use a
[composite alarm](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Create_Composite_Alarm.html)
to send an alert when any of the relevant alarms go off without sending multiple
if those related alarms go off in the same time period. If a composite alarm is
already in the alarm state, even if one of its dependencies newly enters the
alarm state after the first alert is sent, it won't send a new alarm.
Additionally, we can use composite alarms to only send alerts when multiple
relevant alarms going into the alarm state or only if a particular alarm is
alarming on its own (i.e., only if some other relevant alarm _isn't_ alarming).
Composite alarms allow us flexibility to decide when precisely we need to send a
new alert so that we can reduce noise.

## Outlined Steps

<!-- Describe the implementation step necessary for completion. -->

1. Create the monitoring modules for frontend and API production and move
   existing monitors into these
   - This includes moving the UptimeRobot configuration for each service as well
     as the database CPU usage monitors
   - Also create the new SNS topic for the unstable alerts' notification channel
   - Create the unhealthy host count alarm for API and frontend services
     - This serves as a proof of functionality for any infrastructure changes
       from the first step
1. Create each of the rest of the alarms. Each service will have distinct issues
   for response time alarms and response count alarms. This allows the chance
   for multiple people to work on alarm development and prevents alarms of
   potentially differing complexity to block each other.

## Parallelizable streams

<!-- What, if any, work within this plan can be parallelized? -->

After the first step, all alarms can be developed and iterated on in parallel.
Stabilisation and ongoing documentation work will happen in parallel and should
build on knowledge accrued during the first few steps.

## Dependencies

### Infrastructure

<!-- Describe any infrastructure that will need to be provisioned or modified. In particular, identify associated potential cost changes. -->

All of these alarms and alerts will be developed in the infrastructure
repository and codified in our Terraform configuration. These should not require
changes to the deployment/live environment infrastructure, however, and should
only create, configure, and iterate on CloudWatch alarms (or related things like
SNS topics).

### Tools & packages

<!-- Describe any tools or packages which this work might be dependent on. If multiple options are available, try to list as many as are reasonable with your own recommendation. -->

AWS CloudWatch, AWS SNS, and Terraform.

### Other projects or work

<!-- Note any projects this plan is dependent on. -->

None.

## Alternatives

<!-- Describe any alternatives considered and why they were not chosen or recommended. -->

As mentioned above, we've previously discussed similar work implemented using
prometheus and Grafana. We don't have time to stand up that infrastructure right
now, however, so we'll just rely on AWS's tools until we can use something else.

## Design

<!-- Note any design requirements for this plan. -->

None.

## Blockers

<!-- What hard blockers exist which might prevent further work on this project? -->

There are no blockers to this work.

## API version changes

<!-- Explore or mention any changes to the API versioning scheme. -->

There will be no changes to the API.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

Run books will be created for each monitor or group of related monitors to help
maintainers know how to respond when they alarm.

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

Remove anything that isn't working from the Terraform configuration and apply it
to remove it from our AWS account.

## Privacy

<!-- How does this approach protect users' privacy? -->

N/A

## Localization

<!-- Any translation or regional requirements? Any differing legal requirements based on user location? -->

N/A

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

The biggest risk is noisy, inaccurate alarms that cause more headaches than
solve problems.
