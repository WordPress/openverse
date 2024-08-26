import fs from "node:fs"

import path from "node:path"

import { describe, test, expect } from "vitest"
import rootNock from "nock"

const mockThumbnailBuffer = fs.readFileSync(
  path.resolve(__dirname, "mock-thumbnail.bin")
)

import { createClient, ClientCredentials } from "@openverse/api-client"

const getClientAndNock = (credentials?: ClientCredentials) => ({
  client: createClient({
    baseUrl: "https://nock.local/",
    credentials,
  }),
  nock: rootNock("https://nock.local/"),
})

describe("OpenverseClient", () => {
  describe("api token refresh", async () => {
    test("should automatically refresh api token before sending final request", async () => {
      const { client, nock } = getClientAndNock({
        clientId: "test",
        clientSecret: "test-secret",
      })

      const scope = nock
        .post("/v1/auth_tokens/token/", /test-secret/)
        .reply(200, {
          access_token: "test-access-token",
          scope: "test-scope",
          expires_in: 10,
          token_type: "test-token-type",
        })
        .get("/v1/images/")
        .matchHeader("Authorization", "Bearer test-access-token")
        .reply(200, {
          results: ["this would be an image, under normal circumstances..."],
        })

      const images = await client.GET("/v1/images/")

      expect(images.error).toBeUndefined()

      expect(images.data?.results[0]).toEqual(
        "this would be an image, under normal circumstances..."
      )

      scope.done()
    })

    test("should not send multiple api token requests if already requesting", async () => {
      const { client, nock } = getClientAndNock({
        clientId: "test",
        clientSecret: "test-secret",
      })

      const scope = nock
        .post("/v1/auth_tokens/token/", /test-secret/)
        .delay(1000)
        .times(1)
        .reply(200, {
          access_token: "test-access-token",
          scope: "test-scope",
          expires_in: 100,
          token_type: "test-token-type",
        })
        .get("/v1/images/")
        .matchHeader("Authorization", "Bearer test-access-token")
        .reply(200, {
          results: ["this would be an image, under normal circumstances..."],
        })
        .get("/v1/audio/")
        .matchHeader("Authorization", "Bearer test-access-token")
        .reply(200, {
          results: [
            "this would be an audio track, under normal circumstances...",
          ],
        })

      const [images, audio] = await Promise.all([
        client.GET("/v1/images/"),
        client.GET("/v1/audio/"),
      ])

      expect(images.error).toBeUndefined()
      expect(audio.error).toBeUndefined()

      expect(images.data?.results[0]).toEqual(
        "this would be an image, under normal circumstances..."
      )
      expect(audio.data?.results[0]).toEqual(
        "this would be an audio track, under normal circumstances..."
      )

      scope.done()
    })

    test("should send but not await token response if current token still within expiry threshold", async () => {
      const { client, nock } = getClientAndNock({
        clientId: "test",
        clientSecret: "test-secret",
      })

      const scope = nock
        .post("/v1/auth_tokens/token/", /test-secret/)
        .times(1)
        .reply(200, {
          access_token: "test-access-token-1",
          scope: "test-scope",
          // Expiry threshold is 5 so requests after this come back will need to make a new one
          expires_in: 2,
          token_type: "test-token-type",
        })
        .get("/v1/images/")
        .matchHeader("Authorization", "Bearer test-access-token-1")
        .reply(200, {
          results: ["this would be an image, under normal circumstances..."],
        })
        .get("/v1/audio/")
        .matchHeader("Authorization", "Bearer test-access-token-1")
        .reply(200, {
          results: [
            "this would be an audio track, under normal circumstances...",
          ],
        })
        .get("/v1/audio/single-audio/")
        .matchHeader("Authorization", "Bearer test-access-token-1")
        .reply(200, {
          id: "single-audio",
        })
        .post("/v1/auth_tokens/token/", /test-secret/)
        .delay(3)
        .times(1)
        .reply(200, {
          access_token: "test-access-token-2",
          scope: "test-scope",
          expires_in: 10,
          token_type: "test-token-type",
        })
        .get("/v1/images/single-image/")
        .matchHeader("Authorization", "Bearer test-access-token-2")
        .reply(200, {
          id: "single-image",
        })

      // The two search requests will match the first access token
      // Await each so that the audio search definitely happens after the token is available
      // That confirms that requests inside the expiry threshold queue a token refresh but still use the previous valid token
      // until the expiry threshold is passed. The single audio request will still match the first token.
      // Then we need to wait 3 seconds to ensure we're past the expiry of the first token
      // And the single image request will match the second token, triggered by the audio request
      const images = await client.GET("/v1/images/")
      expect(images.error).toBeUndefined()
      expect(images.data?.results[0]).toEqual(
        "this would be an image, under normal circumstances..."
      )
      const audioTracks = await client.GET("/v1/audio/")
      expect(audioTracks.error).toBeUndefined()
      expect(audioTracks.data?.results[0]).toEqual(
        "this would be an audio track, under normal circumstances..."
      )
      const singleAudio = await client.GET("/v1/audio/{identifier}/", {
        params: { path: { identifier: "single-audio" } },
      })
      expect(singleAudio.error).toBeUndefined()
      expect(singleAudio.data?.id).toEqual("single-audio")

      await new Promise((res) => setTimeout(res, 3000))

      const singleResult = await client.GET("/v1/images/{identifier}/", {
        params: {
          path: { identifier: "single-image" },
        },
      })

      expect(singleResult.error).toBeUndefined()
      expect(singleResult.data?.id).toEqual("single-image")
      scope.done()
    })
  })

  test("image stats", async () => {
    const { client, nock } = getClientAndNock()
    const scope = nock
      .get("/v1/images/stats/")
      .reply(200, [{ source_name: "flickr" }])

    const response = await client.GET("/v1/images/stats/")

    expect(response).toEqual(
      expect.objectContaining({
        data: expect.arrayContaining([
          expect.objectContaining({ source_name: "flickr" }),
        ]),
      })
    )
    scope.done()
  })

  test("queried search", async () => {
    const { client, nock } = getClientAndNock()
    const scope = nock
      .get("/v1/images/")
      .query({
        q: "dogs",
      })
      .reply(200, {
        results: [
          {
            id: "a-dog",
          },
        ],
      })
      .get("/v1/images/a-dog/thumb/")
      .reply(200, mockThumbnailBuffer, { "Content-Type": "image/jpeg" })

    const imageSearch = await client.GET("/v1/images/", {
      params: { query: { q: "dogs" } },
    })

    expect(imageSearch).toEqual(
      expect.objectContaining({
        response: expect.objectContaining({
          status: 200,
        }),
        data: expect.objectContaining({
          results: expect.arrayContaining([
            expect.objectContaining({
              id: "a-dog",
            }),
          ]),
        }),
      })
    )

    const identifier = imageSearch.data?.results[0].id as string

    const thumbnail = await client.GET("/v1/images/{identifier}/thumb/", {
      params: { path: { identifier } },
      parseAs: "stream",
    })

    expect(thumbnail.response.status).toEqual(200)

    scope.done()
  })
})
