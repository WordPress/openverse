import { stringToBoolean } from "~/utils/string-to-boolean"

describe("stringToBoolean", () => {
  it('returns true for "true", "yes" and "1"', async () => {
    expect(stringToBoolean("true")).toBe(true)
    expect(stringToBoolean("yes")).toBe(true)
    expect(stringToBoolean("1")).toBe(true)
  })

  it('returns false for "false", "no" and "0"', async () => {
    expect(stringToBoolean("false")).toBe(false)
    expect(stringToBoolean("no")).toBe(false)
    expect(stringToBoolean("0")).toBe(false)
  })

  it("returns booleans as-is", async () => {
    expect(stringToBoolean(true)).toBe(true)
    expect(stringToBoolean(false)).toBe(false)
  })

  it("converts null-ish values to false", async () => {
    expect(stringToBoolean(null)).toBe(false)
    expect(stringToBoolean(undefined)).toBe(false)
  })

  it("handles other strings", () => {
    expect(stringToBoolean("any content")).toBe(true)
    expect(stringToBoolean("")).toBe(false)
  })
})
