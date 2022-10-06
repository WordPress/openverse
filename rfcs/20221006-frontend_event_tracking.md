# RFC: Frontend event tracking

A proposal to emit frontend events based on user interactions nd page visits, first as a no-op and then to a yet to be proposed analytics service.

## Reviewers

- [ ] @sarayourfriend
- [ ] @dhruvkb

## Rationale

Openverse developers have very little insight into the behaviors and interests of our users. We do not have any means of observing if they actually use the features we build in the intended manner, or at all.

There are multiple ways to address this, like conducting user surveys or test sessions. One other way we would like to gather this information is through analytics, specifically logging events performed by users. I'll share a full list of the proposed events later in this proposal, but here are some examples of when we would want to collect an event:

- When a user clicks on a search result from the search results page
- When a user copys the attribution text

By collecting this data, anonymized and with user consent (through opt-out), we can make better decisions about what to build and increase the overall usefulness of Openverse.
