import { describe, expect, it } from "vitest"
import {
  buildEventPayload,
  filterQuery,
  generateApiPath,
} from "~~/server/utils/proxy"

import { SEARCH_QUERY_ALLOWLIST } from "#shared/constants/proxy"

describe("filterQuery", () => {
  it("keeps only the allowed string parameters", () => {
    expect(
      filterQuery(
        {
          q: "cat",
          page: "2",
          page_size: "50",
          license: ["by", "cc0"],
          filter_dead: "false",
        },
        SEARCH_QUERY_ALLOWLIST
      )
    ).toEqual({ q: "cat", page: "2" })
  })
})

describe("generateApiPath", () => {
  it.each`
    kind               | mediaType  | expected
    ${"search"}        | ${"image"} | ${"/v1/images/"}
    ${"search"}        | ${"audio"} | ${"/v1/audio/"}
    ${"single-result"} | ${"image"} | ${"/v1/images/{identifier}/"}
    ${"related"}       | ${"audio"} | ${"/v1/audio/{identifier}/related/"}
  `(
    "returns $expected for $kind $mediaType",
    ({ kind, mediaType, expected }) => {
      expect(generateApiPath(kind, mediaType)).toEqual(expected)
    }
  )
})

describe("buildEventPayload", () => {
  const requestDatetime = new Date("2026-11-13T10:00:00Z")

  it("builds the payload from the Cloudflare headers", () => {
    const headers = new Headers({
      date: "Fri, 13 Nov 2026 10:00:02 GMT",
      "cf-cache-status": "MISS",
      "cf-ray": "8d1e2f3a4b5c6d7e-AMS",
    })
    expect(
      buildEventPayload(headers, requestDatetime, "image", { q: "cat" })
    ).toEqual({
      cfCacheStatus: "MISS",
      cfRayIATA: "AMS",
      elapsedTime: 2,
      queryString: "?q=cat",
      mediaType: "image",
    })
  })

  it("returns undefined without the Cloudflare headers", () => {
    const headers = new Headers({ date: "Fri, 13 Nov 2026 10:00:02 GMT" })
    expect(
      buildEventPayload(headers, requestDatetime, "image", {})
    ).toBeUndefined()
  })
})
