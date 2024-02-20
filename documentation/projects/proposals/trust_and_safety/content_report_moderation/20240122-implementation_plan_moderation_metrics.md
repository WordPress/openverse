# 2024-01-22 Implementation Plan: Moderation response times

**Author**: @dhruvkb

## Reviewers

- [ ] @AetherUnbound
- [ ] @stacimc

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/383)
- [Project Proposal](/projects/proposals/trust_and_safety/content_report_moderation/20230411-project_proposal_content_report_moderation.md#moderation-response-times-requirement-6-optional)

## Overview

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

This implementation plan deals with the development of various metrics, and
appropriate channels to surface them to the team, which will enable us to
monitor the performance and effectiveness of the content moderation pipeline.

These metrics can be helpful for visualising both the accuracy and volume of
incoming reports, and the speed and volume of our decisions about these reports.

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

The following views will be created as a realisation of this plan.

- Real-time dashboard in AWS CloudWatch
- Periodic/on-demand reports in Django Admin

Read on for more information about these views and the various metrics displayed
by each.

## Step-by-step plan

<!--
List the ordered steps of the plan in the form of imperative-tone issue titles.

The goal of this section is to give a high-level view of the order of implementation any relationships like
blockages or other dependencies that exist between steps of the plan. Link each step to the step description
in the following section.

If special deployments are required between steps, explicitly note them here. Additionally, highlight key
milestones like when a feature flag could be made available in a particular environment.
-->

```{mermaid}
flowchart TD
  subgraph b[Deferred metrics]
    4[Step 4: Update models] --- 5[Step 5: Implement deferred metrics] --- 6[Step 6: Surface in Django Admin]
  end
  subgraph a[Realtime metrics]
    2[Step 2: Implement real-time metrics] --- 3[Step 3: Surface in AWS CloudWatch]
  end
  1[Step 1: Identify and categorise metrics] --- 2 & 4
```

In these steps, step 1 should be done sufficiently by this plan itself.

Steps 2 and 4 need step 1 to be completed but can be done independently of each
other. Steps 3 and 5 depends on 2 and 4 respectively. Hence, there can be two
parallel tracks of work, one for the real time metrics and one for the deferred
metrics.

## Step details

<!--
Describe all of the implementation steps listed in the "step-by-step plan" in detail.

For each step description, ensure the heading includes an obvious reference to the step as described in the
"step-by-step plan" section above.
-->

```{caution}
This document shows code-samples but intended as a guide and not meant to be
used directly!
```

### Identify and categorise metrics

The metrics we aim to measure can be classified along two axes:

- Whether they measure user-submitted reports or moderator-generated decisions
- Whether they are real-time or deferred

The following metrics can be considered to begin with (we can always add more in
the future):

- Metrics about reports
  - number of reports (time-series, real-time)
    <!-- TODO: - per media type (time-series, real-time) -->
    - per violation (copyright, sensitive, other)
  - most reported creator/source/provider (deferred)
  - accuracy of reports (deferred)
  - duplication in reports (deferred)
- Metrics about decisions
  - number of decisions (time-series, real-time)
  - time to decision (deferred)
    - average
    - P99

The real-time metrics will be plotted as a time-series on a visual dashboard.
They can be used to observe trends and spikes in reports (which is useful to
understand usage and detect abuse of our reporting mechanisms) and in decisions
(which is useful to know how our decision volume compares to reporting volume
and when we need to scale our moderation resources).

The deferred metrics are computed periodically from our database. They can be
used to build reports that can be presented inside Django's admin interface
(which are useful to identify the sources, providers and creators that have a
lot of sensitive content and need bulk moderation). Having them in Django Admin
brings them closer to where the moderation is being performed.

### Implement real-time metrics

Real-time metrics are implemented by emitting structured log lines from the
moderation pipeline, whenever one of the following event occurs.

- report created
- report confirmed
- report rejected
- report deduplicated
- decision created

The log line must contain a JSON that matches this type definition.

```typescript
interface ReportMessage {
  message_type: "ModerationReport"
  event_type: "created" | "confirmed" | "rejected" | "deduplicated"
  media_type: "image" | "audio"
}
```

```typescript
interface DecisionMessage {
  message_type: "ModerationDecision"
  event_type: "created"
  action_type: "confirmed" | "rejected" | "deduplicated" | "deindexed"
  media_type: "image" | "audio"
}
```

Note that a deindexing decision also implicitly confirms the report. So a report
message with `confirmed` event-type should be emitted for every decision message
with a `deindexed` action-type.

This logging can be abstracted into a specific utility module in the API. These
utilities must be invoked from the `save` method on the Report and Decision
models. This will ensure that these events are logged regardless of whether
moderation happens via a view (like the admin site) or via a console interface
(like a management command).

### Surface in AWS CloudWatch

Real-time metrics will be delivered to CloudWatch via Logs Insights. We can then
create a dashboard in CloudWatch to visualise these metrics.

Here is a sample Logs Insights query that represents the volume of reports and
our various decisions.

```text
fields @timestamp, message_type, event_type
| filter message_type like "ModerationReport"
| stats
    sum(case when event_type = 'created' then 1 else 0 end) as createdCount,
    sum(case when event_type != 'created' then 1 else 0 end) as moderatedCount,
    sum(case when event_type = 'confirmed' then 1 else 0 end) as confirmedCount,
    sum(case when event_type = 'rejected' then 1 else 0 end) as rejectedCount,
    sum(case when event_type = 'deduplicated' then 1 else 0 end) as duplicateCount,
  by bin(5m)
| sort @timestamp desc
```

```text
fields @timestamp, message_type, event_type
| filter message_type like "ModerationDecision"
| stats
    sum(case when event_type = 'created' then 1 else 0 end) as createdCount,
    sum(case when action_type = 'confirmed' then 1 else 0 end) as confirmedCount,
    sum(case when action_type = 'rejected' then 1 else 0 end) as rejectedCount,
    sum(case when action_type = 'deduplicated' then 1 else 0 end) as duplicateCount,
    sum(case when action_type = 'deindexed' then 1 else 0 end) as deindexedCount,
  by bin(5m)
| sort @timestamp desc
```

This query can be used to create a line chart that shows the volume of reports
and our various decisions over time. Similar queries can be used to create
charts for other metrics. Ultimately a dashboard can be put together in
CloudWatch, that tracks all relevant metrics.

This dashboard will also be tracked in the infrastructure repo for backup and
restoration purposes.

### Implement deferred metrics

Deferred metrics are those that are computed periodically or on-demand from the
data in our database. These metrics can be computed using the Django ORM when
triggered using a management command and their results can be cached.

Here is how these deferred metrics can be calculated. Assume `Report`,
`Decision` and `Media` here refer to image and audio models respectively. This
example uses [package `tailslide`](https://github.com/ankane/tailslide) but a
fairly basic aggregator could be implemented by us if needed.

```python
from tailslide import Percentile
from django.db.models import Avg, Count, F
from api.models import Report, Decision, Media
from datetime import timedelta

# 1. Report Accuracy
total_reports = Report.objects.count()
confirmed_reports = Report.objects.filter(decision__action='confirmed').count()
report_accuracy = (confirmed_reports / total_reports) * 100 if total_reports else 0

# 2. Report Duplication
duplicate_reports = Report.objects.filter(decision__action='deduplicated').count()
report_duplication = (duplicate_reports / total_reports) * 100 if total_reports else 0

# 3. Most Reported Items
most_reported_media = Report.objects.values('media_id').annotate(report_count=Count('id')).order_by('-report_count').first()
most_reported_creator = Report.objects.values('media__creator').annotate(report_count=Count('id')).order_by('-report_count').first()
most_reported_source = Report.objects.values('media__source').annotate(report_count=Count('id')).order_by('-report_count').first()

# 4. Average and P99 Time to Decision
time_differences = Report.objects.annotate(
  decision_time=Avg(F('decision__created_on') - F('created_on'))
).values_list('decision_time', flat=True)

average_decision_time = sum(time_differences, timedelta()) / len(time_differences) if time_differences else timedelta()
p99_decision_time = Report.objects.annotate(
  decision_time=F('decision__created_on') - F('created_on')
).aggregate(
  percentile_99=Percentile('decision_time', 0.99)
)['percentile_99']
```

### Surface in Django Admin

The admin site supports both adding
[custom views](https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#adding-views-to-admin-sites)
and
[overriding/extending existing templates](https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#overriding-admin-templates).

These approaches can be coupled together for a good experience in displaying
these metrics to the moderators.

The precise design of how these metrics will be rendered will depend on the UI
of the moderation views as implemented when the previous IP is realised.

## Dependencies

This project should introduce no new dependencies as this builds on top of our
existing technology stack.

### Infrastructure

We already use Logs Insights, CloudWatch and Django Admin in our stack and, more
specifically, in the moderation pipeline.

### Other projects or work

This project depends on our implementation of the moderation workflow. By having
this implementation plan prepared we can design moderation workflow that
accounts from metrics and analytics from the outset and not as an afterthought.

## Alternatives

<!-- Describe any alternatives considered and why they were not chosen or recommended. -->

For the real-time metrics, as an alternative to logging that's parsed by Logs
Insights, we can also use an SDK like Boto to
[put metric data](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch/client/put_metric_data.html)
or
[put_log_events](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs/client/put_log_events.html)
into CloudWatch. This approach was not preferred because we already have a
logging setup that goes to AWS and precedent for building with Logs Insights.
This approach would have caused a lot of API calls to CloudWatch to put each
event as it occurs.

For the deferred metrics, as an alternative to Django Admin, we can have an
endpoint that presents the information as JSON or as a web page. This approach
was not preferred because Django Admin lets us build on top of the existing
access control framework established by the
[Django Admin implementation plan](/projects/proposals/trust_and_safety/content_report_moderation/20231208-implementation_plan_django_admin_moderator_access.md).
That also puts the metrics closer to where the moderation is being performed and
enables moderators to draw inferences from them.

## Blockers

<!-- What hard blockers exist that prevent further work on this project? -->

The implementation of moderation metrics ultimately depends on the
implementation of the moderation pipeline first.

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

The project is purely additive with no migrations. Bugs or other problems in the
metrics implementation can be rolled back by deploying the known last good
version with no adverse consequences.

## Privacy

<!-- How does this approach protect users' privacy? -->

All metrics collected by us will be aggregates and will not contain any
information to identify a user or moderator at the individual level. Reports are
anonymous so there is no possibility of PII in the reports. Decisions are
associated with the maintainer that made them, so we will be careful to not make
any reads on `maintainer_id` for our metrics.

We cannot add metrics like moderator leaderboards such as the moderator with the
most reports moderated or the fastest response times.
