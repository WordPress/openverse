# 2023-03-07 Implementation Plan: Analytics backend and visualisation service

**Author**: @dhruvkb

This RFC deals with the backend of analytics, about how we record events sent
from the frontend and what we do with those events.

## Reviewers

- [x] @obulat
- [x] @sarayourfriend

## Rationale

As discussed in the [previous RFC](20221006-implementation_plan_frontend.md),
the frontend will emit analytic events for a number of interactions such as
clicking on buttons and navigating between pages. These events will be sent to
some endpoint where they will be recorded and then this recorded data can be
used to make decisions, draw visualisations etc.

There are numerous approaches to how the backend could be built, but they fall
primarily into two categories.

- Bespoke in-house implementation
- Off-the-shelf analytics framework

Considering the size of the team, needs of the project and volume of other
projects in the roadmap, an off-the-shelf solution makes more sense compared to
building something, even if rudimentary, from scratch. Such solutions are
numerous, so we must apply the following criteria to narrow down our list.

- Open source
- GDPR compliant
- Privacy respecting
- Simple (subjective)

This leaves us with only two main contenders, [Plausible](https://plausible.io/)
and [Umami](https://umami.is/). They're basically identical (just look at their
landing pages!) but have a few small differences.

| Criteria          | Umami           | Plausible              |
| ----------------- | --------------- | ---------------------- |
| URL               | [umami.is][1]   | [plausible.io][2]      |
| UI                | Clean           | Little dated           |
| Language          | JS              | Elixir                 |
| License           | MIT             | AGPL                   |
| GH stars          | 14.8k           | 14.1k                  |
| Integration       | [nuxt-umami][3] | [vue-plausible][4]     |
| Integration stars | 41              | 112                    |
| npm package       | No              | [plausible-tracker][5] |
| Cloud             | [Beta][6]       | [GA][7]                |

[1]: https://umami.is/
[2]: https://plausible.io/
[3]: https://github.com/ijkml/nuxt-umami/tree/main
[4]: https://github.com/moritzsternemann/vue-plausible
[5]: https://github.com/plausible/plausible-tracker
[6]: https://cloud.umami.is/login
[7]: https://plausible.io/login

Practically there is no reason to prefer one over the other, and it is very easy
for us to switch between them, if needed, thanks to our composable abstracting
the framework.

Considering this, we can go ahead with Plausible because

- Plausible has an NPM package that can be bundled with the app (whereas Umami
  needs a `<script>` tag).
- Plausible has a generally available cloud platform (whereas Umami's is in
  beta).
- there was some talk of it being used in other WordPress endeavours, so it
  makes more sense to use it.
- I've already done some experimental work with it, and it might save us the
  effort if that existing work were to be used.

## Production deployment

To start with we will be using the managed cloud instance of Plausible. This
will help us get up and running with analytics super quickly without having to
provision all the following services:

- a PostgreSQL database
- a Clickhouse database
- a Plausible instance

If we move to our own instance sometime in the future, we can
[export data](https://plausible.io/docs/export-stats) and migrate that to our
instance.

## Pricing

[Plausible pricing](https://plausible.io/#pricing) is based on number of events
/ month. Each page view and each custom event recorded counts towards the total
quota. The annual plan is 10x the monthly price i.e. 2 months free.

There is no cap on:

- data retention, so we can export it much even after lots of usage.
- number of users, so the entire team can be onboarded to see the dashboards.

Considering we have ~15 pages and ~20 custom event types, for a person that
looks through the entire site, we can estimate ~35 API hits. It can get pricey
quite fast. Even if we go with the cloud solution to get up and running quickly,
switching to self-hosted seems like the more economical option in the long term.

> We're operating a sustainable project funded solely by the fees that our
> subscribers pay us. And we donate 5% of our revenue.
>
> \- Plausible

On the other hand, if we're being generous, this can be thought of as investment
towards an open-source project that has doesn't have any other source of
funding.
