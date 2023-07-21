import { useSensitiveMedia } from "~/composables/use-sensitive-media"

let mockUseUiStore = {
  shouldBlurSensitive: true,
  revealedSensitiveResults: [],
}

jest.mock("~/stores/ui", () => ({
  useUiStore: () => mockUseUiStore,
}))

describe("useSensitiveMedia composable", () => {
  let mockMedia: { id: string; isSensitive: boolean }

  beforeEach(() => {
    mockMedia = {
      id: "mock-id",
      isSensitive: false,
    }
    mockUseUiStore = {
      shouldBlurSensitive: true,
      revealedSensitiveResults: [],
    }
  })

  it("should return insensitive when media is null", () => {
    const { visibility } = useSensitiveMedia(null)
    expect(visibility.value).toBe("insensitive")
  })

  it("should return insensitive when media is not sensitive", () => {
    const { visibility } = useSensitiveMedia(mockMedia)
    expect(visibility.value).toBe("insensitive")
  })

  it("should return sensitive-hidden when media is sensitive and shouldBlurSensitive is true", () => {
    mockMedia.isSensitive = true
    const { visibility } = useSensitiveMedia(mockMedia)
    expect(visibility.value).toBe("sensitive-hidden")
  })

  it("should return sensitive-shown when media is sensitive and shouldBlurSensitive is false", () => {
    mockMedia.isSensitive = true
    mockUseUiStore.shouldBlurSensitive = false

    const { visibility } = useSensitiveMedia(mockMedia)
    expect(visibility.value).toBe("sensitive-shown")
  })

  it("should reveal sensitive media", () => {
    mockMedia.isSensitive = true
    const { reveal, visibility } = useSensitiveMedia(mockMedia)
    reveal()
    expect(visibility.value).toBe("sensitive-shown")
  })

  it("should hide sensitive media", () => {
    mockMedia.isSensitive = true
    const { reveal, hide, visibility } = useSensitiveMedia(mockMedia)
    reveal()
    hide()
    expect(visibility.value).toBe("sensitive-hidden")
  })

  it("should correctly report if a media is hidden", () => {
    mockMedia.isSensitive = true
    const { reveal, hide, isHidden } = useSensitiveMedia(mockMedia)
    reveal()
    hide()
    expect(isHidden.value).toBe(true)
  })

  it("should correctly report if a media can be hidden", () => {
    mockMedia.isSensitive = true
    mockUseUiStore.shouldBlurSensitive = false

    const { reveal, canBeHidden } = useSensitiveMedia(mockMedia)
    reveal()
    expect(canBeHidden.value).toBe(false)
  })
})
