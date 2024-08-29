import { nextTick } from "vue"

import { setActivePinia, createPinia } from "~~/test/unit/test-utils/pinia"

import { useUiStore } from "~/stores/ui"
import type { UiState } from "~/stores/ui"
import { defaultPersistientCookieState } from "~/types/cookies"
import { vi, describe, beforeEach, it, expect, test, afterAll } from "vitest"
import { BannerId } from "~/types/banners"

vi.mock("~/types/cookies", async () => {
  const actual =
    await vi.importActual<typeof import("~/types/cookies")>("~/types/cookies")
  return {
    ...actual,
    persistentCookieOptions: {
      ...actual.persistentCookieOptions,
      secure: false,
    },
  }
})

let initialState = { ...defaultPersistientCookieState.ui }

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

describe("Ui Store", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    console.log({ snackBar: initialState.instructionsSnackbarState })
  })

  describe("state", () => {
    it("sets the initial state correctly", () => {
      const uiStore = useUiStore()
      for (const key of Object.keys(initialState) as Array<keyof UiState>) {
        expect(uiStore[key]).toEqual(initialState[key])
      }
    })
  })

  describe("getters", () => {
    afterAll(() => {
      vi.clearAllMocks()
      vi.resetAllMocks()
      initialState = defaultPersistientCookieState.ui
    })

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
      for (const key of Object.keys(initialState) as Array<keyof UiState>) {
        expect(uiStore[key]).toEqual(initialState[key])
      }
    })

    it("initFromCookies sets initial state with a desktop cookie", () => {
      const uiStore = useUiStore()
      uiStore.initFromCookies({
        breakpoint: "lg",
        isFilterDismissed: true,
      })

      expect(uiStore.instructionsSnackbarState).toBe("not_shown")
      expect(uiStore.breakpoint).toBe("lg")
      expect(uiStore.isDesktopLayout).toBe(true)
      expect(uiStore.isFilterVisible).toBe(false)
      expect(uiStore.isFilterDismissed).toBe(true)
    })

    it("initFromCookies sets initial state with a dismissed banner", () => {
      const uiStore = useUiStore()
      const dismissedBanners: BannerId[] = ["translation-ru", "translation-ar"]
      uiStore.initFromCookies({
        dismissedBanners: dismissedBanners,
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
    initialState | breakpoint | expected
    ${true}      | ${"xs"}    | ${{ isDesktopLayout: false }}
    ${false}     | ${"lg"}    | ${{ isDesktopLayout: true }}
  `(
    "updateBreakpoint gets breakpoint $breakpoint and returns $expected",
    ({ initialState, breakpoint, expected }) => {
      const uiStore = useUiStore()
      uiStore.$patch({
        isDesktopLayout: initialState,
      })
      uiStore.updateBreakpoint(breakpoint)
      const actualOutput = {
        isDesktopLayout: uiStore.isDesktopLayout,
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
    "setFiltersState updates state %o",
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
    "toggleFilters updates state %o",
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
    originalState         | bannerId            | expectedState                           | areCookiesSet
    ${[]}                 | ${"translation-es"} | ${["translation-es"]}                   | ${true}
    ${["translation-es"]} | ${"translation-es"} | ${["translation-es"]}                   | ${false}
    ${["translation-es"]} | ${"translation-de"} | ${["translation-es", "translation-de"]} | ${true}
  `(
    "dismissBanner($bannerId): $originalState -> $expectedState",
    async ({ originalState, bannerId, expectedState, areCookiesSet }) => {
      const uiStore = useUiStore()
      uiStore.initFromCookies({})
      uiStore.$patch({ dismissedBanners: originalState })
      uiStore.dismissBanner(bannerId)

      await nextTick()

      const dismissedBannersCookie = document.cookie
        ? JSON.parse(decodeURIComponent(document.cookie.split("=")[1]))[
            "dismissedBanners"
          ]
        : []

      expect(uiStore.dismissedBanners).toEqual(expectedState)
      if (areCookiesSet) {
        expect(dismissedBannersCookie).toEqual(expectedState)
      }
    }
  )
  it.each`
    originalState         | bannerId            | expectedState
    ${[]}                 | ${"translation-es"} | ${false}
    ${["translation-es"]} | ${"translation-es"} | ${true}
    ${["translation-es"]} | ${"translation-de"} | ${false}
  `(
    "isBannerDismissed($bannerId) for $originalState returns $expectedState",
    ({ originalState, bannerId, expectedState }) => {
      const uiStore = useUiStore()
      uiStore.$patch({ dismissedBanners: originalState })

      expect(uiStore.isBannerDismissed(bannerId)).toEqual(expectedState)
    }
  )

  describe("actions", () => {
    it("initFromCookies sets initial state without cookie", () => {
      const uiStore = useUiStore()
      uiStore.initFromCookies({})
      for (const key of Object.keys(initialState) as Array<keyof UiState>) {
        expect(uiStore[key]).toEqual(initialState[key])
      }
    })

    it("initFromCookies sets initial state with a desktop cookie", () => {
      const uiStore = useUiStore()
      uiStore.initFromCookies({
        breakpoint: "lg",
        isFilterDismissed: true,
      })

      console.log(uiStore)

      expect(uiStore.instructionsSnackbarState).toBe("not_shown")
      expect(uiStore.breakpoint).toBe("lg")
      expect(uiStore.isDesktopLayout).toBe(true)
      expect(uiStore.isFilterVisible).toBe(false)
      expect(uiStore.isFilterDismissed).toBe(true)
    })

    it("initFromCookies sets initial state with a dismissed banner", () => {
      const uiStore = useUiStore()
      const dismissedBanners: BannerId[] = ["translation-ru", "translation-ar"]
      uiStore.initFromCookies({
        dismissedBanners: dismissedBanners,
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
    initialState | breakpoint | expected
    ${true}      | ${"xs"}    | ${{ isDesktopLayout: false }}
    ${false}     | ${"lg"}    | ${{ isDesktopLayout: true }}
  `(
    "updateBreakpoint gets breakpoint $breakpoint and returns $expected",
    ({ initialState, breakpoint, expected }) => {
      const uiStore = useUiStore()
      uiStore.$patch({
        isDesktopLayout: initialState,
      })
      uiStore.updateBreakpoint(breakpoint)
      const actualOutput = {
        isDesktopLayout: uiStore.isDesktopLayout,
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
    "setFiltersState updates state %o",
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
    "toggleFilters updates state %o",
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
    originalState         | bannerId            | expectedState                           | areCookiesSet
    ${[]}                 | ${"translation-es"} | ${["translation-es"]}                   | ${true}
    ${["translation-es"]} | ${"translation-es"} | ${["translation-es"]}                   | ${false}
    ${["translation-es"]} | ${"translation-de"} | ${["translation-es", "translation-de"]} | ${true}
  `(
    "dismissBanner($bannerId): $originalState -> $expectedState",
    async ({ originalState, bannerId, expectedState, areCookiesSet }) => {
      const uiStore = useUiStore()
      uiStore.initFromCookies({})
      uiStore.$patch({ dismissedBanners: originalState })
      uiStore.dismissBanner(bannerId)

      await nextTick()

      const dismissedBannersCookie = document.cookie
        ? JSON.parse(decodeURIComponent(document.cookie.split("=")[1]))[
            "dismissedBanners"
          ]
        : []

      expect(uiStore.dismissedBanners).toEqual(expectedState)
      if (areCookiesSet) {
        // eslint-disable-next-line vitest/no-conditional-expect
        expect(dismissedBannersCookie).toEqual(expectedState)
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
