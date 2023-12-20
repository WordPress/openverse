import { describe, expect, it } from "vitest"

import { timeFmt } from "~/utils/time-fmt"

describe("timeFmt", () => {
  it("omits hours if zero", () => {
    expect(timeFmt(59)).toEqual("0:59")
    expect(timeFmt(60)).toEqual("1:00")
    expect(timeFmt(61)).toEqual("1:01")
  })

  it("handles zero minutes", () => {
    expect(timeFmt(59)).toEqual("0:59")
    expect(timeFmt(3600)).toEqual("1:00:00")
    expect(timeFmt(3659)).toEqual("1:00:59")
  })

  it("handles zero seconds", () => {
    expect(timeFmt(60)).toEqual("1:00")
    expect(timeFmt(3600)).toEqual("1:00:00")
    expect(timeFmt(3660)).toEqual("1:01:00")
  })

  it("pads minutes if hours present", () => {
    expect(timeFmt(3661)).toEqual("1:01:01")
  })

  it("handles duration of zero", () => {
    expect(timeFmt(0)).toEqual("0:00")
  })

  it("handles durations over 24 hours", () => {
    expect(timeFmt(86469)).toEqual("24:01:09")
  })
})
