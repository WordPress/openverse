# Implentation Plan: Frontend event tracking - 2022-10-06

A proposal to emit frontend events based on user interactions and page visits.

## Reviewers

- [x] @krysal - For API experience
- [x] @dhruvkb - For frontend and DX experience

## Rationale

Openverse contributors have very little insight into the behaviors and interests
of our users. We do not have any means of observing if they actually use the
features we build in the intended manner, or at all.

There are multiple ways to address this, like conducting user surveys or test
sessions. One other way we would like to gather this information is through
analytics, specifically logging events performed by users. I'll share a full
list of the events later in this proposal, but here are some examples:

- When a user clicks on a search result from the search results page
- When a user copies the attribution text

By collecting this data, anonymized and with user consent (through opt-out), we
can make better decisions about what to build and increase the overall
usefulness of Openverse.

### Why is this distinct from a general-purpose, cross-repo Analytics RFC?

This proposal only discusses front-end event collection. It does not discuss:

- Dashboards or tools for _analysing_ collected data
- The ideal data warehouse for our frontend events
- Whether to use a SaaS product or self-host analytics software

I suggest that our frontend events should be agnostic to any specific analytics
platform. This means that our frontend events will be generalized to contain
information we think is useful, and munged as necessary to conform to the needs
of our analytics service. I see many benefits to doing this:

- It avoids vendor lock-in to a specific analytics platform
- It makes it much easier for users to audit exactly what values we're
  collecting, by avoiding heavy and mysterious 3rd-party SDKs
- Makes us less likely to be blocked by ad and script blocking software

There are many established conventions around frontend event collection. Using
our own system should allow us to adopt most 3rd party platforms without locking
us in. A quick example use case is the Google Analytics alternative
[Plausible.io](https://plausible.io/), which includes an
[events API](https://plausible.io/docs/events-api). Plausible accepts the
following simple request shape to capture a pageview, for example:

```shell
curl -i -X POST https://plausible.io/api/event \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.284' \
  -H 'X-Forwarded-For: 127.0.0.1' \
  -H 'Content-Type: application/json' \
  --data '{"name":"pageview","url":"http://dummy.site","domain":"dummy.site","screen_width":1666}'
```

There are many points in the code execution at which we could transform our
custom events into ones supported by other platforms. By adopting and
implementing our own custom solution, we can start collecting data as soon as
possible without being blocked on time spent evaluating and implementing a full
analytics system.

## The technical details

We will create a system for collecting events on the frontend. Each event will
have a unique name, collect some default data about the enviroment (timestamp,
referer, and so on) and can have an optional data payload containing string and
numerical values. I'd like to limit the payload shape to strings and numbers to
keep it JSON serializable and simple. Allowing for complex nested objects might
prove too complex to query in the future. I think this is a reasonable
constraint but am open to alternatives.

### Sending events

These events will be sent as `POST` requests to a server route on the frontend,
which will then route them to our desired analytics service. In the future, it
may make sense to move this server route to a standalone microservice, but for
now a
[Nuxt server route](https://v3.nuxtjs.org/guide/directory-structure/server/#server-routes)
or
[Server Middleware](https://nuxtjs.org/docs/configuration-glossary/configuration-servermiddleware/)
(once we're updated to Nuxt 3), should be sufficient to handle the analytics
events. This endpoint is essentially a proxy between the frontend and our 'true'
analytics service that makes sure we're always sending events server-side.

#### Privacy

Events will _only_ be collected and sent under the following conditions:

- An `ANALYTICS_ENABLED` feature flag is set to `true`.
- The user has not opted out of analytics by setting the `allowAnalytics` value
  in our UI cookie store to `false`.

Unless all conditions are met the `sendEvent` function will simply no-op.

A previous version of this proposal suggested honoring the
`navigator.doNotTrack` browser method, but upon inspection this was deprecated
in 2018 and is no longer advised.

This proposal will require the creation of some new user interface elements to
toggle analytics tracking:

1. A small popup banner that shows up to users, which informs them that
   Openverse collects anonymized analytics information to make the service
   better. There are "dismiss" and "learn more" calls to action. "Learn more"
   directs users to:
2. An analytics opt-out checkbox on the `/privacy` page. We also add information
   describing our analytics collection, and link to the relevant code in our
   GitHub repository.

### Events

Below I've created a TypeScript type for all the proposed anlytics events, and a
simple function for sending events. For each event you'll see the payload
alongside the default values which will be passed to _all_ events.

```ts
// src/utils/events.ts

// This type is only for illustrative purposes and would be imported from elsewhere.
type SearchType = "image" | "audio" | "all"

/**
 * A list of all events allowed by our analytics server. For each event
 * there is a description and a series of questions the event can help
 * answer about our users and their behavior.
 */
type AnalyticsEvents = {
  /**
   * Description: A search performed by the user
   * Questions:
   *   - How many searches do we serve per day/month/year?
   *   - What are the most popular searches in Openverse?
   *   - Which media types are the most popular?
   *   - Do most users search from the homepage, or internal searchbar?
   */
  SUBMIT_SEARCH: {
    /** The media type being searched */
    mediaType: SearchType
    /** The search term */
    query: string
  }
  /** Description: The user navigates to a page.
   * Questions:
   *   - Which content pages are the most popular?
   *   - Are search result pages commonly shared?
   *   - If so, which are most popular?
   *   - What is the most common user path?
   */
  VIEW_PAGE: {
    /** The title of the page being navigated to (window.document.title)  */
    title: string
    /** The path of the previous page */
    previous: string
    /** The path of the new page */
    next: string
  }
  /**
   * Description: Whenever the user sets a filter
   * Questions:
   *  - Do most users filter their searches?
   *  - What % of users use filtering?
   *  - Which filters are most popular? Least popular?
   *  - Are any filters so commonly applied they should become defaults?
   */
  APPLY_FILTER: {
    /** The name of the filter (not the user-facing element label) */
    key: string
    /** The value of the filter  */
    value: string | boolean
    /** The media type being searched */
    mediaType: SearchType
    /** The search term */
    query: string
  }
  /**
   * Description: Whenever a user changes the content type
   * Questions:
   *   - Which content types are most popular?
   *   - Is there interest in the non-supported content types?
   *   - Do users switch content types? Where in their journeys?
   */
  CHANGE_CONTENT_TYPE: {
    /** The previously-set media type */
    previous: SearchType
    /** The new media type */
    next: SearchType
    /** The name of the Vue component used to switch content types. */
    component: string
  }
  /**
   * Description: Whenever the user scrolls to the end of the results page.
   * Useful to evaluate how often users load more results or click
   * on the external sources dropdown.
   *
   * This event is mainly used as part of a funnel leading to a
   * `LOAD_MORE` or `VIEW_EXTERNAL_SOURCES` event.
   *
   * Questions:
   *   - Do users use meta search after reaching the result end?
   *   - Do users find a result before reaching the end of the results?
   */
  REACH_RESULT_END: {
    /** The media type being searched */
    mediaType: SearchType
    /** The search term */
    query: string
    /** The current page of results the user is on. */
    resultPage: number
  }
  /**
   * Whenever a search results in less than a full page
   * of results or no results.
   *
   * Questions:
   *   - How often do searches provide limited or no results?
   *   - Do users visit external sources when results are insufficient?
   *   - What do users do after a search has no results?
   */
  INSUFFICIENT_RESULTS: {
    /** The media type being searched */
    mediaType: SearchType
    /** The search term */
    query: string
    /** The number of results returned */
    resultCount: number
  }
  /**
   * Description: Whenever the user clicks the load more button
   * Questions:
   *   - On what page do users typically find a result?
   *   - How often and how many pages of results do users load?
   *   - Can we experiment with the types of results / result rankings
   *     on certain pages, pages that users don't usually choose a result
   *     from anyway?
   */
  LOAD_MORE_RESULTS: {
    /** The media type being searched */
    mediaType: SearchType
    /** The search term */
    query: string
    /** The current page of results the user is on. */
    resultPage: number
  }
  /**
   * Description: When a user opens the external sources popover.
   * Questions:
   *   - How often do users use this feature?
   *   - Under what conditions to users use this feature? No results?
   *     Many results, but none they actually select?
   */
  VIEW_EXTERNAL_SOURCES: {
    /** The media type being searched */
    mediaType: SearchType
    /** The search term */
    query: string
    /** The current page of results the user is on. */
    resultPage: number
  }
  /**
   * Description: When the user chooses an external source from the dropdown of external sources
   * Questions:
   *   - Which external sources are most popular? This could drive inclusion in Openverse.
   *   - Are certain media types more popular externally?
   */
  SELECT_EXTERNAL_SOURCE: {
    /** The name of the external source */
    name: string
    /** The full URL of the source */
    url: string
    /** The media type being searched */
    mediaType: SearchType
    /** The search term */
    query: string
  }
  /**
   * Description: The user opens the menu which lists pages.
   * Questions:
   *   - How often is this menu used?
   *   - Is this menu visible enough?
   */
  OPEN_PAGES_MENU: {}
  /**
   * Description: The user clicks to a link outside of Openverse.
   * Questions:
   *   - What types of external content do users seek?
   *   - Are there external resources we should make more visible?
   *   - Is there content we might want to add to Openverse directly?
   */
  EXTERNAL_LINK_CLICK: {
    /** The url of the external link */
    url: string
    /**
     * The name of the Vue component used to switch content types.
     * @todo: We need to determine the best way of creating a string
     * representation of a vue component, which allows us to know
     * which ui element was clicked. Perhaps we could use unique data-test-ids
     * or another unique identifier for this?
     */
    component: string
  }
  /**
   * Description: Whenever the user selects a result from the search results page.
   * Questions:
   *   - Which results are most popular for given searches?
   *   - How often do searches lead to clicking a result?
   *   - Are there popular searches that do not result in result selection?
   */
  SELECT_SEARCH_RESULT: {
    /** The unique ID of the media */
    id: string
    /** If the result is a related result, provide the ID of the 'original' result */
    relatedTo: string | null
    /** The media type being searched */
    mediaType: SearchType
    /** The slug (not the prettified name) of the provider */
    provider: string
    /** The search term */
    query: string
  }
  /**
   * Description: The user clicks the CTA button to the external source to use the image
   * Questions:
   *   - How often do users go to the source after viewing a result?
   */
  GET_MEDIA: {
    /** The unique ID of the media */
    id: string
    /** The slug (not the prettified name) of the provider */
    provider: string
    /** The media type being searched */
    mediaType: SearchType
  }
  /**
   * Description: The user clicks one of the buttons to copy the media attribution
   * Questions:
   *   - How often do users use our attribution tool?
   *   - Which format is the most popular?
   */
  COPY_ATTRIBUTION: {
    /** The unique ID of the media */
    id: string
    /** The format of the copied attribution */
    format: "plain" | "rich" | "html"
    /** The media type being searched */
    mediaType: SearchType
  }
  /**
   * Description: The user reports a piece of media through our form
   * Questions:
   *   - How often do we get reports?
   *   - Which types of reports are more common?
   *   - Do we see an uptick in reports when a certain provider
   *     is added/updated/refreshed?
   */
  REPORT_MEDIA: {
    /** The unique ID of the media */
    id: string
    /** The slug (not the prettified name) of the provider */
    provider: string
    /** The media type being searched */
    mediaType: SearchType
  }
  /** Description: The user plays, pauses, or seeks an audio track.
   * @todo: This potentially requires throttling.
   *
   * Questions:
   *   - Do users interact with media frequently?
   *   - Is it more common to playback audio on single results
   *     or search pages?
   *   - How many audio plays do we get?
   */
  AUDIO_INTERACTION: {
    /** The unique ID of the media */
    id: string
    event: "seek" | "play" | "pause"
    /** The slug (not the prettified name) of the provider */
    provider: string
    /** The name of the Vue component used on the interaction, e.g. the global or main player. */
    component: string
  }
  /**
   * Description: The user visits a CC license description page on CC.org
   * Questions:
   *   - How often are external licenses viewed?
   */
  VISIT_LICENSE_PAGE: {
    /** The slug of the license the user clicked on */
    license: string
  }
  /**
   * Description: The user visits a creator's link in the single result UI
   * Questions:
   *   - Are creator links clicked much? Does Openverse increase visibility
   *     of included creator's profiles?
   */
  VISIT_CREATOR_LINK: {
    /** The unique ID of the media */
    id: string
    /** The permalink to the creator's profile */
    url: string
  }
  /**
   * Description: The user right clicks a single image result, most likely to download it.
   * Questions:
   *   - Do users right click images often? Does this suggest downloading them directly,
   *     when not paired with a `GET_MEDIA` event?
   */
  RIGHT_CLICK_IMAGE: {
    /** The unique ID of the media */
    id: string
    /** The media type being searched */
    mediaType: SearchType
  }
  /**
   * Description: The user uses the 'back to search' link on a single result
   * Questions:
   *   - Are these links used much? Are they necessary?
   */
  BACK_TO_SEARCH: {
    /** The unique ID of the media */
    id: string
    /** The media type being searched */
    mediaType: SearchType
  }
  /**
   * Description: The visibility of the filter sidebar on desktop is toggled
   * Questions:
   *   - Do a majority users prefer the sidebar visible or hidden?
   */
  TOGGLE_FILTERS: {
    /** The media type being searched */
    mediaType: SearchType
    /** The state of the filter sidebar after the user interaction. */
    state: "open" | "closed"
  }
}
type AnalyticsEventTypes = keyof AnalyticsEvents
```

## Default values and sample implementation of event sending code

This is a sample implementation of what our event sending code can look like.
With the power of TypeScript we can make sure to only send valid events with
proper payloads.

Pay careful attention to the `defaults` object. This is the default payload that
will send with every single event. These are properties that are universally
useful to any event, like the current page the user is on, and also properties
that allow for tracking unique user sessions.

```ts
/**
 * Send an event to our analytics endpoint. Should be a no-op
 * if the user has opted-out of analytics.
 */
async function sendEvent<T extends AnalyticsEventTypes>(
  key: T,
  payload?: AnalyticsEvents[T]
): Promise<any> {
  /**
   * The default values to send with every analytics event.
   * Any sensitive or personally-identifying information
   * sent here is *not* stored, rather used to derive
   * anonymized session, device, and browser statistics.
   *
   * The items not stored directly include: width, height,
   * ipAddress, and userAgent
   */
  const defaults = {
    timestamp: Date.now(),
    path: window.location.pathname,
    referrer: document.referrer || null,
    language: i18n.locale, // collected from the global Nuxt i18n object
    // These fields are not stored directly, rather used to derive anonymized values
    width: window.innerWidth, // The width of the user's device
    height: window.innerHeight, // The height of the user's device
    ipAddress: "", // Should be read from the X-Forwarded-For header server-side, will need to be stored securely during the user's session
    userAgent: navigator.userAgent,
  }
  /**
   * Actually send the event here, with some additional values.
   * I would have prefered to use `navigator.sendBeacon` here
   * but it is blocked by most ad blockers.
   *
   * We might not want to call our api route "analytics" to
   * further avoid blocking by adblockers, but I'll use that
   * name for clarity here.
   */
  const response = await fetch(`/analytics`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...defaults, ...payload }),
  })
}
```

### Implementation Plan

- [ ] Create "Event Tracking" GitHub milestone in the frontend repository
- [ ] Design: design a privacy and analytics opt-out checkbox on the Privacy
      page. Also a pop-up banner to be shown to users letting them know
      Openverse uses analytics (can use the existing audio notice for this)
- [ ] Create the `ANALYTICS_ENABLED` feature flag which defaults to
      `off`/`false`.
- [ ] Create a PR which adds an `allowAnalytics` value to our UI cookie store;
      implements the checkbox on the privacy page; and shows a 'Openverse
      collects analytics information...' banner to first-time (new session)
      users.
- [ ] Create an issue for the creation of the `sendEvent` function and the api
      route to post analytics events to. The api route will post events to an
      `ANALYTICS_ENDPOINT` environment variable. If that variable is unset
      and/or the `ANALYTICS_ENABLED` flag is off, the analytics events will not
      send.
- [ ] Create each event in the sample implementation. Each event will need a
      detailed description of the payload and trigger (the actual user
      interaction that fires off the event). Events will need to account for
      accessibility concerns. Will keyboard users' actions trigger the events
      the same way as mouse users?
- [ ] Future: Create a PR to turn `ANALYTICS_ENABLED` to `on`/`true`, set the
      `ANALYTICS_ENDPOINT` environment variable, and do any munging of data
      necessary for the decided on analytics service.

## Concerns / Pitfalls

- Related to content safety, this is an area where we are surfacing user
  information in the form of text, or even malicious URLs, to Openverse
  developers. These searches could include explicit or sensitive material. We're
  also potentially surfacing explicit image results to anyone working with this
  data.
- We're building something here that is commonly drop-in when 3rd party tools
  are used. At least for page views; custom events still require custom work. Is
  this a poor use of time?
- I think it's great to build this decoupled from a specific back-end, but if we
  never actually implement a backend this would largely be a wasted effort.

### Prior Art

[Snowplow](https://snowplow.io/) is "the world’s largest developer-first engine
for collecting behavioral data". This is a heavy, complicated, and powerful
analytics platform for
[collecting](https://docs.snowplow.io/docs/collecting-data/collecting-from-own-applications/snowplow-tracker-protocol/example-requests/),
[enriching](https://docs.snowplow.io/docs/enriching-your-data/available-enrichments/),
and
[modeling](https://docs.snowplow.io/docs/modeling-your-data/what-is-data-modeling/)
data. This is about as robust as an open-source user behavior tracking platform
can be.

[Plausible](https://plausible.io/) is a simple, lightweight, and self-hostable
Google Analytics alternative. Our implementation here would be easily
compatiable with Plausible's self-hosted or cloud offerings.

[Umami](https://umami.is/) is quite similar to Plausible. Their codebase
contains
[valuable discussions](https://github.com/umami-software/umami/pull/1272), for
example why one might use `fetch` instead of `navigator.sendBeacon` to send
analytics events even though the later was _designed_ for analytis use cases.
