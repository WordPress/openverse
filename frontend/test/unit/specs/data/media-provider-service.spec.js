import { initProviderServices } from "~/data/media-provider-service"
import { warn } from "~/utils/console"

jest.mock("~/utils/console", () => ({ warn: jest.fn(), log: jest.fn() }))
let mockReturn = {}
jest.mock("~/data/api-service", () => ({
  createApiService: function () {
    return {
      get: async () => {
        return mockReturn
      },
    }
  },
}))

describe("Media Provider Service", () => {
  afterEach(() => {
    warn.mockClear()
  })
  it("No data in response", async () => {
    const result = await initProviderServices.image().getProviderStats()
    expect(result).toEqual([])
    expect(warn).toHaveBeenCalledTimes(1)
    expect(warn).toHaveBeenCalledWith(
      "Invalid response from provider stats endpoint: {}"
    )
  })
})
