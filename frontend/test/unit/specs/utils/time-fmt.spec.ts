import { describe, expect, it } from "vitest"

import { timeFmt } from "~/utils/time-fmt"

describe("timeFmt", () => {
  it("omits hours if zero", async () => {
    expect(timeFmt(59)).toBe("0:59")
    expect(timeFmt(60)).toBe("1:00")
    expect(timeFmt(61)).toBe("1:01")
  })

  it("handles zero minutes", async () => {
    expect(timeFmt(59)).toBe("0:59")
    expect(timeFmt(3600)).toBe("1:00:00")
    expect(timeFmt(3659)).toBe("1:00:59")
  })

  it("handles zero seconds", async () => {
    expect(timeFmt(60)).toBe("1:00")
    expect(timeFmt(3600)).toBe("1:00:00")
    expect(timeFmt(3660)).toBe("1:01:00")
  })

  it("pads minutes if hours present", async () => {
    expect(timeFmt(3661)).toBe("1:01:01")
  })

  it("handles duration of zero", () => {
    expect(timeFmt(0)).toBe("0:00")
  })

  it("handles durations over 24 hours", () => {
    expect(timeFmt(86469)).toBe("24:01:09")
  })
})
