// Playwright utilities for making sure analytics events are sent correctly.
// Use collectAnalyticsEvents at the top of your test to collect all analytics events,
// and then expectEventPayloadToMatch to make sure a specific event(s) has the correct payload.

import { BrowserContext, expect } from "@playwright/test"

import type { EventName, Events } from "~/types/analytics"

export type EventResponse<T extends EventName> = {
  n: T
  p: Events[T]
}

export type AnalyticEventResponses = Array<EventResponse<EventName>>

export function expectEventPayloadToMatch<T extends EventName>(
  event: EventResponse<T> | undefined,
  expectedPayload: Events[T]
): void {
  expect(
    event,
    `Event not captured; expected payload of ${JSON.stringify(expectedPayload)}`
  ).toBeDefined()
  // Safe to cast as previous line ensures it is defined
  expect((event as EventResponse<T>).p).toMatchObject(expectedPayload)
}

export const collectAnalyticsEvents = (context: BrowserContext) => {
  const sentAnalyticsEvents: AnalyticEventResponses = []
  context.route(/\/api\/event$/, (route, request) => {
    const postData = request.postData()
    if (postData) {
      const parsedData = JSON.parse(postData)
      const event = parsedData
      if (parsedData.p) {
        event.p = JSON.parse(parsedData.p)
      }
      sentAnalyticsEvents.push({ ...event })
    }
    route.abort()
  })

  return sentAnalyticsEvents
}
