import { describe, expect, it } from "vitest"

import { decodeData } from "~/utils/decode-data"

describe("decodeData", () => {
  it("returns empty string for empty string", () => {
    const data = ""

    expect(decodeData(data)).toBe("")
  })

  it("returns empty string for undefined data", () => {
    const data = undefined

    expect(decodeData(data)).toBe("")
  })

  it("returns decoded ASCII hexacode strings", () => {
    const data = "s\\xe9"

    expect(decodeData(data)).toBe("sé")
  })

  it("returns decoded unicode strings", () => {
    const data = "s\\u1234"

    expect(decodeData(data)).toBe("s\u1234")
  })

  it("returns decoded strings consisting of both unicode and ASCII hexacode characters", () => {
    const data = "s\\u1234\xe9"

    expect(decodeData(data)).toBe("s\u1234\xe9")
  })

  it("returns decoded string when string does not contain backslash", () => {
    const data = "musu00e9e"

    expect(decodeData(data)).toBe("musée")
  })

  it("shouldn't throw exception", () => {
    const data = "Classic Twill - SlipcoverFabrics.com 100% Cotton"

    expect(decodeData(data)).toBe(data)
  })
})
