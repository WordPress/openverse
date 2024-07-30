import { beforeEach, describe, expect, it, vi } from "vitest"

import { useSensitiveMedia } from "~/composables/use-sensitive-media"
import type { Sensitivity } from "~/constants/content-safety"

let mockUseUiStore = {
  shouldBlurSensitive: true,
  revealedSensitiveResults: [],
}

vi.resetModules()

vi.mock("#app/nuxt", async () => {
  const original = await import("#app/nuxt")
  return {
    ...original,
    useNuxtApp: vi.fn(() => ({
      $sendCustomEvent: vi.fn(),
    })),
  }
})

vi.mock("~/stores/ui", () => ({
  useUiStore: () => mockUseUiStore,
}))

describe("useSensitiveMedia composable", () => {
  const sendCustomEventMock = vi.fn()

  let mockMedia: {
    id: string
    sensitivity: Sensitivity[]
    isSensitive: boolean
  }

  beforeEach(() => {
    mockMedia = {
      id: "mock-id",
      sensitivity: [],
      isSensitive: false,
    }
    mockUseUiStore = {
      shouldBlurSensitive: true,
      revealedSensitiveResults: [],
    }

    sendCustomEventMock.mockClear()
  })

  it("should return non-sensitive when media is null", async () => {
    const { visibility } = useSensitiveMedia(null)
    expect(visibility.value).toBe("non-sensitive")
  })

  it("should return non-sensitive when media is not sensitive", async () => {
    const { visibility } = useSensitiveMedia(mockMedia)
    expect(visibility.value).toBe("non-sensitive")
  })

  it("should return sensitive-hidden when media is sensitive and shouldBlurSensitive is true", async () => {
    mockMedia.isSensitive = true

    const { visibility } = useSensitiveMedia(mockMedia)
    expect(visibility.value).toBe("sensitive-hidden")
  })

  it("should return sensitive-shown when media is sensitive and shouldBlurSensitive is false", async () => {
    mockMedia.isSensitive = true
    mockUseUiStore.shouldBlurSensitive = false

    const { visibility } = useSensitiveMedia(mockMedia)
    expect(visibility.value).toBe("sensitive-shown")
  })

  it("should correctly report if a media is hidden", async () => {
    mockMedia.isSensitive = true

    const { reveal, hide, isHidden } = useSensitiveMedia(mockMedia)
    reveal()
    hide()

    expect(isHidden.value).toBe(true)
  })

  it("should correctly report if a media can be hidden", async () => {
    mockMedia.isSensitive = true
    mockUseUiStore.shouldBlurSensitive = false

    const { reveal, canBeHidden } = useSensitiveMedia(mockMedia)
    reveal()

    expect(canBeHidden.value).toBe(false)
  })
})
