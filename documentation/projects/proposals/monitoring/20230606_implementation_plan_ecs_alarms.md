# 2023-06-06 Implementation Plan: Baseline Alarms for ECS Services

**Author**: @sarayourfriend

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @krysal
- [x] @stacimc
- [x] @AetherUnbound

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/2344)
- [Milestone](https://github.com/WordPress/openverse/milestone/15)

```{admonition} Where's the project plan?
This implementation plan is not associated with a specific project plan.
It was requested as a result of various discussions between maintainers
reflecting on recent incidents. While there were some open issues to add
monitoring and alarms for specific things, without a cohesive implementation
plan to describe the general approach, these continued to fall to the
wayside. We need to establish a general approach for the initial set of alarms that can be built and iterated upon as the project evolves.
```

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

The Django API and Nuxt frontend will have a reasonable set of baseline alarms.
Each service will have a specific set of unstable alarms monitoring the
production environment that can be iterated on and later stabilised, once we
have had time to tweak the specific settings. **The initial implementation of
alarms will be a starting point.** The initial configuration cannot be treated
as final or sufficient and must be iterated on until the alarms can be
stabilised.

This implementation plan outlines the alarms themselves as well as a process for
stabilisation.

## Goals

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

This implementation plan has the following goals:

1. Establish a baseline approach for maintaining, configuring, and organising
   service monitoring tools through Terraform.
2. Propose an initial set of unstable alerts for our ECS services and describe
   their implementation details.
3. Describe a plan for stabilising new alarms that includes the creation and
   iteration of run books for each alarm.

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

We will continue to use the SNS Email alerts tool. This is an inexpensive and
easy way to send alerts to our notification channels.

We had discussed using EventBridge to identify unhealthy task instances, but the
Elastic Load Balancer (ELB) `UnHealthyHostCount` metric should be sufficient for
our initial implementation. Working with EventBridge is sufficiently different
from CloudWatch metrics such that it would significantly increase the complexity
of this implementation plan.

## Terms

This list of terms attempts to match AWS's own terminology. Personally I find
some of these confusing[^alarms-in-alarm], but in the interest of reducing the
cognitive overhead of switching between our documentation and CloudWatch, I've
chosen to use these terms anyway. Others may be somewhat colloquial or casual
jargon[^going-off], but I've opted to use them as well because they are commonly
used in the field and alternative turns of phrase are much clumsier.

[^alarms-in-alarm]:
    "Alarms in alarm" baffles me. I've made several editorial passes to this
    entire document to find the clearest way to describe this. Unfortunately,
    without completely deviating from CloudWatch's terminology, it's impossible
    to do so elegantly. I've tried to make the distinction by using the word
    "alert", but keep in mind that CloudWatch alarms can trigger actions other
    than alerts, so it is not a necessary relationship. We don't take advantage
    of that feature in this implementation plan, however, so it didn't feel
    worth further complication to accommodate.

[^going-off]:
    "Going off" may be colloquial, but in my experience it is extensively used
    in actual monitoring and observability practice when discussing monitors
    that are in "the bad state".

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
- "Notification channel": A place where alarms send alerts. e.g., a Slack or
  Matrix channel, an email address, or a tool like
  PagerDuty[^notification-channels]. These are configured via SNS.
- "Downtime": A known period of time when a given metric is unsuitable for
  alarming, typically due to daily variations in user behaviour.
  [See the section on downtime for examples and implementation details](#downtime).

[^notification-channels]:
    I am intentionally vague in this implementation plan about specific
    notification channels we use. Our current approach relies on tools to which
    access cannot be shared with anyone other than core maintainers due to
    limitations of the tools themselves. Future work might change this, as
    suggested in the
    [previous project proposal](/projects/proposals/monitoring/20220307-project_proposal.md),
    but for now we should continue to use the approach that works and is least
    expensive, both in terms of real dollar cost and in terms of work hours we
    need to put towards it.

```{note}
I use "alarm" throughout this document as a synonym for "alarms that send alerts".
For the purposes of this implementation plan, all alarms either trigger alert actions
themselves or are constituents in composite alarms that in turn trigger alert actions.
Where relevant, I have tried to clarify which alarms should trigger the alert actions.
```

## Overview

### Terraform Configuration

Alarms must be considered per-environment and per-service. With few exceptions,
it is highly unlikely that alarm configuration can be shared between
environments or services. In light of this, alarms will be configured in a new
monitoring namespace in the `next/modules` directory within the concrete modules
for services as internal submodules and will be named after the service and
environment they monitor. For example, Django API monitoring configuration would
go in `/modules/monitoring/production-api` and be instantiated in the production
root module in `api.tf`:

```terraform
module "api-monitoring" {
   source = "../modules/monitoring/production-api"

   # ... relevant inputs
}
```

New modules for each service/environment help to prevent an increase in root
module complexity. In order to consolidate monitoring configuration, the
existing `service-monitors` instances, which configure UptimeRobot, will be
moved into these new monitoring modules. `service-monitors` should be renamed at
this point to reflect the fact that it only configures UptimeRobot and not
"monitors in general". Likewise, existing RDS, Elasticache, and Elasticsearch
alarms present in the `next` root modules should also be moved.

```{note}
The CloudWatch Dashboards that collect all metrics for `next` root module services
will not be moved into these new modules. These are configured by the
`concrete/cloudwatch-dashboard` module which creates a dashboard for all services
in the root module. Keeping this configuration at the root module level allows us
to easily share documentation relevant for all services and simplify the configuration
as proposed in
[WordPress/openverse-infrastructure #472](https://github.com/WordPress/openverse-infrastructure/issues/472).
Splitting these could make sense in the future if significant differences in the needs
of services arise. That is outside the scope of this implementation plan, however.
```

We will need at least one new SNS topic for unstable alarms to send
notifications to a channel specific for unstable alarms. Separate notification
channels for unstable and stable alerts helps maintainers quickly distinguish
between the types of alerts they respond to. The new topic should be created in
the `singleton` module and follow the existing pattern of deferring management
to the production environment by using a data resource in staging. The existing
topics and subscription should also be moved into the singleton module.

### Stable vs Unstable Alarms and their Responses

As this project will add several new alarms, it is critical to understand the
distinction between stable and unstable alarms. In particular, all maintainers
interacting with the new tools must understand how to respond and determine
urgency for all alerts. Stability also refers to individual alarms and must be
considered in context of how they relate to the alerts that depend on them.
Alarms that comprise a composite alarm, for example, may require a different
approach to stability and accuracy if the resulting composite alarm is itself
sufficiently accurate.

Alarms should be considered unstable if they regularly produce false positives.
That is to say, if we incorrectly send an alert, and this happens on a regular
basis, then the alarm is unstable. Stable alarms, on the other hand, should have
virtually no incidents of false positives. If an alarm sends alerts to the
stable notification channel, it should be assumed that something is wrong that
needs to be addressed. In either case, the
[alert's corresponding run book](#run-books) should guide maintainers in
identifying severity so that they can complete the rest of the triaging process
outlined in the general incident response guide. It is important to note that
unstable alarms may produce a high number of false positives but should not be
treated with the blanket assumption that they are entirely inaccurate. As
described below, **run books must assist maintainers in quickly identifying
false positives**.

Because all the alarms proposed in this plan are new and for services that have
never had alarms of this nature, all of them will begin as unstable alarms. For
each alarm, until it is deemed stable (after we have observed for a sufficient
period of time that it does not create false positives), alarms will follow the
process outlined below for "unstable alarm response".

### Stabilising Alarms

All unstable alarms should eventually be stabilised or deleted. No alarm should
indefinitely stay in the "unstable" category. In order to increase and
distribute accountability for alarm stabilisation, each alarm will be assigned
to a maintainer who will be responsible for investigating false positive alerts
that come from the unstable alarm. Issues to create an alarm will remain open
until the alarm is stabilised to represent the ongoing work of stabilisation. As
with all other Openverse work, these issues can be reassigned as needed. MSR is
still responsible for triaging individual alerts. The default assignee to
investigate false alarms will be the maintainer assigned to the associated alarm
creation issue. If folks running MSR find that unstable alarms are too noisy, we
can change this approach for specific alarms or all alarms to have the
maintainer assigned to stabilising the alarm be responsible for responding to
the alerts. The maintainer assigned to stabilise the alarm is not solely
responsible for identifying areas of stability improvement. The development of
automated monitoring tools is still a collaborative effort. However, in addition
to ensuring false alarm investigation does not fall to the wayside, assigning a
maintainer also ensures that each alarm has someone who understands the
long-term context of the alarm, is aware of all of its previous behaviour, and
has paid consistent attention to it during stabilisation. Alarm maintainers
should have a similar relationship to their assigned alarms as project leads do
for projects. Once the alarm is stabilised, there will no longer be a specific
person assigned to it. Once maintainers reach a high level of confidence that
the alarm will not regularly cause false positives, the alarm should be
stabilised, with relevant run books updated by the maintainer to reflect the
fact. At this point, the alarm's maintainer will be unassigned. To summarise the
overall process:

1. Propose a new alarm based on metric observation
2. Implement the unstable version of the alarm and create the initial run book
   and link it from the notification for the alarm
3. Evaluate the new alarm over time to ensure correctness
4. Iterate on the severity identification guide for alerts from the alarm based
   on experience evaluating the unstable alarm
5. Stabilise the alarm by updating the run book and sending alerts to the stable
   channel
   - The run book should be updated to note:
     - When the alarm was stabilised
     - Consolidate false positive advice or anything else that can be simplified
       now that we have a deeper understanding of the alarm
   - The issue for the alarm will be closed as completed

### Run Books

Alert run books document the process for understanding a particular alert from
one or many alarms. Alert run books are not replacements for the general
incident response plan and maintainers must defer to the general process for
incidence response. The primary responsibility of the run book is to help
maintainers identify the severity of an issue and identify false positives.
While an alarm is still unstable, the run book also serves to document
historical information relevant to false positive identification and potential
changes to the alarm configuration that may help the alarm reach stability.
Alert run books should also document downtime.

Every notification sent by an alarm must include a link to a run book.

Run books are critical to alarm development because they document and share the
knowledge of metric interpretation with everyone responding to alerts. Some
alarms may share similar or exactly the same details or instructions. In those
cases, we can develop documents that are linked to via individual alert run
books. Even if every detail is shared between two separate alarms, each alarm
must still have its own run book to serve as a space to encourage alarm-specific
documentation. An alarm will naturally have few details in its run book to begin
with, but it should expand over time as maintainers' experience with each alarm
grows.

To clarify: alert run books must help identify severity and false positives and
may document remediation avenues but should never supersede the general
incidence response plan.

```{tip}
Run books are for _alerts_, not alarms. Alerts inform us of relevant alarm
states. Some alarms may go off for multiple states. For example, anomaly
detection may use the same alarm to notify when a metric is too high or too low.
Each is a separate "alert" and may require separate information to identify
severity. Additional consideration may be necessary for alerts from composite
alarms. These may require manually checking multiple alarms to help identify
severity. Keeping this in mind helps us focus each run book as much as
possible so that responders have the most accessible information at any time.
```

Run books must include the following:

- Stability: whether the alert is considered stable or unstable
- The run book maintainer's GitHub handle, if the alert is unstable
- Configured downtime
- A link to the alarm configuration and relevant metrics
- Instructions/guidelines to help identify the severity of the issue
- Additional helpful information for diagnosing particular problems beyond
  severity identification
- Links to related incident reports

#### Example Run Books

The following run book examples aim to give a concrete idea of what this will
look like:

```{toctree}
:titlesonly:
:glob:

run_book_samples/*
```

As demonstrated, run books should not include anything about the general process
of responding to incidents. For example, they do not need to include how to
triage the issue once you understand the severity nor who will be responsible
for responding to the incident. To reiterate a final time, the run book is a
supplement, not a replacement, to the general incident response plan.

#### Strategies for Stabilisation

- Identify downtime periods
- Use a more flexible/broader evaluation period for the metric query
- Use a composite alarm to compare the state of related alarms and only send an
  alert when a particular alarm configuration is present (e.g., only go off if a
  related alarm is not in alarm, etc.)

### Determining Alarm Accuracy

Throughout the description above of the alarm creation process, I've mentioned
the idea of alarm "accuracy". This refers primarily to an alarms rate of false
positives and false negatives. The ideal alarm never experiences either state,
but it's nearly impossible to achieve that level of perfection in the face of
changing user behaviour, new features, etc. Additionally, there is no universal
metric we can use to evaluate whether an alarm is "accurate". Each alarm must
define its own acceptable level of false alarms. Certainly there are general
thresholds and expectations we can hold ourselves to: we should not accept daily
false alarms from a stable alarm, for example. If such an alarm existed, it
would need to be radically re-written to solve this. While certain false alarms
may be unavoidable, it is still best to weed out and prevent them, not least
because it makes it easier to identify the real incidents, but also because it
makes it much less stressful for folks triaging issues.

Keep in mind that false negatives can be harder to identify, particularly
because you are rarely forced to confront a false negative. While false
negatives are not noisy, and an alarm that does not have false positives and
still catches _some_ problems is better than nothing, we should also consider
false negatives when determining an alarm's accuracy.

In summary, each alarm needs time, attention, and experience from one or a
handful of maintainers for it to reach a state where we can be sure that when it
sends a notification, the vast majority of the time, it is doing so for a good
reason, and that it doesn't keep quiet when a real issue is happening.

### Summary of new alarms

```{warning}
The periods and stats used in the example metric queries below are **not specific
recommendations**. During implementation, the implementer _must_ do further
research into each metric and decide what the appropriate starting period to
use will be and which statistical approach best interprets the metric to achieve
the goals of the alarm.
```

Each service should have a CloudWatch alarm that alerts if the Target Group
"UnHealthyHostCount" for any service exceeds 0.

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

```{important}
The `UnHealthyHostCount` alarm is the only alarm in this implementation plan
that should be implemented for staging. The reason we _can_ implement this for
staging and not the others is because this is the only metric that does not
rely on real user behaviour to create usable numbers we can depend on for
alert thresholds. All the other metrics used for alarms in this implementation
plan rely on having consistent historical and ongoing data that is generated
almost exclusively from real user interactions with our services.
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

We will group alarm creation by metric and service so that we can work to
stabilise alarms based on specific metrics at the same time. The
["Outlined Steps"](#outlined-steps) section lists each specific group of alarms.

Each of these use metrics that are already used in the ECS service dashboards.
Implementers should reference the dashboard configuration for example queries
for these metrics.

All of these should alarm on "no data" except for 5xx response count which may
reach 0 without being an issue. If a service entirely stops responding then the
no data alarm condition on the total response count will be sufficient to
capture the event. All "no data" alarms for these specific alarms must be
identified in the run books as the highest severity. No data either corresponds
to a full outage or broken metrics configurations. In the former case, the issue
must be resolved immediately. The latter is slightly lower priority (don't eat
dinner at your desk to fix it) but is still very high priority: if our services
fail while our monitoring is broken we won't know until users tell us about it
or we happen to notice on our own by chance.

The response time anomaly should be configured only to alert when the response
time is outside the upper range of the anomaly, not below (it's fine if things
are "too fast")[^too-fast]. Request count anomaly should be configured to alert
on both sides.

[^too-fast]:
    It does occur to me that response time could abnormally drop due to, for
    example, a general decrease in results from Elasticsearch that made the
    search route have mostly 0 work to do. However, I don't think response time
    is going to be an accurate way to catch that. It would be better to consider
    future
    [logs insights based metric alarms](#logs-insights-metrics-based-alarms) for
    such things.

This list is not an exhaustive list of all possible useful alarms. It is a
starting point. We should and will add and remove alarms over time.

#### Downtime

Some anomaly-based alerts may need downtime during low traffic periods. In my
experience, anomaly detection is generally pretty flaky when services have
significant periods of low activity, which all of ours do. We should start
without downtime but anticipate the need for those alerts. Refer to
[CloudWatch documentation regarding "metric math functions" for examples of how to combine expressions based on date metrics to configure downtime for specific periods of time](https://aws.amazon.com/blogs/mt/enhance-cloudwatch-metrics-with-metric-math-functions/).

The main alarm I suspect will need downtime is request count. With large
fluctuations it can be difficult to tell the difference between request count
falling due to increase error rate or due to the daily ebb and flow of usage. As
above, alarms should start without downtime. However, if an alarm configuration
makes sense for catching dips during high-traffic but causes false alarms during
low traffic, a downtime during daily or weekly low traffic periods is the best
way to prevent this. Occasionally separate alarms may be configured for these
periods of time, in which case each alarm would have downtime configured the
opposite of the other. In other words, it may be the case that we still want
anomaly detection for low traffic periods, but the configuration differs from
high traffic periods. In that case, we would create two separate alarms, with
the high traffic anomaly detection alarm configured with downtime during the
period of time that the low traffic anomaly alarm is on and vice-versa.

#### Logs Insights metrics based alarms

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

During the clarification round, reviewers agreed that Logs Insights metrics
based alarms are outside the scope of this implementation plan.
[I've created an issue to investigate the use of log parsing for route-specific timings on critical paths](https://github.com/WordPress/openverse/issues/2435).

### Composite Alarms

Some alarms described above are likely to go off at the same time due to their
interrelated nature, like p99 and average response time anomalies for a given
route. This can be distressing. To prevent multiple, duplicative alarms (without
reducing alarm accuracy), we can use a
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

I haven't made a specific recommendation to use composite alarms anywhere in
this implementation plan because it will be dependent on the observed behaviour
of the alarm over time. I want to avoid applying complicated conditions too
eagerly to the alarms if we can avoid it.

## Outlined Steps

<!-- Describe the implementation step necessary for completion. -->

1. Create the monitoring modules for frontend and API production and move
   existing alarms into these
   - This includes moving the UptimeRobot configuration for each service as well
     as the database and Redis monitors
   - Rename `service-monitors` to `service-uptime-robot` to clarify the module's
     purpose
   - Also create the new SNS topic for the unstable alerts' notification channel
   - Create the unhealthy host count alarm for production and staging services
     - This serves as a proof of functionality for any infrastructure changes
       from this first step
   - **This step is high priority as it unblocks further alarm creation**
1. Create each of the rest of the alarms.

Alarm creation will happen in groups based on service and related metrics for
the alarm. Each service will have an issue for each the response time (threshold
and anomaly) and response count alarms. In other words, each service will have 2
issues to implement the initial set of alarms for it:

- General API
  - Response time (threshold and anomaly)
  - Response count
- API Thumbnails
  - Response time (threshold and anomaly)
  - Response count
- Frontend
  - Response time (threshold and anomaly)
  - Response count

A note should be added to all issues created for this implementation plan that
it is easier to develop the metric queries and alarm configurations in the AWS
Dashboard and then export them into our Terraform configuration after the
initial iteration.

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

Run books will be created for each alarm or group of related alarm to help
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
solve problems. The implementation plan presents strategies to avoid this
becoming a long-term issue, if it happens at all.
