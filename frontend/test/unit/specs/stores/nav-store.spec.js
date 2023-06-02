import { setActivePinia, createPinia } from "~~/test/unit/test-utils/pinia"

import { useNavigationStore } from "~/stores/navigation"

const initialState = {
  isReferredFromCc: false,
}

describe("Nav Store", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })
  it("sets the initial state correctly", () => {
    const navigationStore = useNavigationStore()
    expect(navigationStore.isReferredFromCc).toEqual(
      initialState.isReferredFromCc
    )
  })

  it.each([true, false, undefined])(
    "sets isReferredFromCc",
    (isReferredFromCc) => {
      const navigationStore = useNavigationStore()
      navigationStore.setIsReferredFromCc(isReferredFromCc)
      const expectedValue = isReferredFromCc ?? true

      expect(navigationStore.isReferredFromCc).toEqual(expectedValue)
    }
  )
})
