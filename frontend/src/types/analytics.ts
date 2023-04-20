import type { MediaType, SearchType } from "~/constants/media"
import type { ReportReason } from "~/constants/content-report"

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
   * Description: The user clicks on one of the images in the gallery on the homepage.
   * Questions:
   * - Do users know homepage images are links?
   * - Do users find these images interesting?
   * - Which set is most interesting for the users?
   */
  CLICK_HOME_GALLERY_IMAGE: {
    /** the set to which the image belongs */
    set: string
    /** the identifier of the image */
    identifier: string
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
    /** The full URL of the source */
    url: string
    /** The media type being searched */
    mediaType: MediaType
    /** The search term */
    query: string
    /** The component that triggered the event */
    component: "VNoResults" | "VExternalSourceList"
  }
}

/**
 * the name of a custom event sent from the site
 */
export type EventName = keyof Events
