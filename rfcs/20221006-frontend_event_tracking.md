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

## Sample implementaton and event types

```ts
// Each event should have a unique key and a json-serializable data payload.

// This type is only for illustrative purposes and would be imported from elsewhere.
type MediaType = "image" | "audio" | "all";

/**
 * A list of all events allowed by our analytics server.
 */
type AnalyticsEvents = {
  /** A search performed by the user */
  SUBMIT_SEARCH: {
    /** The media type being searched */
    mediaType: MediaType;
    /** The search term **/
    query: string;
  };
  /**
   * Whenever the user navigates to a page.
   */
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
  /** Whenever the user clicks the load more button */
  LOAD_MORE_RESULTS: {};
  /** When a user opens the external sources popover. */
  VIEW_EXTERNAL_SOURCES: {};
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
  OPEN_PAGES_MENU: {};
  SELECT_RESULT: {
    /** If the result is a related result, provide the ID of the 'original' result */
    related: string | null;
  };
  GET_MEDIA: {};
  COPY_ATTRIBUTION: {};
  REPORT_MEDIA: {};
  AUDIO_INTERACTION: {};
  VISIT_LICENSE_PAGE: {};
  VISIT_CREATOR_LINK: {};
  RIGHT_CLICK_IMAGE: {};
  BACK_TO_SEARCH: {};
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
  const response = await fetch(`/api`, {
    method: "POST", // *GET, POST, PUT, DELETE, etc.
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return response.json(); // parses JSON response into native JavaScript objects
}
```
