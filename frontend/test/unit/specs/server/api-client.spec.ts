import { afterEach, describe, expect, it, vi } from "vitest"
import {
  createOpenverseApiClient,
  getSignatureHeaders,
} from "~~/server/utils/api-client"

const NOW = 1_763_200_000_000

describe("getSignatureHeaders", () => {
  it("signs the path, query and timestamp", () => {
    expect(
      getSignatureHeaders(
        "https://api.openverse.org/v1/images/?q=cat%20dog&page=2",
        "test-secret",
        NOW
      )
    ).toEqual({
      "x-ov-cf-timestamp": "1763200000",
      "x-ov-cf-mac": "h4Gq657vV8M3LsN2uks62k4hBnjk5RB1qqJv0W_nTzw",
    })
  })
})

describe("createOpenverseApiClient", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  const getSentHeaders = async (signingSecret?: string) => {
    const fetchMock = vi.fn(async () => Response.json({ results: [] }))
    vi.stubGlobal("fetch", fetchMock)

    const client = createOpenverseApiClient({
      apiUrl: "https://api.openverse.org/",
      signingSecret,
    })
    await client.GET("/v1/images/", { params: { query: { q: "cat" } } })

    const [, init] = fetchMock.mock.calls[0] as unknown as [
      Request,
      RequestInit,
    ]
    return new Headers(init.headers)
  }

  it("signs the requests when the secret is set", async () => {
    const headers = await getSentHeaders("test-secret")

    expect(headers.get("x-ov-cf-timestamp")).toMatch(/^\d+$/)
    expect(headers.get("x-ov-cf-mac")).toMatch(/^[\w-]{43}$/)
    expect(headers.get("user-agent")).toContain("Openverse")
  })

  it("does not sign the requests without the secret", async () => {
    const headers = await getSentHeaders()

    expect(headers.has("x-ov-cf-timestamp")).toBe(false)
    expect(headers.has("x-ov-cf-mac")).toBe(false)
  })
})
