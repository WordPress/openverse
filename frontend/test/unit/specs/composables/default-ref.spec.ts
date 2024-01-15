import { describe, expect, it } from "vitest"

import { defaultRef } from "~/composables/default-ref"

describe("defaultRef", () => {
  it("should use the default value", async () => {
    const getDefault = () => 100
    const value = defaultRef(getDefault)
    expect(value.value).toBe(100)
  })

  it("should use the set value", async () => {
    const value = defaultRef(() => "a")
    value.value = "b"
    expect(value.value).toBe("b")
  })

  it.each([0, "", false, undefined, null] as const)(
    "should use the set value even if it is falsy as `%s`",
    (v) => {
      const value = defaultRef(() => "non-null default" as typeof v)
      value.value = v
      expect(value.value).toBe(v)
    }
  )
})
