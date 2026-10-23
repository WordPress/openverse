# 2022-03-07 Project Proposal: Monitoring

**Author**: @sarayourfriend

Note: Because I had to spend a good deal of time sketching out how this stuff
works, I wrote a good deal of preliminary code. It's probably not perfect so
it's really only a starting point, but it at least gives a vision for how we
could do this.

## Reviewers

- [x] @zackkrida (Infrastructure sign off)
- [x] @AetherUnbound
- [x] @obulat

## Milestone

TBD

## Rationale

Production Openverse is deployed across several services, each with their own
unique parameters for optimal performance and stability. We have little to no
visibility into the performance of most of these services aside from Sentry.

- Airflow - Has some Slack alerting for DAG failures/successes and some built in
  things we can gather basic performance information from.
- API - Has Sentry error monitoring but zero performance monitoring.
- Nuxt - Has Sentry error monitoring but zero performance monitoring.
- Thumbnail proxy - Has zero monitoring
- Postgres - Has zero monitoring aside from some CloudWatch system metrics being
  tracked
- Elasticsearch - Same as Postgres as far as I'm aware

Without visibility into our various services stability and performance we have
few or even zero ways to know whether we're introducing performance or stability
degradations with new releases (nor whether we're improving things). If our
services go down, we'll learn this because a user or contributor notices and
lets the team know. This is not ideal.

As the production instances of the Openverse API start getting used for Jetpack
and even WordPress core integrations soon and in the near future we will likely
see a tremendous increase in traffic. Without visibility into our services we
will be significantly hindered when debugging production performance and
stability issues.

Without measuring _current_ performance, we can't make decisions about how to
improve performance that aren't couched in anything better than educated
guesses. This is not a situation we want to be in long term. We also have a
sense that our services are reasonably speedy at the moment, but we don't know
exactly how speedy or what kind of outliers exist. Sometimes we see the API slow
down to over 2 seconds per-request. How often does that happen? Is it a 99th
percentile or more like 60th (i.e., closer to the average experience).

## Purpose

This RFC proposes we introduce [Prometheus](https://prometheus.io) and
[Grafana](https://grafana.com/) to monitor our infrastructure. It also proposes
that we create a new RDS Postgres instance for Grafana.

Prometheus is a time series database with an advanced query language and the
ability to configure aggregate data transformations (for example, based on a
given metric you can also tell Prometheus to calculate a running mean of the
metric from over the last 5 minutes, or any other span of time). It includes
anomaly detection as well as integration with many tools you can use for
alerting like Slack, PagerDuty, or email. There are
[official and unofficial client libraries](https://prometheus.io/docs/instrumenting/clientlibs/)
for all the langauges we currently use or could conceivably use in the future
including Python, Node.js, Go, PHP, and JVM languages.

Grafana is a data visualization tool that supports building complex dashboards.
It has the ability to integrate with nearly any source of data you could
imagine, including our existing catalog and API databases. In the future we
could use it to monitor cataloging progress over time for example. It's a tool
good for many things in addition to visualizing metrics.

The Prometheus and Grafana services encompass the following key features that
are important for maintaining the health and stability of our services:

- Metrics gathering
- Dashboard creation for making it quick and easy to understand the current
  state of our service health
- Anomaly detection and alarming so that if things get weird, we'll know about
  it as soon as possible

Additionally, both are free software. Prometheus is Apache 2 licensed and
Grafana is AGPL-3.0. Both are actively developed in the open with heavy
community involvement. They are also both widely deployed with lots of blog
posts discussing configuration, use cases, and troubleshooting.

## Self-hosted vs. hosted

We will self-host and use a new Postgres RDS instance for Grafana.

To simplify the hosting situation, let's try to deploy this using ECS from the
beginning.

## What will we monitor

There are three key aspects of the application services I think we should
monitor, along with a slew of system level metrics that we should monitor as
well.

### System level metrics

- CPU
- RAM
- Storage
- Processes/threads

These would be gathered from Airflow, API, Thumbnail proxy, Postgres and Nuxt.
These metrics need to be retrieved from AWS. I _think_ that
[this page describes how to do that](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Agent-PrometheusEC2.html)
but AWS's language around this stuff is so cryptic to me I can't say with
confidence it's the right documentation page for it.

It would also be nice if we could integrate Cloudflare data into Grafana so that
our visualizations are all in one place. Cache hits and other relevant
information from Cloudflare would be excellent to monitor within our greater
monitoring stack.

### Application level metrics

These are _per service_ when available. The Thumbnail proxy and Postgres, for
example, may not be able to implement all or any of these.

- Overall requests per second
- Per-route requests per second
- Per-route timings per response code
- Per-route response code rate
- Overall response code rate
- DB transaction times
- DB transaction count
- DB query count
- External request count and times

## How we will gather metrics

`django-prometheus` exports Prometheus metrics from a Django app and covers all
the information we'd want, at least to start off with.

There is not a real equivalent for Nuxt so we'll have to write our own either
from scratch or based on the ones that already exist. It would be nice to do
this as a separate Nuxt module so that we can share it with the wider Nuxt
community as an actively maintained and used-in-production Prometheus exporter.

The rest of our services all have relevant exporters available, either official
ones or ones with massive community support. Those are covered in the
"Prometheus data integrations" section below.

## Monitoring

It's hard to get into specifics about this, but there are a some scenarios
up-front that we can anticipate wanting monitors for.

- Sustained periods of time (60 seconds?) where
  `count_req_total == count_5xx_total` or
  `count_req_total >= (count_5xx_total / threshold)`
  - Note, queries are rarely that intutive to write and have at least two moving
    parts that dictate how the alarm works, the query and then the alarm
    condition.
- Each view has a version of the above relative to request frequency. Views with
  lower overall requests per second will require longer windows of time before
  alerting. We could also configure something like
  `view_request_count > threshold && view_5xx_count == view_request_count` to
  filter out cases where only a small number of requests have occurred against a
  view that happened to fail; though this is risky. I think in those cases we'd
  not want an _alarm_ _per se_ but would still want to be closely monitoring
  these types of occurrences through some low-priority alert and active
  dashboard viewing.

Additionally, we'll eventually be able to incorporate anomaly monitors. Anomaly
monitoring boils down to determining whether there are any statistically
significant periods of time where any given metric is an unexpected standard
deviation away from seasonal-mean[^2] for the metric. For example, if we
normally mean 1200 2xx response codes per second, with a standard deviation of
100 and our 2xx response codes drop to 1000 per second for a sustained period of
time, then we'd want an alarm to be raised.

Note that those numbers above are _not_ realistic, they're just simpler for
explaining the concept. In reality an anomaly monitor takes a lot of tinkering
to get right and often need to be iterated on to prevent false alarms.
Additionally, I suspect our services see irregular levels of traffic so our
standard deviations for some metrics might be really wild and hard to figure out
a good solution for. If a metric is extremely consistent then alarming on
deviations as low as 1 standard deviation away from mean could make sense. For
irregular metrics we could have to go higher.

Generally, anomaly monitors have two main variables that need tweaking to get
right:

- How long before alarming; that is, how long should the metric be outside the
  expected trend before we consider it to be an anomaly?
- How far outside the trend; that is, how many standard deviations away from the
  center/mean does it need to be for us to consider it anomalous?

Our ability to fine tune monitors based on these two variables goes up with the
more traffic we have, simply because with more data you can create better
statistical trend models with which to define anomalous behavior against. If we
have views that get relatively few requests per second then it will be difficult
to create anomaly monitors for them and we'll have to rely on binary monitors
for them.

There are additional derived statistical information for each metric:
percentiles. In particular for view timing this would be a useful thing to keep
in mind. If the mean or median response time for a particular view is 300 ms,
that looks great. However, if the 95th percentile response time is 1500 ms, then
we've got a problem. Most users are experiencing good response times but there
are some outliers that are getting significantly worse experiences. Percentile
based metrics falling outside of 1 standard deviation from the mean should be
actionable and high-value tickets to address.

## Isolating the monitoring backend

I considered that it might be nice to isolate the monitoring backend integration
so that the various Openverse services didn't rely on any specific
implementation. This would be nice (especially for alternative deployments of
Openverse, which would be cool to be able to support) but is too heavy a lift
for us and given we can isolate the integrations via configuration and external
modules it wouldn't be worth our time at the moment.

## Relevant integrations

Here's the list of integrations we'll want to incorporate into Prometheus and
Grafana.

### Prometheus data integrations

These are for pulling metrics into Prometheus from various services. This would
all be in addition to writing and integration for Nuxt and deploying
`django-prometheus` for the API (Airflow should be automatically covered by the
exporter listed below).

- Elasticsearch exporter:
  https://github.com/prometheus-community/elasticsearch_exporter
- Postgres exporter: https://github.com/prometheus-community/postgres_exporter
- AWS ECS exporter: https://github.com/slok/ecs-exporter
- Cloudflare exporter: https://gitlab.com/gitlab-org/cloudflare_exporter
- AWS CloudWatch exporter: https://github.com/prometheus/cloudwatch_exporter
  - This one is interesting. I think we'd define system metrics to gather in
    CloudWatch and then export them into Prometheus. Hopefully this wouldn't
    incur additional costs to what we're already doing with CloudWatch.
- Alternative to the CloudWatch exporter is to implement the Node exporter:
  https://github.com/prometheus/node_exporter
  - This has the added benefit of being portable across cloud providers vs
    CloudWatch being AWS services only.
  - Does not cover ECS in an obvious way; could we run the node exporter in the
    container? Would that produce meaningful information?
- Additional alternative to CloudWatch exporter is EC2 exporter:
  https://github.com/jmal98/ec2-exporter
- Airflow exporter: https://github.com/epoch8/airflow-exporter

### Grafana alerting integrations

Grafana has built in alerting since v4.0. It works upstream from provider
alertmanagers, so if we wanted to consume alerting rules from Prometheus we
could build rules in Prometheus and then consume them in Grafana and alert on
them.

[Here is the list of Grafana "contact points" for alerting.](https://grafana.com/docs/grafana/latest/alerting/unified-alerting/contact-points/)
A contact point is the notification channels that Grafana can send alerts to.

The most relevant for our usage are probably Slack, Webhook, and Email.
Optionally we could incorporate PagerDuty depending on the team's tolerance and
how we decide to organize expectations around responding to alerts.

My preference is for us to primarily rely on email and in particular to use
email lists to allow individuals to subscribe/unsubscribe at will from alarm
streams and provide an easy historical public record of alarms. We could use
something like [GNU Mailman](https://list.org/) to
[host this ourselves](https://github.com/maxking/docker-mailman) using FARGATE.

Email also makes it easy to compartmentalize alarms per category, it makes it
easy for individuals to subscribe to specific streams of alarms by using
different email prefixes per category. For example, each service could have its
own mailing list.

We can also integrate Slack for good measure and have all alarms sent to the
relevant channels via Slack incoming Webhook. It's very easy to configure the
Slack integration.

The general purpose Webhook integration is useful for a future where we migrate
away from Slack to Matrix (should that ever happen).

#### Runbooks

Runbooks are the expected steps for addressing a particular alarm. As I
mentioned elsewhere, alarms should be actionable. If they're not actionable then
they're just noise and should be demoted to a warning until they're more
accurate (less false positives). The _actions_ you take for any given alarm are
directed by an alarm's accompanying runbook.

All alarms should have a relevant runbook linked in the alarm body. Ideally
these would just be flat Markdown files but it'd be best if they could be hosted
in the Openverse handbook on WordPress.org as well for redundancy and
accessibility.

### Grafana data sources

- Prometheus: https://grafana.com/docs/grafana/latest/datasources/prometheus/
- Elasticsearch:
  https://grafana.com/docs/grafana/latest/datasources/elasticsearch/
  - Note: not for visualizing system stats, those will come from Prometheus.
    This would be for querying the index. Totally optional.
- Postgres: https://grafana.com/docs/grafana/latest/datasources/postgres/
  - Just if we wanted to be able to visualize certain query results. Could
    eventually be relevant for general analytics.

## Configuration and infrastructure (local and cloud)

The discussion about Prometheus configuration and infrastructure go hand in
hand, primarily because so much of the configuration needs to directly reference
other pieces of infrastructure for the various integrations to work.

Prometheus works by scraping HTTP endpoints on services that provide a formatted
set of metrics data. Essentially services don't need to worry about whether
Prometheus is running or concern themselves with how long to wait between
sending batched event lists. Each service just writes to a file (or some other
storage) that is served to Prometheus over HTTP whenever it requests it.

That has some really nice properties in that each service doesn't need to worry
about what Prometheus is doing. We don't need to worry about it's tolerances for
getting new events, rate limits, handling bad requests or timeouts if Prometheus
is temporarily unavailable, anything like that. We (or rather the client
library) just write and serve the metric data in the appropriate format and
Prometheus handles the rest.

This does have the effect of centralizing a ton of decisions about how to
organize things directly into Prometheus's configuration. I don't know where we
would want to store this information necessarily. Ideally it'd be somewhere
central like our infrastructure repository so that we don't have to duplicate or
aggregate various configurations during deployments.

On the other hand, this massively complicates local development of the
monitoring infrastructure and leaves us with two options:

1. We can choose one of the existing repositories to put a docker-compose stack
   into that would spin up Prometheus and Grafana as needed for the entire local
   stack. The catalog, API, and frontend repositories would need to be
   configured such that that Prometheus stack is able to discover them on the
   local network.
2. We can place a `docker-compose.monitoring.yml` in the WordPress/openverse
   repository and optionally pull the file down when certain commands are run to
   set up monitoring for each individual piece of the stack.

The second one seems more complicated to me. For one, if you're running all
three repositories locally you'd end up with three separate Prometheus and
Grafana instances to manage and configure.

The first one also seems complicated but I believe it's also easier. Remember
that Prometheus is the source of truth for the configuration, so we wouldn't
have to spread out the knowledge about where Prometheus lives in all our
services. As long as our services are configured to serve Prometheus the
appropriate data on consistent HTTP endpoints, then any Prometheus instance
anywhere can consume them. That does mean that some configuration will be spread
in the other direction: that is, rather than storing information about
Prometheus in each service, each service's information will be stored in
Prometheus. This seems like an appropriate compromise.

I'm not sure where the best place to put the monitoring docker-compose is. I
think I'd like to propose putting it in WordPress/openverse under a `monitoring`
directory that would include the `docker-compose.yml` as well as documentation
about how to configure monitors, our own best practices, etc. It doesn't make
sense to me for us to just pick one of the three application repositories to put
it in. The monitoring stack also fits in with the "meta"/"overview" nature of
the WordPress/openverse repository.

The major difference between the production stack and the local stack will be
the lack of a dedicated Postgres instance locally. Grafana will happily run on
SQLite locally and there's no reason to complicate that for us locally
(especially because we already have several other Postgres instances running
locally elsewhere in the stack). We can follow the standard
`docker-compose.overrides.yml` pattern we have followed to make changes in our
stack between local and production. This will mostly involve passing environment
variables to Grafana and Prometheus to configure them for production.

Aside from service configuration, however, there is also the issue of how to
store our Prometheus query, alerting, and other configuations locally. Likewise
we need to address that for Grafana dashboards. For example, we don't want to
have to manually copy the configurations for our anomaly monitors from
production. Even if we develop these monitors in a live staging environment
(more on that in the section below on the monitor development workflow) we'll
still want to store those in code to have them committed to production, rather
than manually copying them to prod. As long as the code they're saved to is
accessible to the local monitoring stack, we should be able to seed the local
stack with the same base monitors and dashboards present in production.

### Local infrastructure recommendations

One of the goals I'd like to achieve with the local infrastructure is to make it
as easy as running `just monitor` and it spins up everything with tolerances for
services that aren't currently running locally. For example, if someone is
working primarily on developing frontend monitors, it would do no good for
Prometheus to be producing errors about not be able to reach a local API,
Airflow, image proxy, or Postgres instance. Same for someone working on the
catalog, they should have to deal with answers about the frontend not being
discoverable by Prometheus locally.

## Monitor development workflow

1. Log into the staging Prometheus and Grafana instances
2. Develop your monitors and dashboards
3. Export them from staging and save them into the appropriate
   `monitoring/configurations/{prometheus,grafana}` folder
   - For Grafana, you can save new dashboards in the
     `monitoring/grafana/dashboards` folder in the Grafana JSON format.
     Datasources should be configured in the
     `monitoring/grafana/provisioning/datasources/datasources.yml`. It is
     unnecessary to change the `dashboards/dashboards.yml` configuration as the
     proposed configuration automatically picks up new JSON files.
   - For Prometheus, make the necessary changes to the
     `prometheus.yml.template`, run `just mkpromconf [environment]`. Any rules
     (if we end up using them) can be places directly into the `rules.d` and
     they will be automatically picked up by Prometheus the next time it is
     restarted.
4. Run the local monitoring stack to ensure that the saved configurations in a
   brand new deployment match the expected configurations from staging.
   - This may require exercising the local service a bit to check that metrics
     appear as expected in the dashboards... can be difficult with small amounts
     of data though.
5. Deploy them to production via terraform or some other method to update the
   running Prometheus and Grafana instances with the latest configurations
   - Terraform has
     [providers for uploading dashboard configurations to Grafana](https://registry.terraform.io/providers/grafana/grafana/latest)
   - With Prometheus, generate the new configuration file per environment using
     `just mkpromconf [environment]` and upload the configuration to the
     environment then restart Prometheus.

## DevEx

I've added some new `just` recipes in the example code in this PR.

Grafana configurations are stored as JSON so I think they'd be linted by
prettier. They should be copy/paste exports anyway so we don't need to lint them
for correctness or even style technically.

Prometheus configurations can be linted by `promtool` using this pre-commit
repo: https://github.com/fortman/pre-commit-prometheus.

## Outstanding questions

### Authentication

Do we want to hide the metrics endpoint behind authentication? I don't really
see why we would other than to stop spamming (but we could throttle those
endpoints to match the prometheus scrape rate for example and it would prevent
anyone from doing too much damage).

I like the idea of having fully open Prometheus and Grafana dashboards that
don't require authentication to _explore_. Obviously we'd want to hide
administration inside of authentication but each Prometheus and Grafana handle
that on their own.

### Alerting

Do we want to use Prometheus for alerting or Grafana?

Pros for Prometheus:

- It is possible and potentially even trivial to provision alerts based on
  configuration files

Cons for Prometheus:

- It is much harder to configure and automatically provision changes to
  Prometheus's configuration
- The UI for building them does not exist so I'm not sure what the best way to
  write new rules is other than via yaml files which will be harder for folks to
  contribute to given we're not all full-time devops people with tons of time to
  learn how to do this without fiddling around with visual helper tools

Pros for Grafana:

- The UI for building them is nice

Cons for Grafana:

- There's no way to export or provision them so the only way to add rules is
  through the UI (there's no JSON version of the form either). Moving rules
  across environments would be hard... to be fair, developing rules with
  anything except production data is also very difficult (lots of guessing) so
  maybe this isn't a problem.

I'd rather use Grafana provided we back up the database of alert configurations.
If we do that then not having them in the code is hopefully less of a disaster.

It is possible to export _all_ of them via the rules API:
`http://grafana/api/ruler/grafana/api/v1/rules`. There's just no way to upload
that JSON blob directly. We could scrape the endpoint and back it up into the
code base for good measure and to further distribute the configuration.

### Updating configurations

#### Grafana

Grafana is configured to automatically detect new dashboards uploaded via JSON.
It needs a restart to add new datasources and notification channels via the
`provisioning` folder[^3].

There is currently no way to export or provision alerting rules.

#### Prometheus

Prometheus is configured via a single `prometheus.yml` file. I've created a
Python script that generatese the appropriate `prometheus.{environment}.yml`
file based on a `.conf` file using Python's `configparser` module. It's in the
contents of this PR.

## Overview of proposed changes

- Use the existing Grafana instance in production
- Use ECS to deploy the following services in production:
  - Prometheus
  - GNU Mailman
- Use a new, small RDS instance for Grafana's Postgres DB.
- Rely on Prometheus primarily as a metrics aggregator and time series database.
  Do not use it for rule and alarm configuration.
- Rely on Grafana for visbility and alarming upstream from Prometheus.
- Create separate alarm streams per service in Mailman and aggregate all alarms
  into a Slack channel for extra visibility and redundancy.
- Use `django-prometheus` library to add the Prometheus `/metrics` endpoint to
  the API
- Expose Grafana dashboards publicly _a la_
  [Wikimedia](https://grafana.wikimedia.org/?orgId=1) and other FOSS projects
- Create `@openverse/nuxt-module-prometheus` to create a pluggable Prometheus
  monitoring integration for Nuxt based on existing (but incomplete) projects
- Integrate Prometheus exporters for the rest of our services and infrastructure
- Deploy Runbooks for all alarms to the Openverse handbook on WordPress.org

## Implementation Plan

1. Merge the example local stack implementation from this PR and update any of
   the things we agree to change during the RFC period.
   - Additionally configure pre-commit linting for prometheus configurations
1. Add `django_prometheus` to the API to expose the `/metrics` endpoint consumed
   by Prometheus.
   - As part of this we need to figure out if we want to hide the metrics
     endpoint behind authentication. See `Outstanding questions/Authentication`
     above.
   - Configure Prometheus to be able to scrape the relevant environment's
     `/metrics` endpoint (base this off the local configuration)
   - Deploy the API and confirm that the metrics are able to be scraped at the
     new endpoint.
1. Create the same `/metrics` endpoint for Nuxt using the
   [Node.js client library](https://github.com/siimon/prom-client)
   - This will be more work as we'll have to write our own middlware for it.
   - There are some existing Nuxt Prometheus modules like
     [this one](https://github.com/franckaragao/nuxt-prometheus-module) but
     they're not maintained and far more basic than what we actually want to
     get. We could fork those and create our own
     `@openverse/nuxt-prometheus-module` or something with better defaults more
     akin to the level of visibility that the `django-prometheus` module
     provides for Django.
   - Configure Prometheus to be able to scrape the `/metrics` endpoint and
     update configurations for each environment.
1. Continue the above for each service.
1. Let metrics gather for around 3-6 weeks then begin identifying areas we can
   create our first alerts around. Once we reach that milestone, create issues
   for creating alarms and writing runbooks for them.

<hr />

[^0]:
    While not necessary, we may consider switching to asyncio Django for this
    reason, so we can fire event submission tasks without blocking the response.
    For example, in the middleware pseudo code above it would be nice to be able
    to send the response back before incrementing the view status count.
    Alternatively we could add Celery for this purpose as well.

[^1]:
    In Django we'll use the view name, the class or function name that handles
    the view. This should include the absolute module path to ensure
    disambiguation between views. In Nuxt there isn't the same concept, so we'll
    just need to rely on the path. Replace intermediate slashes with double
    underscores, (e.g., `/search/images` turns into `search__images`).

[^2]:
    The "seasonal-mean" is a mean that incorporates daily, weekly or monthly
    seasonality. For example, the mean Friday at 1200 UTC is treated as distinct
    from the mean on Saturday at 1200 UTC. Browsing activity changes during the
    week. Most services see reduced traffic over the weekends. I'm not sure if
    that'll be the case for Openverse but implementing this is usually "free"
    and comes with any standard

[^3]:
    This could be wrong but I couldn't find any other way to do it that didn't
    require a script that made HTTP requests. Even the grafana-cli isn't capable
    of re-evaluating the provisioning scripts.

## Appendices

### Appendix A: Relevant documentation

Below are links to relevant documentation in Prometheus and Grafana. Reviewing
these is not necessary for reviewing the RFC. I've included them to help
implementers have a good starting point for finding things as sometimes even
knowing what terms to search for can be a hurdle.

- Prometheus rules unit tests:
  https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/
- Prometheus metric types: https://prometheus.io/docs/concepts/metric_types/
- Prometheus anomaly detection:
  https://prometheus.io/blog/2015/06/18/practical-anomaly-detection/
- Prometheus query functions:
  https://prometheus.io/docs/prometheus/latest/querying/functions/
- Prometheus range vectors:
  https://prometheus.io/docs/prometheus/latest/querying/basics/#range-vector-selectors
- Prometheus naming best practices: https://prometheus.io/docs/practices/naming/
- Prometheus official and unofficial client libraries:
  https://prometheus.io/docs/instrumenting/clientlibs/
- Adding a datasource to Grafana:
  https://grafana.com/docs/grafana/latest/datasources/add-a-data-source/
- Grafana dashboard best practices:
  https://grafana.com/docs/grafana/latest/best-practices/best-practices-for-creating-dashboards/
- Histograms and heatmaps in Grafana:
  https://grafana.com/docs/grafana/latest/basics/intro-histograms/
- Grafana glossary (super helpful!):
  https://grafana.com/docs/grafana/latest/basics/glossary/

### Appendix B: Alternative technologies

The following alternatives were considered before landing on Prometheus and
Grafana.

#### Graphite with Grafana

[Graphite](https://graphiteapp.org/) is very easy to put metrics into and
integrates smoothly with Grafana. However, for every bit as easy as Graphite is
to put metrics into, it is also that difficult to create queries against.
Graphite does not hold your hand at all. It supports anomaly detection through
[additional services](https://github.com/etsy/skyline), but they're not actively
developed and configuring the anomaly detections requires relatively deep
knowledge about statistics that I don't think our team is necessarily prepared
to invest time into (nor do we have the existing knowledge here as far as I
know).

Graphite is also older than Prometheus and while it works really well, there's a
lot less current information about how to deploy and configure it. There's also
almost no support for languages outside of the core langauges supported by the
project including poor JavaScript support (which would make monitoring our Nuxt
service more difficult).

#### CloudWatch

[CloudWatch](https://docs.aws.amazon.com/cloudwatch/index.html) is AWS's
proprietary system and service monitoring tool. It supports the three key
features I listed above. It is also easy to deploy, literally just click a
button and AWS adds it to your account.

As long as you're comfortable with AWS IAM credentials management, it is also
easy to wire up the AWS SDK clients to the backend.

However, as it is a proprietary AWS offering, it is targeted at large enterprise
clients, most of whom have multiple teams dedicated to managing their
infrastructure. These teams are often staffed with engineers who are trained
specifically in AWS and will have enterprise level support accounts to lean on
to fill in knowledge gaps.

We don't have anyone on the team who has dedicated AWS knowledge.

AWS's documentation for CloudWatch is downright cryptic. There are decent
overviews about the _concepts_, but implementing new monitors in Python or
JavaScript might as well be esoteric knowledge. The libraries are extremely
low-level for what they're doing and require you to manage batched event
reporting by hand, something other client libraries for competing services like
Prometheu's clients or statsd for Graphite handle out of the box.

Additionally, it is a proprietary service. We would not be able to get our
metrics out of AWS and if we decided to move away from AWS this would be a huge
hurdle to overcome if we invest into it. Likewise, anyone else trying to deploy
Openverse anywhere other than AWS would have to do work to tear out the
CloudWatch stuff as there are no alternative backends for it the way there are
for S3. More on this below.

#### Other extremely low level monitoring tools

There are also some very low level
[Linux daemon based time-series databases](https://github.com/oetiker/rrdtool-1.x)
that are quite capable and can integrate with Grafana. However, they are all
very low level and mostly do not support all of the three features I listed
above.

#### DataDog

[DataDog](https://www.datadoghq.com/) is a SaaS offerring that runs an open
source stack mixed with some proprietary magic. Prometheus and Grafana together
very much resemble DataDog, even down to the UI.

DataDog is fantastic. But it also comes at a higher cost than self-hosted
Prometheus and Grafana. It is also ultimately a closed system. They provide ways
for getting your data out and the client libraries for sending events used are
the same (or very similar) to the ones for Graphite and Prometheus but it would
still put work on alternative Openverse instances to make significant changes to
the monitoring backend.

DataDog does have very good documentation and holds your hand a _lot_ when it
comes to setting up monitors and dashboards. If I had to choose a hosted
proprietary solution I'd go with DataDog over AWS. However, I would not choose
it over hosted Prometheus and Grafana if given the choice.

#### Solar Winds stack

Solar Winds also has their own
[server and application monitoring tool](https://www.solarwinds.com/server-application-monitor/use-cases).
It's meant to be easy to deploy and automatically configures itself for the
services you have running. I don't have any experience with this other than
having used it to monitor Tomcat services at a previous job. My impression is
that it's targeted mostly at large enterprise and government contracts rather
than projects like ours. The services themselves are also not free software,
though the SDKs that integrate with them are. Likewise, it doesn't seem to be a
very flexible offering; it would probably be difficult to integrate things like
monitoring a Nuxt service.

#### The ELK stack

The final alternative is the
[ELK stack](https://www.elastic.co/what-is/elk-stack). It's not exactly a 1:1
alternative to Prometheus and Grafana, though it could fulfill
[some](https://www.elastic.co/guide/en/kibana/current/xpack-ml-anomalies.html)
of the [same](https://www.elastic.co/kibana/) use cases. This is a strong
alternative that I hope reviewers of this RFC spend time considering. Read
through Elastic's documentation about it and see if it could make sense for us.
It could also be something that we implement down the road as a supplement to
Prometheus and Grafana. Or it can replace it altogether.
