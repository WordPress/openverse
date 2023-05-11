import { render } from "~~/test/unit/test-utils/render"

import VWaveform from "~/components/VAudioTrack/VWaveform.vue"

jest.mock("~/utils/resampling", () => {
  return {
    downsampleArray: jest.fn((data) => data),
    upsampleArray: jest.fn((data) => data),
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

    options = {
      propsData: props,
    }
  })

  it("should use given peaks when peaks array is provided", () => {
    const peaksCount = 5
    props.peaks = Array.from({ length: peaksCount }, () => 0)
    const { container } = render(VWaveform, options)
    // There is also a yellow "played" rectangle
    expect(container.querySelectorAll("rect").length).toBe(peaksCount + 1)
  })

  it("should use random peaks when peaks not set", () => {
    const peaksCount = 100
    const { container } = render(VWaveform, options)
    expect(container.querySelectorAll("rect")).toHaveLength(peaksCount + 1)
  })

  it("should use random peaks when peaks array is blank", () => {
    const peaksCount = 100
    props.peaks = null
    const { container } = render(VWaveform, options)
    expect(container.querySelectorAll("rect")).toHaveLength(peaksCount + 1)
  })
})
