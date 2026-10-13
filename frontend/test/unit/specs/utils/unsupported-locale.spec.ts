import { describe, expect, it } from "vitest"

import { getUnsupportedLocaleRedirect } from "#shared/utils/unsupported-locale"

const supported = ["en", "es", "es-ar"]

describe("getUnsupportedLocaleRedirect", () => {
  it.each`
    path                | expected
    ${"/cn"}            | ${"/"}
    ${"/cn/search"}     | ${"/search"}
    ${"/xx-yy/about"}   | ${"/about"}
    ${"/zz/"}           | ${"/"}
  `(
    "strips the unsupported prefix `$path` -> `$expected`",
    ({ path, expected }) => {
      expect(getUnsupportedLocaleRedirect(path, supported)).toBe(expected)
    }
  )

  it.each`
    path            | reason
    ${"/es"}        | ${"supported base locale"}
    ${"/es/search"} | ${"supported base locale with sub-path"}
    ${"/es-ar"}     | ${"supported regional locale"}
  `("leaves supported locale `$path` alone ($reason)", ({ path }) => {
    expect(getUnsupportedLocaleRedirect(path, supported)).toBeNull()
  })

  it.each`
    path             | reason
    ${"/"}           | ${"homepage"}
    ${"/about"}      | ${"a real page name"}
    ${"/search"}     | ${"a real page name"}
    ${"/image/uuid"} | ${"a multi-segment path"}
    ${"/123"}        | ${"a numeric segment"}
  `("leaves non-locale-shaped path `$path` alone ($reason)", ({ path }) => {
    expect(getUnsupportedLocaleRedirect(path, supported)).toBeNull()
  })

  it("preserves nested paths beyond the first segment", () => {
    expect(getUnsupportedLocaleRedirect("/cn/search/audio", supported)).toBe(
      "/search/audio"
    )
  })
})
