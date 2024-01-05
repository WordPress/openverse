import { describe, expect, vi } from "vitest"

import { initProviderServices } from "~/data/media-provider-service"
import { warn } from "~/utils/console"

vi.mock("~/utils/console", () => ({ warn: vi.fn(), log: vi.fn() }))

// vi.mock("~/data/api-service", () => ({
//   createApiService: function () {
//     return {
//       get: async () => {
//         return {}
//       },
//     }
//   },
// }))

describe("Media Provider Service", () => {
  it("No data in response", async () => {
    const result = await initProviderServices.image().getProviderStats()
    expect(result).toEqual([])
    expect(warn).toHaveBeenCalledTimes(1)
    expect(warn).toHaveBeenCalledWith(
      "Invalid response from provider stats endpoint: {}"
    )
  })
})
