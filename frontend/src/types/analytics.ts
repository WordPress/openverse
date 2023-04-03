import type { UnionToIntersection } from "type-fest"

type ReservedPropNames =
  | "timestamp"
  | "language"
  | "breakpoint"
  | "ua"
  | "os"
  | "platform"
  | "browser"
  | "version"
  | "origin"
  | "pathname"
  | "referrer"
  | "width"
  | "height"

type BaseEventsType = Record<string, Record<string, string | number | boolean>>

type MergePayloadTypes<E extends BaseEventsType> = UnionToIntersection<
  E[keyof E]
>
type ValidatePayloads<
  E extends BaseEventsType,
  Payloads = MergePayloadTypes<E>
> = Omit<Payloads, ReservedPropNames> extends Payloads
  ? E
  : "Payloads include reserved prop names."

type ExtractEventNames<E> = E extends Record<infer K, unknown>
  ? K extends string
    ? K
    : never
  : never

type ValidateEventNames<E> = ExtractEventNames<E> extends Uppercase<
  ExtractEventNames<E>
>
  ? E
  : "Event names must be in SCREAMING_SNAKE_CASE."

type OnlyErrors<A, B> = A extends string
  ? B extends string
    ? A | B
    : A
  : B extends string
  ? B
  : boolean

type ValidateEvents<
  E extends BaseEventsType,
  ValidatedEventNames = ValidateEventNames<E>,
  ValidatedPayloads = ValidatePayloads<E>,
  Errors = OnlyErrors<ValidatedEventNames, ValidatedPayloads>
> = Errors extends string ? Errors : E

type IsRecord<E extends BaseEventsType> = E

/**
 * compound type of all custom events sent from the site; Index with `EventName`
 * to get the type of the payload for a specific event.
 *
 * Conventions:
 * - Names should be in SCREAMING_SNAKE_CASE.
 * - Names should be imperative for events associated with user action.
 * - Names should be in past tense for events not associated with user action.
 * - Documentation must be the step to emit the event, followed by a line break.
 * - Questions that are answered by the event must be listed as bullet points.
 */
export type Events = ValidateEvents<{
  /**
   * Click on one of the images in the gallery on the homepage.
   *
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
}>

/**
 * If `Events` is not a valid type parameter to `IsRecord` then
 * the configuration is invalid. `Events` will be set to string
 * types represnting the specific error case(s) present.
 *
 * Exported to avoid needing to ignore the unused variable error.
 */
export type IsValid = IsRecord<Events>

/**
 * the name of a custom event sent from the site
 */
export type EventName = keyof Events
