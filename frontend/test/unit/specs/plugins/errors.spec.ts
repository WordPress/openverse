import { describe, expect, it } from "vitest"
import { FetchError } from "ofetch"

import { normalizeFetchingError } from "~/plugins/04.errors"

const fetchError = ({
  statusCode,
  data,
  headers = {},
}: {
  statusCode?: number
  data?: unknown
  headers?: Record<string, string>
}) => {
  const error = new FetchError("[GET] /api/search/image/: request failed")
  error.statusCode = statusCode
  error.data = data
  if (statusCode) {
    error.response = new Response(null, {
      status: statusCode,
      headers,
    }) as FetchError["response"]
  }
  return error
}

describe("normalizeFetchingError with proxy route errors", () => {
  it("keeps the status code and the Retry-After header of a 429", () => {
    const error = fetchError({
      statusCode: 429,
      data: { statusCode: 429, data: { retryAfter: 30 } },
      headers: { "retry-after": "30" },
    })

    expect(normalizeFetchingError(error, "image", "search")).toMatchObject({
      statusCode: 429,
      code: "ERR_UNKNOWN",
      details: { retryAfter: "30" },
    })
  })

  it("uses the API detail message", () => {
    const error = fetchError({
      statusCode: 400,
      data: { statusCode: 400, data: { detail: "Invalid license" } },
    })

    expect(normalizeFetchingError(error, "image", "search")).toMatchObject({
      statusCode: 400,
      message: "Invalid license",
    })
  })

  it("uses the error code from the route", () => {
    const error = fetchError({
      statusCode: 504,
      data: { statusCode: 504, data: { code: "ECONNABORTED" } },
    })

    expect(
      normalizeFetchingError(error, "audio", "single-result")
    ).toMatchObject({ statusCode: 504, code: "ECONNABORTED" })
  })

  it("returns a network error without a response", () => {
    expect(
      normalizeFetchingError(fetchError({}), "image", "related")
    ).toMatchObject({ code: "ERR_NETWORK" })
  })
})
