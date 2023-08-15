import { setActivePinia, createPinia } from "~~/test/unit/test-utils/pinia"

import { useUiStore } from "~/stores/ui"

const initialState = {
  instructionsSnackbarState: "not_shown",
  innerFilterVisible: false,
  isFilterDismissed: false,
  isDesktopLayout: false,
  isMobileUa: true,
  dismissedBanners: [],
}

const VISIBLE_AND_DISMISSED = {
  innerFilterVisible: true,
  isFilterDismissed: true,
}
const NOT_VISIBLE_AND_DISMISSED = {
  innerFilterVisible: false,
  isFilterDismissed: true,
}
const VISIBLE_AND_NOT_DISMISSED = {
  innerFilterVisible: true,
  isFilterDismissed: false,
}
const NOT_VISIBLE_AND_NOT_DISMISSED = {
  innerFilterVisible: false,
  isFilterDismissed: false,
}

const cookieOptions = {
  maxAge: 5184000,
  path: "/",
  sameSite: "strict",
  secure: false,
}

describe("Ui Store", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })
  describe("state", () => {
    it("sets the initial state correctly", () => {
      const uiStore = useUiStore()
      for (const key of Object.keys(initialState)) {
        expect(uiStore[key]).toEqual(initialState[key])
      }
    })
  })

  describe("getters", () => {
    test.each`
      status         | isVisible
      ${"not_shown"} | ${false}
      ${"visible"}   | ${true}
      ${"dismissed"} | ${false}
    `(
      "areInstructionsVisible return $isVisible when status is $status",
      ({ status, isVisible }) => {
        const uiStore = useUiStore()
        uiStore.$patch({ instructionsSnackbarState: status })

        expect(uiStore.areInstructionsVisible).toEqual(isVisible)
      }
    )

    test.each`
      isDesktopLayout | innerFilterVisible | isFilterDismissed | isVisible
      ${true}         | ${true}            | ${true}           | ${true}
      ${true}         | ${true}            | ${false}          | ${true}
      ${true}         | ${false}           | ${true}           | ${false}
      ${true}         | ${false}           | ${false}          | ${true}
      ${false}        | ${true}            | ${true}           | ${true}
      ${false}        | ${true}            | ${false}          | ${true}
      ${false}        | ${false}           | ${true}           | ${false}
      ${false}        | ${false}           | ${false}          | ${false}
    `(
      "isFilterVisible return $isVisible when isDesktopLayout is $isDesktopLayout, innerFilterVisible is $innerFilterVisible, and isFilterDismissed is $isFilterDismissed",
      ({
        innerFilterVisible,
        isFilterDismissed,
        isDesktopLayout,
        isVisible,
      }) => {
        const uiStore = useUiStore()
        uiStore.$patch({
          isDesktopLayout,
          innerFilterVisible,
          isFilterDismissed,
        })

        expect(uiStore.isFilterVisible).toEqual(isVisible)
      }
    )
  })

  describe("actions", () => {
    it("initFromCookies sets initial state without cookie", () => {
      const uiStore = useUiStore()
      uiStore.initFromCookies({})
      for (const key of Object.keys(initialState)) {
        // isMobileUa is set to true only if we explicitly get a mobile UA
        // from cookie or the browser request
        const exepectedStoreValue =
          key === "isMobileUa" ? false : initialState[key]
        expect(uiStore[key]).toEqual(exepectedStoreValue)
      }
    })

    it("initFromCookies sets initial state with a desktop cookie", () => {
      const uiStore = useUiStore()
      uiStore.initFromCookies({
        uiBreakpoint: "lg",
        uiIsFilterDismissed: true,
      })

      expect(uiStore.instructionsSnackbarState).toEqual("not_shown")
      expect(uiStore.breakpoint).toEqual("lg")
      expect(uiStore.isDesktopLayout).toEqual(true)
      expect(uiStore.isMobileUa).toEqual(false)
      expect(uiStore.isFilterVisible).toEqual(false)
      expect(uiStore.isFilterDismissed).toEqual(true)
    })

    it("initFromCookies sets initial state with a mobile cookie", () => {
      const uiStore = useUiStore()
      uiStore.initFromCookies({
        uiIsMobileUa: true,
        uiIsFilterDismissed: false,
      })

      expect(uiStore.instructionsSnackbarState).toEqual("not_shown")
      expect(uiStore.isDesktopLayout).toEqual(false)
      expect(uiStore.breakpoint).toEqual("sm")
      expect(uiStore.isMobileUa).toEqual(true)
      expect(uiStore.isFilterDismissed).toEqual(false)
      expect(uiStore.isFilterVisible).toEqual(false)
    })

    it("initFromCookies sets initial state with a dismissed banner", () => {
      const uiStore = useUiStore()
      const dismissedBanners = ["ru", "ar"]
      uiStore.initFromCookies({
        uiDismissedBanners: dismissedBanners,
      })

      expect(uiStore.dismissedBanners).toEqual(dismissedBanners)
    })
  })

  test.each`
    before         | after
    ${"not_shown"} | ${"visible"}
    ${"visible"}   | ${"visible"}
    ${"dismissed"} | ${"dismissed"}
  `(
    "showInstructionsSnackbar changes instructionsSnackbarState from $before to $after",
    ({ before, after }) => {
      const uiStore = useUiStore()
      uiStore.$patch({ instructionsSnackbarState: before })
      uiStore.showInstructionsSnackbar()

      expect(uiStore.instructionsSnackbarState).toEqual(after)
    }
  )

  test.each`
    before         | after
    ${"not_shown"} | ${"not_shown"}
    ${"visible"}   | ${"not_shown"}
    ${"dismissed"} | ${"dismissed"}
  `(
    "hideInstructionsSnackbar changes instructionsSnackbarState from $before to $after",
    ({ before, after }) => {
      const uiStore = useUiStore()
      uiStore.$patch({ instructionsSnackbarState: before })
      uiStore.hideInstructionsSnackbar()

      expect(uiStore.instructionsSnackbarState).toEqual(after)
    }
  )

  test.each`
    initialState     | breakpoint | expected
    ${[true, false]} | ${"xm"}    | ${{ isDesktopLayout: false, isMobileUa: false }}
    ${[false, true]} | ${"lg"}    | ${{ isDesktopLayout: true, isMobileUa: true }}
  `(
    "updateBreakpoint gets breakpoint $breakpoint and returns $expected",
    ({ initialState, breakpoint, expected }) => {
      const uiStore = useUiStore()
      uiStore.$patch({
        isDesktopLayout: initialState[0],
        isMobileUa: initialState[1],
      })
      uiStore.updateBreakpoint(breakpoint)
      const actualOutput = {
        isDesktopLayout: uiStore.isDesktopLayout,
        isMobileUa: uiStore.isMobileUa,
      }

      expect(actualOutput).toEqual(expected)
    }
  )

  test.each`
    isDesktopLayout | currentState                     | visible  | expectedState
    ${true}         | ${VISIBLE_AND_NOT_DISMISSED}     | ${true}  | ${VISIBLE_AND_NOT_DISMISSED}
    ${true}         | ${VISIBLE_AND_DISMISSED}         | ${false} | ${NOT_VISIBLE_AND_DISMISSED}
    ${true}         | ${NOT_VISIBLE_AND_DISMISSED}     | ${true}  | ${VISIBLE_AND_NOT_DISMISSED}
    ${true}         | ${NOT_VISIBLE_AND_DISMISSED}     | ${false} | ${NOT_VISIBLE_AND_DISMISSED}
    ${false}        | ${VISIBLE_AND_NOT_DISMISSED}     | ${true}  | ${VISIBLE_AND_NOT_DISMISSED}
    ${false}        | ${VISIBLE_AND_NOT_DISMISSED}     | ${false} | ${NOT_VISIBLE_AND_NOT_DISMISSED}
    ${false}        | ${NOT_VISIBLE_AND_NOT_DISMISSED} | ${true}  | ${VISIBLE_AND_NOT_DISMISSED}
    ${false}        | ${NOT_VISIBLE_AND_DISMISSED}     | ${true}  | ${VISIBLE_AND_DISMISSED}
    ${false}        | ${NOT_VISIBLE_AND_DISMISSED}     | ${false} | ${NOT_VISIBLE_AND_DISMISSED}
  `(
    "setFiltersState sets state to $expectedState when visible is $visible and isDesktopLayout is $isDesktopLayout",
    ({ isDesktopLayout, currentState, visible, expectedState }) => {
      const uiStore = useUiStore()
      uiStore.$patch({
        isDesktopLayout,
        ...currentState,
      })

      uiStore.setFiltersState(visible)

      expect(uiStore.isFilterVisible).toEqual(expectedState.innerFilterVisible)
      expect(uiStore.isFilterDismissed).toEqual(expectedState.isFilterDismissed)
    }
  )

  test.each`
    isDesktopLayout | currentState                     | expectedState
    ${true}         | ${VISIBLE_AND_NOT_DISMISSED}     | ${NOT_VISIBLE_AND_DISMISSED}
    ${true}         | ${VISIBLE_AND_DISMISSED}         | ${NOT_VISIBLE_AND_DISMISSED}
    ${true}         | ${NOT_VISIBLE_AND_DISMISSED}     | ${VISIBLE_AND_NOT_DISMISSED}
    ${true}         | ${NOT_VISIBLE_AND_DISMISSED}     | ${VISIBLE_AND_NOT_DISMISSED}
    ${false}        | ${VISIBLE_AND_NOT_DISMISSED}     | ${NOT_VISIBLE_AND_NOT_DISMISSED}
    ${false}        | ${NOT_VISIBLE_AND_NOT_DISMISSED} | ${VISIBLE_AND_NOT_DISMISSED}
    ${false}        | ${NOT_VISIBLE_AND_DISMISSED}     | ${VISIBLE_AND_DISMISSED}
    ${false}        | ${VISIBLE_AND_NOT_DISMISSED}     | ${NOT_VISIBLE_AND_NOT_DISMISSED}
    ${false}        | ${NOT_VISIBLE_AND_DISMISSED}     | ${VISIBLE_AND_DISMISSED}
  `(
    "toggleFilters sets state to $expectedState when isDesktopLayout is $isDesktopLayout",
    ({ isDesktopLayout, currentState, expectedState }) => {
      const uiStore = useUiStore()
      uiStore.$patch({
        isDesktopLayout,
        ...currentState,
      })

      uiStore.toggleFilters()

      expect(uiStore.isFilterVisible).toEqual(expectedState.innerFilterVisible)
      expect(uiStore.isFilterDismissed).toEqual(expectedState.isFilterDismissed)
    }
  )
  it.each`
    originalState | bannerId | expectedState   | areCookiesSet
    ${[]}         | ${"es"}  | ${["es"]}       | ${true}
    ${["es"]}     | ${"es"}  | ${["es"]}       | ${false}
    ${["es"]}     | ${"de"}  | ${["es", "de"]} | ${true}
  `(
    "dismissBanner($bannerId): $originalState -> $expectedState",
    ({ originalState, bannerId, expectedState, areCookiesSet }) => {
      const uiStore = useUiStore()
      uiStore.$patch({ dismissedBanners: originalState })
      uiStore.dismissBanner(bannerId)

      expect(uiStore.dismissedBanners).toEqual(expectedState)
      if (areCookiesSet) {
        // eslint-disable-next-line jest/no-conditional-expect
        expect(uiStore.$nuxt.$cookies.set).toHaveBeenCalledWith(
          "uiDismissedBanners",
          expectedState,
          cookieOptions
        )
      }
    }
  )
  it.each`
    originalState | bannerId | expectedState
    ${[]}         | ${"es"}  | ${false}
    ${["es"]}     | ${"es"}  | ${true}
    ${["es"]}     | ${"de"}  | ${false}
  `(
    "isBannerDismissed($bannerId) for $originalState returns $expectedState",
    ({ originalState, bannerId, expectedState }) => {
      const uiStore = useUiStore()
      uiStore.$patch({ dismissedBanners: originalState })

      expect(uiStore.isBannerDismissed(bannerId)).toEqual(expectedState)
    }
  )
})
