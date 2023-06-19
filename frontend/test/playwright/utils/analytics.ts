// Playwright utilities for making sure analytics events are sent correctly.
// Use collectAnalyticsEvents at the top of your test to collect all analytics events,
// and then expectAnalyticsEvent to make sure a specific event(s) has the correct payload.

import { BrowserContext, expect } from "@playwright/test"

import type { EventName, Events } from "~/types/analytics"

export type EventResponse<T extends EventName> = {
  n: T
  p: Events[T]
}

export type AnalyticEventResponses = Array<EventResponse<EventName>>

export function validateAnalyticsEvent<T extends EventName>(
  event: EventResponse<T>,
  expectedPayload: Events[T]
): boolean {
  const payload = event.p

  for (const key in expectedPayload) {
    if (payload[key] !== expectedPayload[key]) {
      return false
    }
  }

  return true
}

export function expectAnalyticsEvent<T extends EventName>(
  event: EventResponse<T>,
  expectedPayload: Events[T]
): void {
  const isValidEvent = validateAnalyticsEvent(event, expectedPayload)
  expect(isValidEvent).toBeTruthy()
}

export const collectAnalyticsEvents = (context: BrowserContext) => {
  const sentAnalyticsEvents: AnalyticEventResponses = []
  context.route("/api/event", (route, request) => {
    const postData = request.postData()
    if (postData) {
      const parsedData = JSON.parse(postData)
      const event = parsedData
      if (parsedData.p) {
        event.p = JSON.parse(parsedData.p)
      }
      sentAnalyticsEvents.push({ ...parsedData })
    }
    route.continue()
  })

  return sentAnalyticsEvents
}
