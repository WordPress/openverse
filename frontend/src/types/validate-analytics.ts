import type { Events } from "~/types/analytics"

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

type EventsOrErrors = ValidateEvents<Events>

/**
 * If `Events` is not a valid type parameter to `IsRecord` then
 * the configuration is invalid. `Events` will be set to string
 * types represnting the specific error case(s) present.
 *
 * Exported to avoid needing to ignore the unused variable error.
 */
export type IsValid = IsRecord<EventsOrErrors>
