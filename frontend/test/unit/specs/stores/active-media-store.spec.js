import { describe, expect, it, vi, beforeEach } from "vitest"
import { setActivePinia, createPinia } from "~~/test/unit/test-utils/pinia"

import { AUDIO } from "#shared/constants/media"
import { audioErrorMessages } from "#shared/constants/audio"
import { warn } from "~/utils/console"
import { useActiveMediaStore } from "~/stores/active-media"

const mockCaptureException = vi.fn()

vi.mock("#app/nuxt", () => ({
  useNuxtApp: () => ({
    $captureException: mockCaptureException,
  }),
}))

vi.mock("~/utils/console", () => ({
  warn: vi.fn(),
}))

const initialState = { type: null, id: null, status: "ejected", message: null }
const statuses = ["ejected", "paused", "playing"]

describe("Active Media Store", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe("state", () => {
    it("sets initial filters to filterData", () => {
      const activeMediaStore = useActiveMediaStore()
      expect(activeMediaStore.type).toEqual(initialState.type)
      expect(activeMediaStore.id).toEqual(initialState.id)
      expect(activeMediaStore.status).toEqual(initialState.status)
      expect(activeMediaStore.message).toEqual(initialState.message)
    })
  })

  describe("actions", () => {
    it.each(statuses)(`can set active media with status $status`, (status) => {
      const activeMediaStore = useActiveMediaStore()
      const mediaItem = { type: AUDIO, id: "audio1" }
      activeMediaStore.setActiveMediaItem({ ...mediaItem, status })
      const expectedState = { ...initialState, ...mediaItem, status }

      expect(activeMediaStore.id).toEqual(expectedState.id)
      expect(activeMediaStore.type).toEqual(expectedState.type)
      expect(activeMediaStore.status).toEqual(expectedState.status)
    })

    it.each(statuses)("can pause an item with any status", (status) => {
      const activeMediaStore = useActiveMediaStore()
      activeMediaStore.setActiveMediaItem({ status })
      activeMediaStore.pauseActiveMediaItem()

      expect(activeMediaStore.status).toBe("paused")
    })

    it("can eject an item", () => {
      const activeMediaStore = useActiveMediaStore()

      activeMediaStore.setActiveMediaItem({
        type: AUDIO,
        id: "audio1",
        status: "playing",
      })
      activeMediaStore.ejectActiveMediaItem()

      expect(activeMediaStore.id).toEqual(initialState.id)
      expect(activeMediaStore.type).toEqual(initialState.type)
      expect(activeMediaStore.status).toEqual(initialState.status)
    })

    it("can set a message", () => {
      const activeMediaStore = useActiveMediaStore()
      const expectedMessage = "Cannot play this audio"
      activeMediaStore.setMessage({ message: expectedMessage })
      expect(activeMediaStore.message).toEqual(expectedMessage)
    })
  })

  describe("playAudio", () => {
    it("should handle undefined audio element", () => {
      const activeMediaStore = useActiveMediaStore()

      const playFn = vi.fn().mockReturnValue(undefined)
      const mockAudio = {
        play: playFn,
      }

      activeMediaStore.playAudio(mockAudio)

      expect(warn).toHaveBeenCalledWith("Play promise is undefined")
    })

    it("should handle successful play", async () => {
      const activeMediaStore = useActiveMediaStore()
      const playFn = vi.fn().mockResolvedValue()
      const mockAudio = {
        play: playFn,
        pause: vi.fn(),
      }

      activeMediaStore.playAudio(mockAudio)

      await vi.waitFor(() => {
        expect(playFn).toHaveBeenCalled()
        expect(mockAudio.pause).not.toHaveBeenCalled()
        expect(activeMediaStore.message).toBeNull()
      })
    })

    it.each(Object.keys(audioErrorMessages))(
      "should handle known error: %s",
      async (errorName) => {
        const activeMediaStore = useActiveMediaStore()
        const error = new DOMException("Msg", errorName)
        const playFn = vi.fn().mockRejectedValue(error)
        const mockAudio = {
          play: playFn,
          pause: vi.fn(),
        }

        activeMediaStore.playAudio(mockAudio)

        await vi.waitFor(() => {
          expect(playFn).toHaveBeenCalled()
          expect(mockAudio.pause).toHaveBeenCalled()
          expect(activeMediaStore.message).toBe(audioErrorMessages[errorName])
          expect(mockCaptureException).not.toHaveBeenCalled()
        })
      }
    )

    it("should handle unknown error", async () => {
      const activeMediaStore = useActiveMediaStore()
      const unknownError = new Error()
      unknownError.name = "UnknownError"
      const playFn = vi.fn().mockRejectedValue(unknownError)
      const mockAudio = {
        play: playFn,
        pause: vi.fn(),
      }

      activeMediaStore.playAudio(mockAudio)

      await vi.waitFor(() => {
        expect(playFn).toHaveBeenCalled()
        expect(mockAudio.pause).toHaveBeenCalled()
        expect(activeMediaStore.message).toBe("err_unknown")
        expect(mockCaptureException).toHaveBeenCalledWith(unknownError)
      })
    })
  })
})
