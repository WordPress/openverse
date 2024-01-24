// @vitest-environment node
import { describe, expect, it } from "vitest"

import { getApiAccessToken } from "~/utils/api-token"

describe("missing client credentials", () => {
  describe("completely missing", () => {
    it("should not make any requests and fall back to tokenless", async () => {
      const token = await getApiAccessToken({})

      expect(token).toEqual(undefined)
    })
  })

  describe("explicitly undefined", () => {
    it("should not make any requests and fall back to tokenless", async () => {
      const accessToken = await getApiAccessToken({
        apiClientId: undefined,
        apiClientSecret: undefined,
      })
      expect(accessToken).toEqual(undefined)
    })
  })
})
