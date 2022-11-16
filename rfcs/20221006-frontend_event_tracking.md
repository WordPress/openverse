# RFC: Frontend event tracking

A proposal to emit frontend events based on user interactions and page visits.

## Reviewers

- [ ] @sarayourfriend
- [ ] @dhruvkb

## Rationale

Openverse developers have very little insight into the behaviors and interests of our users. We do not have any means of observing if they actually use the features we build in the intended manner, or at all.

There are multiple ways to address this, like conducting user surveys or test sessions. One other way we would like to gather this information is through analytics, specifically logging events performed by users. I'll share a full list of the events later in this proposal, but here are some examples:

- When a user clicks on a search result from the search results page
- When a user copies the attribution text

By collecting this data, anonymized and with user consent (through opt-out), we can make better decisions about what to build and increase the overall usefulness of Openverse.

### Why is this distinct from a general-purpose, cross-repo Analytics RFC?

This proposal only discusses front-end event collection. It does not discuss:

- Dashboards or tools for _analysing_ collected data
- The ideal data warehouse for our frontend events
- Whether to use a SaaS product or self-host analytics software

I suggest that our frontend events should be agnostic to any specific analytics platform. This means that our frontend events will be generalized to contain information we think is useful, and munged as necessary to conform to the needs of our analytics service. I see many benefits to doing this:

- It avoids vendor lock-in to a specific analytics platform
- It makes it much easier for users to audit exactly what values we're collecting, by avoiding heavy and mysterious 3rd-party SDKs
- Makes us less likely to be blocked by ad and script blocking software

There are many established conventions around frontend event collection. Using our own system should allow us to adopt most 3rd party platforms with without locking us in. A quick example use case is the Google Analytics alternative [Plausible.io](https://plausible.io/), which includes an [events API](https://plausible.io/docs/events-api). Plausible accepts the following simple request shape to capture a pageview, for example:

```shell
curl -i -X POST https://plausible.io/api/event \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.284' \
  -H 'X-Forwarded-For: 127.0.0.1' \
  -H 'Content-Type: application/json' \
  --data '{"name":"pageview","url":"http://dummy.site","domain":"dummy.site","screen_width":1666}'
```

There are many points in the code execution at which we could transform our custom events into ones supported by other platforms, if we need to. By adopting and implementing our own custom solution we can start collecting data as soon as possible without being blocked by time spent evaluating and implementing other analytics systems.

## The technical details

We should create a system for collecting events on the frontend. Each event will have a unique name, collect some default data about the enviroment (timestamp, referer, and so on) and can have an optional data payload containing string and numerical values.

### Sending events

These events will be sent as `POST` requests to a server route on the frontend, which will then route them to our desired analytics service. In the future it may make sense to move this server route to a standalone microservice but for now a [Nuxt server route](https://v3.nuxtjs.org/guide/directory-structure/server/#server-routes) should be sufficient to handle the analytics events. This endpoint is essentially a proxy between the frontend and our 'true' analytics service.

#### Privacy

Events will _only_ be collected and sent under the following conditions:

- An `ANALYTICS_ENABLED` feature flag is set to `true`.
- The user has not opted out of analytics by setting the `allowAnalytics` value in our UI cookie store to `false`.

Unless all conditions are met the `sendEvent` function will simply no-op.

A previous version of this proposal suggested honoring the `navigator.doNotTrack` browser method, but upon inspection this was deprecated in 2018 and is no longer advised.

This proposal will require the creation of a user settings page _or_ a analytics opt-out checkbox on the soon to be created `/privacy` page.

### Sample implementaton and event types

Below I've created a TypeScript type for all allowed anlytics events, and a simple function for sending events. This is where you can see a list of proposed events and their payloads, along with the default values which will be passed to all events.

```ts
// src/utils/events.ts

// This type is only for illustrative purposes and would be imported from elsewhere.
type MediaType = "image" | "audio" | "all";

/**
 * A list of all events allowed by our analytics server.
 */
type AnalyticsEvents = {
  /** A search performed by the user **/
  SUBMIT_SEARCH: {
    /** The media type being searched */
    mediaType: MediaType;
    /** The search term **/
    query: string;
  };
  /** The user navigates to a page. */
  VIEW_PAGE: {
    /** The title of the page being navigated to (window.document.title)  */
    title: string;
    /** The path of the previous page */
    previous: string;
    /** The path of the new page */
    next: string;
  };
  /** Whenever the user sets a filter  */
  APPLY_FILTER: {
    /** The name of the filter (not the user-facing element label) */
    key: string;
    /** The value of the filter */
    value: string | boolean;
    /** The media type being searched */
    mediaType: MediaType;
    /** The search term **/
    query: string;
  };
  /** Whenever a user changes the content type */
  CHANGE_CONTENT_TYPE: {
    /** The previously-set media type */
    previous: MediaType;
    /** The new media type */
    next: MediaType;
    /** The name of the Vue component used to switch content types. **/
    component: string;
  };
  /**
   * Whenever the user scrolls to the end of the results page.
   * Useful to evaluate how often users load more results or click
   * on the external sources dropdown.
   * */
  REACH_RESULT_END: {
    /** The media type being searched */
    mediaType: MediaType;
    /** The search term **/
    query: string;
  };
  /** Whenever the user clicks the load more button */
  LOAD_MORE_RESULTS: {
    /** The media type being searched */
    mediaType: MediaType;
    /** The search term **/
    query: string;
  };
  /** When a user opens the external sources popover. */
  VIEW_EXTERNAL_SOURCES: {
    /** The media type being searched */
    mediaType: MediaType;
    /** The search term **/
    query: string;
  };
  /** When the user chooses an external source from the dropdown of external sources */
  SELECT_EXTERNAL_SOURCE: {
    /** The name of the external source */
    name: string;
    /** The full URL of the source */
    link: string;
    /** The media type being searched */
    mediaType: MediaType;
    /** The search term **/
    query: string;
  };
  /**  The user opens the menu which lists pages. */
  OPEN_PAGES_MENU: {};
  /** Whenever the user selects a result from the search results page. */
  SELECT_SEARCH_RESULT: {
    /** If the result is a related result, provide the ID of the 'original' result */
    related: string | null;
    /** The media type being searched */
    mediaType: MediaType;
    /** The search term **/
    query: string;
  };
  GET_MEDIA: {};
  COPY_ATTRIBUTION: {};
  REPORT_MEDIA: {};
  AUDIO_INTERACTION: {};
  VISIT_LICENSE_PAGE: {};
  VISIT_CREATOR_LINK: {};
  /** The user right clicks a single image result, most likely to download it. **/
  RIGHT_CLICK_IMAGE: {};
  /** The user uses the 'back to search' link on a single result **/
  BACK_TO_SEARCH: {};
  /** The visibility of the filter sidebar on desktop is toggled **/
  TOGGLE_FILTERS: {};
};
type AnalyticsEventTypes = keyof AnalyticsEvents;

/**
 * Send an event to our analytics endpoint. Should be a no-op if the
 * user has opted-out of analytics.
 */
async function sendEvent<T extends AnalyticsEventTypes>(
  key: T,
  payload?: AnalyticsEvents[T]
): Promise<any> {
  /**
   * Actually send the event here, with some additional values:
   *
   * - Session ID
   * - Current path
   */
  // Default options are marked with *
  navigator.sendBeacon;
  const response = await fetch(`/api`, {
    method: "POST", // *GET, POST, PUT, DELETE, etc.
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return response.json(); // parses JSON response into native JavaScript objects
}
```

### Prior Art

[Snowplow](https://snowplow.io/) is "the world’s largest developer-first engine for collecting behavioral data". This is a heavy, complicated, and powerful analytics platform for [collecting](https://docs.snowplow.io/docs/collecting-data/collecting-from-own-applications/snowplow-tracker-protocol/example-requests/), [enriching](https://docs.snowplow.io/docs/enriching-your-data/available-enrichments/), and [modeling](https://docs.snowplow.io/docs/modeling-your-data/what-is-data-modeling/) data. This is about as robust as an open-source user behavior tracking platform can be.

[Plausible](https://plausible.io/) is a simple, lightweight, and self-hostable Google Analytics alternative. Our implementation here would be easily compatiable with Plausible's self-hosted or cloud offerings.

[Umami](https://umami.is/) is quite similar to Plausible. Their codebase contains [valuable discussions](https://github.com/umami-software/umami/pull/1272), for example why one might use `fetch` instead of `navigator.sendBeacon` to send analytics events even though the later was _designed_ for analytis use cases.
