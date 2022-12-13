# RFC: Frontend event tracking

A proposal to emit frontend events based on user interactions and page visits.

## Reviewers

- [ ] @krysal - For API experience
- [ ] @dhruvkb - For frontend and DX experience

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

There are many established conventions around frontend event collection. Using our own system should allow us to adopt most 3rd party platforms without locking us in. A quick example use case is the Google Analytics alternative [Plausible.io](https://plausible.io/), which includes an [events API](https://plausible.io/docs/events-api). Plausible accepts the following simple request shape to capture a pageview, for example:

```shell
curl -i -X POST https://plausible.io/api/event \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.284' \
  -H 'X-Forwarded-For: 127.0.0.1' \
  -H 'Content-Type: application/json' \
  --data '{"name":"pageview","url":"http://dummy.site","domain":"dummy.site","screen_width":1666}'
```

There are many points in the code execution at which we could transform our custom events into ones supported by other platforms. By adopting and implementing our own custom solution, we can start collecting data as soon as possible without being blocked on time spent evaluating and implementing a full analytics system.

## The technical details

We will create a system for collecting events on the frontend. Each event will have a unique name, collect some default data about the enviroment (timestamp, referer, and so on) and can have an optional data payload containing string and numerical values. I'd like to limit the payload shape to strings and numbers to keep it JSON serializable and simple. Allowing for complex nested objects might prove too complex to query in the future. I think this is a reasonable constraint but am open to alternatives.

### Sending events

These events will be sent as `POST` requests to a server route on the frontend, which will then route them to our desired analytics service. In the future, it may make sense to move this server route to a standalone microservice, but for now a [Nuxt server route](https://v3.nuxtjs.org/guide/directory-structure/server/#server-routes) or [Server Middleware](https://nuxtjs.org/docs/configuration-glossary/configuration-servermiddleware/) (once we're updated to Nuxt 3), should be sufficient to handle the analytics events. This endpoint is essentially a proxy between the frontend and our 'true' analytics service that makes sure we're always sending events server-side.

#### Privacy

Events will _only_ be collected and sent under the following conditions:

- An `ANALYTICS_ENABLED` feature flag is set to `true`.
- The user has not opted out of analytics by setting the `allowAnalytics` value in our UI cookie store to `false`.

Unless all conditions are met the `sendEvent` function will simply no-op.

A previous version of this proposal suggested honoring the `navigator.doNotTrack` browser method, but upon inspection this was deprecated in 2018 and is no longer advised.

This proposal will require the creation of a user settings page _or_ an analytics opt-out checkbox on the `/privacy` page.

### Sample implementaton and event types

Below I've created a TypeScript type for all the proposed anlytics events, and a simple function for sending events. For each event you'll see the payload alongside the default values which will be passed to _all_ events.

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
  /**
   * Whenever a search results in less than a full page
   * of results or no results.
   */
  INSUFFICIENT_RESULTS: {
    /** The media type being searched */
    mediaType: MediaType;
    /** The search term **/
    query: string;
    /** The number of results returned **/
    resultCount: number;
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
    url: string;
    /** The media type being searched */
    mediaType: MediaType;
    /** The search term **/
    query: string;
  };
  /**  The user opens the menu which lists pages. */
  OPEN_PAGES_MENU: {};
  EXTERNAL_LINK_CLICK: {
    /** The url of the external link */
    url: string;
    /**
     * The name of the Vue component used to switch content types.
     * @todo: We need to determine the best way of creating a string
     * representation of a vue component, which allows us to know
     * which ui element was clicked. Perhaps we could use unique data-test-ids
     * or another unique identifier for this?
     **/
    component: string;
  };
  /** Whenever the user selects a result from the search results page. */
  SELECT_SEARCH_RESULT: {
    /** If the result is a related result, provide the ID of the 'original' result */
    related: string | null;
    /** The media type being searched */
    mediaType: MediaType;
    /** The slug (not the prettified name) of the provider */
    provider: string;
    /** The search term **/
    query: string;
  };
  /** The user clicks the CTA button to the external source to use the image */
  GET_MEDIA: {
    /** The unique ID of the media */
    id: string;
    /** The slug (not the prettified name) of the provider */
    provider: string;
    /** The media type being searched */
    mediaType: MediaType;
  };
  /** The user clicks one of the buttons to copy the media attribution */
  COPY_ATTRIBUTION: {
    /** The unique ID of the media */
    id: string;
    /** The format of the copied attribution */
    format: "plain" | "rich" | "html";
    /** The media type being searched */
    mediaType: MediaType;
  };
  /** The user reports a piece of media through our form */
  REPORT_MEDIA: {
    /** The unique ID of the media */
    id: string;
    /** The slug (not the prettified name) of the provider */
    provider: string;
    /** The media type being searched */
    mediaType: MediaType;
  };
  /** The user plays, pauses, or seeks an audio track.
   * @todo: This potentially requires throttling.
   **/
  AUDIO_INTERACTION: {
    /** The unique ID of the media */
    id: string;
    event: "seek" | "play" | "pause";
    /** The slug (not the prettified name) of the provider */
    provider: string;
  };
  /** The user visits a CC license description page on CC.org  **/
  VISIT_LICENSE_PAGE: {
    /** The slug of the license the user clicked on */
    license: string;
  };
  /** The user visits a creator's link in the single result UI  **/
  VISIT_CREATOR_LINK: {
    /** The unique ID of the media */
    id: string;
    /** The permalink to the creator's profile */
    url: string;
  };
  /** The user right clicks a single image result, most likely to download it. **/
  RIGHT_CLICK_IMAGE: {
    /** The unique ID of the media */
    id: string;
    /** The media type being searched */
    mediaType: MediaType;
  };
  /** The user uses the 'back to search' link on a single result **/
  BACK_TO_SEARCH: {
    /** The unique ID of the media */
    id: string;
    /** The media type being searched */
    mediaType: MediaType;
  };
  /** The visibility of the filter sidebar on desktop is toggled **/
  TOGGLE_FILTERS: {
    /** The media type being searched */
    mediaType: MediaType;
    /** The state of the filter sidebar after the user interaction. */
    state: "open" | "closed";
  };
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
  };
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
  });
}
```

### Implementation Plan

This needs more elaboration, as it's a very rough outline. For example, specific events will require more detailed planning.

- [ ] Create "Event Tracking" GitHub milestone in the frontend repository
- [ ] Design: design a privacy and analytics opt-out checkbox on the Privacy page
- [ ] Create an issue for the `ANALYTICS_ENABLED` feature flag
- [ ] Create an issue for the creation of the 'sendEvent' function and for the api route to post analytics events to
- [ ] Create a single issue for each event in the sample implementation. Each issue will need its specific implementation (when the event is called, what user DOM interaction triggers it, etc.) approved by frontend developers before it is implemented.

## Concerns / Pitfalls

- Related to content safety, this is an area where we are surfacing user information in the form of text, or even malicious URLs, to Openverse developers. These searches could include explicit or sensitive material. We're also potentially surfacing explicit image results to anyone working with this data.
- I think it's great to build this decoupled from a specific back-end, but if we never actually implement a backend this would largely be a wasted effort.
- We're building something here that is commonly drop-in when 3rd party tools are used. At least for page views; custom events still require custom work. Is this a poor use of time?

### Prior Art

[Snowplow](https://snowplow.io/) is "the world’s largest developer-first engine for collecting behavioral data". This is a heavy, complicated, and powerful analytics platform for [collecting](https://docs.snowplow.io/docs/collecting-data/collecting-from-own-applications/snowplow-tracker-protocol/example-requests/), [enriching](https://docs.snowplow.io/docs/enriching-your-data/available-enrichments/), and [modeling](https://docs.snowplow.io/docs/modeling-your-data/what-is-data-modeling/) data. This is about as robust as an open-source user behavior tracking platform can be.

[Plausible](https://plausible.io/) is a simple, lightweight, and self-hostable Google Analytics alternative. Our implementation here would be easily compatiable with Plausible's self-hosted or cloud offerings.

[Umami](https://umami.is/) is quite similar to Plausible. Their codebase contains [valuable discussions](https://github.com/umami-software/umami/pull/1272), for example why one might use `fetch` instead of `navigator.sendBeacon` to send analytics events even though the later was _designed_ for analytis use cases.
