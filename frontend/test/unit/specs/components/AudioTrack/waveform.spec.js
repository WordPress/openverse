// vitest-environment jsdom
import { render } from "~~/test/unit/test-utils/render"

import VWaveform from "~/components/VAudioTrack/VWaveform.vue"

vi.mock("~/utils/resampling", () => {
  return {
    downsampleArray: vi.fn((data) => data),
    upsampleArray: vi.fn((data) => data),
  }
})

describe("VWaveform", () => {
  let options = null
  let props = null

  beforeEach(() => {
    props = {
      peaks: [],
      audioId: "test",
    }

    options = { props }
  })

  it("should use given peaks when peaks array is provided", async () => {
    const peaksCount = 5
    props.peaks = Array.from({ length: peaksCount }, () => 0)
    const { container } = await render(VWaveform, options)
    // There is also a yellow "played" rectangle
    expect(container.querySelectorAll("rect").length).toBe(peaksCount + 1)
  })

  it("should use random peaks when peaks not set", async () => {
    const peaksCount = 100
    const { container } = await render(VWaveform, options)
    expect(container.querySelectorAll("rect")).toHaveLength(peaksCount + 1)
  })

  it("should use random peaks when peaks array is blank", async () => {
    const peaksCount = 100
    props.peaks = null
    const { container } = await render(VWaveform, options)
    expect(container.querySelectorAll("rect")).toHaveLength(peaksCount + 1)
  })
})
