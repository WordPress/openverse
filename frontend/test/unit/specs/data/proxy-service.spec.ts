import { describe, expect, it, vi } from "vitest"
import { image } from "~~/test/unit/fixtures/image"

import { INTERNAL_REQUEST_HEADER } from "#shared/constants/proxy"
import { createProxyClient } from "~/data/proxy-service"
import { useProviderStore } from "~/stores/provider"

const { id } = image

const setup = (response: unknown, internalRequestToken?: string) => {
  const requestFetch = vi.fn().mockResolvedValue(response)
  const client = createProxyClient({
    requestFetch: requestFetch as unknown as typeof $fetch,
    providerStore: useProviderStore(),
    internalRequestToken,
  })
  return { client, requestFetch }
}

describe("createProxyClient", () => {
  it("sends searches to the server route and keys results by id", async () => {
    const { client, requestFetch } = setup({
      data: {
        result_count: 1,
        page_count: 1,
        page_size: 20,
        page: 1,
        results: [image],
      },
    })

    const { data } = await client.search("audio", { q: "cat" })

    expect(requestFetch).toHaveBeenCalledWith("/api/search/audio/", {
      query: { q: "cat", peaks: "true" },
      headers: {},
    })
    expect(Object.keys(data.results)).toEqual([id])
  })

  it("adds the internal request header when a token is passed", async () => {
    const { client, requestFetch } = setup({ results: [] }, "token")

    await client.getRelatedMedia("image", id)

    expect(requestFetch).toHaveBeenCalledWith(`/api/image/related/${id}/`, {
      query: {},
      headers: { [INTERNAL_REQUEST_HEADER]: "token" },
    })
  })

  it("requests a single result", async () => {
    const { client, requestFetch } = setup(image)

    const item = await client.getSingleMedia("image", id)

    expect(requestFetch).toHaveBeenCalledWith(`/api/image/${id}/`, {
      headers: {},
    })
    expect(item.id).toEqual(id)
  })
})
