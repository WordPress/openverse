import { ref } from "vue"

import { describe, expect, it, vi } from "vitest"

import { useSeekable } from "~/composables/use-seekable"

describe("useSeekable", () => {
  const setup = (time = 0) => {
    const currentTime = ref(time)
    const duration = ref(60.116463)
    const onSeek = vi.fn()
    const seekable = useSeekable({
      currentTime,
      duration,
      isReady: ref(true),
      isSeekable: ref(true),
      onSeek,
      onTogglePlayback: vi.fn(),
    })

    return { ...seekable, currentTime, duration, onSeek }
  }

  it.each<[number, string]>([
    [0, "0:00"],
    [1, "0:01"],
    [1.999999, "0:01"],
    [60.116463, "1:00"],
    [59.116463, "0:59"],
    [3600, "1:00:00"],
  ])("formats %s seconds as %s for the announced value", (time, expected) => {
    const { attributes } = setup(time)

    expect(attributes.value["aria-valuetext"]).toBe(expected)
  })

  it("updates the announced value when the playback position changes", () => {
    const { attributes, currentTime } = setup()

    expect(attributes.value["aria-valuetext"]).toBe("0:00")

    currentTime.value = 60.116463
    expect(attributes.value["aria-valuetext"]).toBe("1:00")

    currentTime.value = 59.116463
    expect(attributes.value["aria-valuetext"]).toBe("0:59")
  })

  it("preserves precision in numeric ARIA values and seek fractions", () => {
    const { attributes, meta, currentTime, duration } = setup(59.116463)

    expect(attributes.value["aria-valuenow"]).toBe(currentTime.value)
    expect(attributes.value["aria-valuemax"]).toBe(duration.value)
    expect(meta.currentFrac.value).toBe(currentTime.value / duration.value)
  })

  it.each<[string, number]>([
    ["Home", 0],
    ["End", 1],
    ["ArrowLeft", 58.116463 / 60.116463],
    ["ArrowRight", 60.116463 / 60.116463],
  ])("preserves seeking with %s", (key, expectedFraction) => {
    const { listeners, onSeek } = setup(59.116463)
    const event = new KeyboardEvent("keydown", {
      key,
      cancelable: true,
    })

    listeners.keydown(event)

    expect(event.defaultPrevented).toBe(true)
    expect(onSeek).toHaveBeenCalledOnce()
    expect(onSeek.mock.calls[0][0]).toBeCloseTo(expectedFraction)
  })
})
