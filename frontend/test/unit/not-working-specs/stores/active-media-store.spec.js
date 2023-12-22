import { setActivePinia, createPinia } from "~~/test/unit/test-utils/pinia"

import { AUDIO } from "~/constants/media"

import { useActiveMediaStore } from "~/stores/active-media"

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
})
