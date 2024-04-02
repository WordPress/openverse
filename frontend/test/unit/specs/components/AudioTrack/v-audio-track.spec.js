import { fireEvent } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"
import { getAudioObj } from "~~/test/unit/fixtures/audio"

import { useActiveMediaStore } from "~/stores/active-media"

import VAudioTrack from "~/components/VAudioTrack/VAudioTrack.vue"

window.HTMLMediaElement.prototype.play = () => {
  /* mock */
}

jest.mock("~/composables/use-match-routes", () => ({
  // mocking `Ref<boolean>` as `{ value: boolean }`
  useMatchSearchRoutes: jest.fn(() => ({ matches: { value: false } })),
  useMatchSingleResultRoutes: jest.fn(() => ({ matches: { value: false } })),
}))

const stubs = {
  VLicense: true,
  VWaveform: true,
  VAudioThumbnail: true,
}

describe("AudioTrack", () => {
  let options = null
  let props = null
  let configureVue = null
  let captureExceptionMock = jest.fn()

  beforeEach(() => {
    props = {
      audio: getAudioObj(),
    }
    configureVue = (localVue, options) => {
      const activeMediaStore = useActiveMediaStore(options.pinia)
      activeMediaStore.$patch({
        state: {
          type: "audio",
          id: "e19345b8-6937-49f7-a0fd-03bf057efc28",
          message: null,
          state: "paused",
        },
      })
      activeMediaStore.$nuxt.$sentry = {
        captureException: captureExceptionMock,
      }
    }

    options = {
      propsData: props,
      stubs,
    }
  })

  it("should render the full audio track component even without duration", () => {
    options.propsData.layout = "full"
    const { getByText } = render(VAudioTrack, options, configureVue)
    const creator = getByText(props.audio.creator)
    expect(creator).toBeInstanceOf(HTMLAnchorElement)
  })

  it("should show audio title as main page title in full layout", () => {
    options.propsData.layout = "full"
    const { getByText } = render(VAudioTrack, options, configureVue)
    // Title text appears multiple times in the track, so need to specify selector
    const element = getByText(props.audio.title, { selector: "H1" })
    expect(element).toBeInTheDocument()
  })

  it("should show audio creator in a full layout with link", () => {
    options.propsData.layout = "full"
    const { getByText } = render(VAudioTrack, options, configureVue)
    const element = getByText(props.audio.creator)
    expect(element).toBeInstanceOf(HTMLAnchorElement)
    expect(element).toHaveAttribute("href", props.audio.creator_url)
  })

  it("should render the row audio track component even without duration", () => {
    options.propsData.layout = "row"
    const { getByText } = render(VAudioTrack, options, configureVue)
    const creator = getByText("by " + props.audio.creator)
    expect(creator).toBeTruthy()
  })

  it.each`
    errorType              | errorText
    ${"NotAllowedError"}   | ${/Reproduction not allowed./i}
    ${"NotSupportedError"} | ${/This audio format is not supported by your browser./i}
    ${"AbortError"}        | ${/You aborted playback./i}
    ${"UnknownError"}      | ${/An unexpected error has occurred./i}
  `(
    "on play error displays a message instead of the waveform",
    async ({ errorType, errorText }) => {
      options.propsData.audio.url = "bad.url"
      options.propsData.layout = "row"
      options.stubs.VWaveform = false
      options.stubs.VAudioThumbnail = true

      jest.clearAllMocks()

      const pauseStub = jest
        .spyOn(window.HTMLMediaElement.prototype, "pause")
        .mockImplementation(() => undefined)

      const playError = new DOMException("msg", errorType)

      const playStub = jest
        .spyOn(window.HTMLMediaElement.prototype, "play")
        .mockImplementation(() => Promise.reject(playError))

      const { getByRole, getByText } = render(
        VAudioTrack,
        options,
        configureVue
      )

      await fireEvent.click(getByRole("button"))
      expect(playStub).toHaveBeenCalledTimes(1)
      expect(pauseStub).toHaveBeenCalledTimes(1)
      expect(getByText(errorText)).toBeVisible()

      // Only the UnknownError should be sent to Sentry.
      if (errorType === "UnknownError") {
        // eslint-disable-next-line jest/no-conditional-expect
        expect(captureExceptionMock).toHaveBeenCalledWith(playError)
      } else {
        // eslint-disable-next-line jest/no-conditional-expect
        expect(captureExceptionMock).not.toHaveBeenCalled()
      }
    }
  )

  it("has blurred title in box layout when audio is sensitive", async () => {
    options.propsData.audio.isSensitive = true
    options.propsData.layout = "box"
    options.propsData.size = "large"
    const { getByText } = render(VAudioTrack, options, configureVue)
    const h2 = getByText("This audio track may contain sensitive content.")
    expect(h2).toHaveClass("blur-text")
  })

  it("has blurred info in row layout when audio is sensitive", async () => {
    options.propsData.audio.isSensitive = true
    options.propsData.layout = "row"
    const { getByText } = render(VAudioTrack, options, configureVue)

    const h2 = getByText("This audio track may contain sensitive content.")
    expect(h2).toHaveClass("blur-text")

    const creator = getByText("by Creator")
    expect(creator).toHaveClass("blur-text")
  })

  it("is does not contain title or creator anywhere when the audio is sensitive", async () => {
    options.propsData.audio.isSensitive = true
    options.propsData.layout = "row"
    const screen = render(VAudioTrack, options, configureVue)
    let { title, creator } = options.propsData.audio
    let match = RegExp(`(${title}|${creator})`)
    expect(screen.queryAllByText(match)).toEqual([])
    expect(screen.queryAllByTitle(match)).toEqual([])
    expect(screen.queryAllByAltText(match)).toEqual([])
  })
})
