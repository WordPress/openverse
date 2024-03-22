import type {
  MediaType,
  SearchType,
  SupportedSearchType,
} from "~/constants/media"
import type { ReportReason } from "~/constants/content-report"
import type { FilterCategory } from "~/constants/filters"
import { ResultKind } from "~/types/result"

import { RequestKind } from "./fetch-state"
import { Collection } from "./search"

export type AudioInteraction = "play" | "pause" | "seek"
export type AudioInteractionData = Exclude<
  Events["AUDIO_INTERACTION"],
  "component"
>
export type AudioComponent =
  | "VRelatedAudio"
  | "VGlobalAudioTrack"
  | "AudioSearch"
  | "AudioDetailPage"
  | "VAllResultsGrid"

/**
 * Common properties related to searches
 * on collection pages, added in the
 * "Additional Search Views" project.
 */
type CollectionProperties = {
  /** If a collection page, the type of collection */
  collectionType: Collection | null
  /** A string representing a unique identifier for the collection */
  collectionValue: string | null
}

/**
 * Compound type of all custom events sent from the site; Index with `EventName`
 * to get the type of the payload for a specific event.
 *
 * Conventions:
 * - Names should be in SCREAMING_SNAKE_CASE.
 * - Names should be imperative for events associated with user action.
 * - Names should be in past tense for events not associated with user action.
 * - Documentation must be the step to emit the event, followed by a line break.
 * - Questions that are answered by the event must be listed as bullet points.
 */
export type Events = {
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
    searchType: SearchType
    /** The search term */
    query: string
  }
  /**
   * Description: The user clicks on one of the images in the gallery on the homepage.
   * Questions:
   * - Do users know homepage images are links?
   * - Do users find these images interesting?
   * - Which set is most interesting for the users?
   */
  CLICK_HOME_GALLERY_IMAGE: {
    /** the set to which the image belongs */
    set: string
    /** The unique ID of the media */
    id: string
  }
  /**
   * Description: The user opens the menu which lists pages.
   * Questions:
   *   - How often is this menu used?
   *   - Is this menu visible enough?
   */
  OPEN_PAGES_MENU: Record<string, never>
  /**
   * Description: The user right clicks a single image result, most likely to download it.
   * Questions:
   *   - Do users right-click images often? Does this suggest downloading them directly,
   *     when not paired with a `GET_MEDIA` event?
   */
  RIGHT_CLICK_IMAGE: {
    id: string
  }
  /**
   * Click on the 'back to search' link on a single result
   *
   * - Are these links used much? Are they necessary?
   */
  BACK_TO_SEARCH: {
    /** The unique ID of the media */
    id: string
    /** The content type being searched (can include All content) */
    searchType: SearchType
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
   *   - Do users use external search after reaching the result end?
   *   - Do users find a result before reaching the end of the results?
   */
  REACH_RESULT_END: {
    /** The media type being searched */
    searchType: SupportedSearchType
    /** The kind of search reached (a collection, a standard search view, etc.)  */
    kind: ResultKind
    /** The search term */
    query: string
    /** The current page of results the user is on. */
    resultPage: number
  } & CollectionProperties
  /**
   * Description: The user clicks the CTA button to the external source to use the image
   * Questions:
   *   - How often do users go to the source after viewing a result?
   */
  GET_MEDIA: {
    /** the unique ID of the media */
    id: string
    /** The slug (not the prettified name) of the provider */
    provider: string
    /** The media type being searched */
    mediaType: MediaType
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
    mediaType: MediaType
  }
  /**
   * Description: The user reports a piece of media through our form
   * Questions:
   *   - How often do we get reports?
   *   - Which types of reports are more common?
   *   - Do we see an uptick in reports when a certain provider
   *     is added/updated/refreshed?
   * Note: Because the DMCA report is sent via a Google form, we send
   * this event when the form is opened, and not when the report form
   * is actually sent.
   */
  REPORT_MEDIA: {
    /** the unique ID of the media */
    id: string
    /** the slug (not the prettified name) of the provider */
    provider: string
    /** the media type being searched */
    mediaType: MediaType
    /** the reason for the report */
    reason: ReportReason
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
    /** The media type being searched */
    mediaType: MediaType
    /** The search term */
    query: string
    /** The component that triggered the event */
    component: "VNoResults" | "VExternalSourceList"
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
   * Description: The visibility of the filter sidebar on desktop is toggled
   * Questions:
   *   - Do a majority users prefer the sidebar visible or hidden?
   */
  TOGGLE_FILTER_SIDEBAR: {
    /** The media type being searched */
    searchType: SearchType
    /** The state of the filter sidebar after the user interaction. */
    toState: "opened" | "closed"
  }
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
  }
  /**
   * Description: The user visits a creator's link in the single result UI
   * or the creator's collection page.
   * Questions:
   *   - Are creator links clicked much? Does Openverse increase visibility
   *     of included creator's profiles?
   */
  VISIT_CREATOR_LINK: {
    /** The unique ID of the media, if the creator link is on the single result page */
    id?: string
    /** The permalink to the creator's profile */
    url: string
    /** The slug for the source where the creator's media is from */
    source: string
  }
  /**
   * Description: The user visits a source's link in the single result UI
   * or the source's collection page.
   * Questions:
   *   - Are source links clicked much? Does Openverse increase visibility
   *     of included sources?
   */
  VISIT_SOURCE_LINK: {
    /** The unique ID of the media, if the source link is on the single
     * result page */
    id?: string
    /** The source's slug that identifies it */
    source: string
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
    /** Kind of the result selected: search/related/collection */
    kind: ResultKind
    /** The media type being searched */
    mediaType: SearchType
    /** The slug (not the prettified name) of the provider */
    provider: string
    /** The search term */
    query: string
    /** the reasons for why this result is considered sensitive */
    sensitivities: string
    /** whether the result was blurred or visible when selected by the user */
    isBlurred: boolean | null
  } & CollectionProperties
  /**
   * Description: When a user opens the external sources popover.
   * Questions:
   *   - How often do users use this feature?
   *   - Under what conditions to users use this feature? No results?
   *     Many results, but none they actually select?
   */
  VIEW_EXTERNAL_SOURCES: {
    /** The media type being searched */
    searchType: SearchType
    /** The search term */
    query: string
    /** Pagination depth */
    resultPage: number
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
    searchType: SearchType
    /** The kind of search (a collection, a standard search view, etc.)  */
    kind: ResultKind
    /** The search term */
    query: string
    /** The current page of results the user is on,
     * *before* loading more results.. */
    resultPage: number
  } & CollectionProperties
  /**
   * Description: Whenever the user sets a filter. Filter category and key are the values used in code, not the user-facing filter labels.
   * Questions:
   *  - Do most users filter their searches?
   *  - What % of users use filtering?
   *  - Which filters are most popular? Least popular?
   *  - Are any filters so commonly applied they should become defaults?
   */
  APPLY_FILTER: {
    /** The filter category, e.g. `license`  */
    category: FilterCategory
    /** The filter key, e.g. `by` */
    key: string
    /** Whether the filter is checked or unchecked */
    checked: boolean
    /** The media type being searched, can include All content */
    searchType: SearchType
    /** The search term */
    query: string
  }

  /** Description: The user plays, pauses, or seeks an audio track.
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
    event: AudioInteraction
    /** The slug (not the prettified name) of the provider */
    provider: string
    /** The name of the Vue component used on the interaction, e.g. the global or main player. */
    component: AudioComponent
  }

  /* Content safety events */

  /**
   * Description: The user flips the sidebar toggle to fetch sensitive results.
   *
   * Questions:
   * - Are users seeking sensitive content from Openverse?
   */
  TOGGLE_FETCH_SENSITIVE: {
    /** whether the switch was turned on or off */
    checked: boolean
  }

  /**
   * Description: The user flips the sidebar toggle to not blur sensitive
   * content in the search results.
   *
   * Questions:
   * - Are users comfortable seeing sensitive content alongside safe results?
   * - Do users find the blurring useful or just an extra step?
   */
  TOGGLE_BLUR_SENSITIVE: {
    /** whether the switch was turned on or off */
    checked: boolean
  }

  /**
   * Description: The user proceeds to see the sensitive content from the
   * content safety wall.
   *
   * Questions:
   * - Do people choose to see a result based on the explanation for why it was
   *   marked sensitive?
   * - What sensitivity values are most likely to make a user want to go ahead?
   */
  UNBLUR_SENSITIVE_RESULT: {
    /** the unique ID of the sensitive result */
    id: string
    /** the reasons for why this result is considered sensitive */
    sensitivities: string
  }

  /**
   * Description: The user opts not to see the sensitive content and to go back
   * to the search results from the content safety wall.
   *
   * Questions:
   * - Do people choose not to see a result based on the explanation for why it
   *   was marked sensitive?
   * - What sensitivity values are most likely to make a user go back?
   *
   * This event is similar to the `BACK_TO_SEARCH` event, but is separate
   * because it is only triggered from the content safety wall.
   */
  GO_BACK_FROM_SENSITIVE_RESULT: {
    /** the unique ID of the sensitive result */
    id: string
    /** the reasons for why this result is considered sensitive */
    sensitivities: string
  }

  /**
   * Description: The user opts to re-hide the sensitive content that has been
   * unblurred and presented to them.
   *
   * Questions:
   * - What content on Openverse would be so sensitive that a person would want
   *   to hide it after they've seen it?
   * - Do users prefer to briefly see and re-hide most sensitive content?
   */
  REBLUR_SENSITIVE_RESULT: {
    /** the unique ID of the sensitive result */
    id: string
    /** the reasons for why this result is considered sensitive */
    sensitivities: string
  }
  /**
   * Description: The user expands collapsed tags or collapses the expanded ones.
   *
   * Questions:
   * - Are the extra tags useful to users?
   * - Do users ever collapse expanded tags?
   */
  TOGGLE_TAG_EXPANSION: {
    /** The state of the tags after the user interaction. */
    toState: "expanded" | "collapsed"
  }
  /**
   * Description: Recorded when a network error occurs. Recorded in Plausible,
   * rather than Sentry, because we never have sufficient information in Sentry
   * to identify patterns that could be relevant, like regional issues.
   */
  NETWORK_ERROR: {
    /** The kind of request the network error occurred during */
    requestKind: RequestKind
    /** The search type when the network error occurred */
    searchType: SupportedSearchType
  }
}

/**
 * the name of a custom event sent from the site
 */
export type EventName = keyof Events
