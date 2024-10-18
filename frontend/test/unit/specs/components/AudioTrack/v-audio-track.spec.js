import { fireEvent } from "@testing-library/vue"

import { createApp } from "vue"

import { render } from "~~/test/unit/test-utils/render"

import { i18n } from "~~/test/unit/test-utils/i18n"
import { getAudioObj } from "~~/test/unit/fixtures/audio"

import { useActiveMediaStore } from "~/stores/active-media"

import VAudioTrack from "~/components/VAudioTrack/VAudioTrack.vue"

window.HTMLMediaElement.prototype.play = () => {
  /* mock */
}

const RouterLinkStub = createApp({}).component("RouterLink", {
  template: "<a :href='href'><slot /></a>",
  props: ["to"],
  computed: {
    href() {
      return this.to
    },
  },
})._context.components.RouterLink
const stubs = {
  VLicense: true,
  VWaveform: true,
  VAudioThumbnail: true,
  RouterLink: RouterLinkStub,
}

describe("AudioTrack", () => {
  let options = null
  let props = null
  let captureExceptionMock = vi.fn()

  beforeEach(() => {
    props = {
      audio: getAudioObj(),
      layout: "full",
    }
    const activeMediaStore = useActiveMediaStore()
    activeMediaStore.$patch({
      state: {
        type: "audio",
        id: "e19345b8-6937-49f7-a0fd-03bf057efc28",
        message: null,
        state: "paused",
      },
    })

    options = {
      props: props,
      global: {
        plugins: [i18n],
        stubs,
      },
    }
  })

  it("should render the full audio track component even without duration", async () => {
    options.props.layout = "full"
    const { getByRole } = await render(VAudioTrack, options)
    const creator = getByRole("link", { name: props.audio.creator })
    expect(creator).toBeVisible()
  })

  it("should show audio title as main page title in full layout", async () => {
    options.props.layout = "full"
    const { getByRole } = await render(VAudioTrack, options)
    // Title text appears multiple times in the track, so need to specify selector
    const element = getByRole("heading", { level: 1 })
    expect(element).toBeInTheDocument()
    expect(element).toHaveTextContent(props.audio.title)
  })

  it("should show audio creator in a full layout with link", async () => {
    options.props.layout = "full"
    const { getByRole } = await render(VAudioTrack, options)
    const element = getByRole("link", { name: props.audio.creator })
    expect(element).toBeVisible()
    expect(element).toHaveAttribute(
      "href",
      `/audio/collection?source=jamendo&creator=${props.audio.creator}`
    )
  })

  it("should render the row audio track component even without duration", async () => {
    options.props.layout = "row"
    const { getByText } = await render(VAudioTrack, options)
    const creator = getByText("by " + props.audio.creator)
    expect(creator).toBeTruthy()
  })

  // https://github.com/wordpress/openverse/issues/411
  it.skip.each`
    errorType              | errorText
    ${"NotAllowedError"}   | ${/Reproduction not allowed./i}
    ${"NotSupportedError"} | ${/This audio format is not supported by your browser./i}
    ${"AbortError"}        | ${/You aborted playback./i}
    ${"UnknownError"}      | ${/An unexpected error has occurred./i}
  `(
    "on play error displays a message instead of the waveform",
    async ({ errorType, errorText }) => {
      options.props.audio.url = "bad.url"
      options.props.layout = "row"
      options.global.stubs.VWaveform = false
      options.global.stubs.VAudioThumbnail = true

      vi.clearAllMocks()

      const pauseStub = vi
        .spyOn(window.HTMLMediaElement.prototype, "pause")
        .mockImplementation(() => undefined)

      const playError = new DOMException("msg", errorType)

      const playStub = vi
        .spyOn(window.HTMLMediaElement.prototype, "play")
        .mockImplementation(() => Promise.reject(playError))

      const { getByRole, getByText } = await render(VAudioTrack, options)

      await fireEvent.click(getByRole("button"))
      expect(playStub).toHaveBeenCalledTimes(1)
      expect(pauseStub).toHaveBeenCalledTimes(1)
      expect(getByText(errorText)).toBeVisible()

      // Only the UnknownError should be sent to Sentry.
      if (errorType === "UnknownError") {
        expect(captureExceptionMock).toHaveBeenCalledWith(playError)
      } else {
        expect(captureExceptionMock).not.toHaveBeenCalled()
      }
    }
  )

  it("has blurred title in box layout when audio is sensitive", async () => {
    options.props.audio.isSensitive = true
    options.props.layout = "box"
    options.props.size = "large"
    const { getByText } = await render(VAudioTrack, options)
    const h2 = getByText("This audio track may contain sensitive content.")
    expect(h2).toHaveClass("blur-text")
  })

  it("has blurred info in row layout when audio is sensitive", async () => {
    options.props.audio.isSensitive = true
    options.props.layout = "row"
    const { getByText } = await render(VAudioTrack, options)

    const h2 = getByText("This audio track may contain sensitive content.")
    expect(h2).toHaveClass("blur-text")

    const creator = getByText("by Creator")
    expect(creator).toHaveClass("blur-text")
  })

  it("is does not contain title or creator anywhere when the audio is sensitive", async () => {
    options.props.audio.isSensitive = true
    options.props.layout = "row"
    const screen = await render(VAudioTrack, options)
    let { title, creator } = options.props.audio
    let match = RegExp(`(${title}|${creator})`)
    expect(screen.queryAllByText(match)).toEqual([])
    expect(screen.queryAllByTitle(match)).toEqual([])
    expect(screen.queryAllByAltText(match)).toEqual([])
  })
})
