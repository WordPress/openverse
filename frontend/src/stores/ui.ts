import { defineStore } from "pinia"

import { useNavigationStore } from "~/stores/navigation"

import type { OpenverseCookieState, SnackbarState } from "~/types/cookies"
import type { BannerId, TranslationBannerId } from "~/types/banners"

import type { Breakpoint } from "~/constants/screens"
import { ALL_SCREEN_SIZES } from "~/constants/screens"
import { cookieOptions } from "~/utils/cookies"
import { needsTranslationBanner } from "~/utils/translation-banner"

import type { LocaleObject } from "@nuxtjs/i18n"

const desktopBreakpoints: Breakpoint[] = ["2xl", "xl", "lg"]

export interface UiState {
  /**
   * whether to show the instructions snackbar.
   */
  instructionsSnackbarState: SnackbarState
  /**
   * whether the filters are shown (sidebar on desktop or modal on mobile).
   * This is the inner value, components should use the un-prefixed getter.
   */
  innerFilterVisible: boolean
  /**
   * (only for desktop layout) whether the filters were dismissed. If true,
   * the filters should be closed on SSR for the first load on desktop layout.
   */
  isFilterDismissed: boolean
  /**
   * whether the site layout is desktop (or mobile).
   */
  isDesktopLayout: boolean
  /**
   * the width of the browser viewport
   */
  deviceWidth: number
  /**
   * the height of the browser viewport
   */
  deviceHeight: number
  /**
   * the screen's max-width breakpoint.
   */
  breakpoint: Breakpoint
  /**
   * whether the request user agent is mobile or not.
   */
  isMobileUa: boolean
  dismissedBanners: BannerId[]
}

export const breakpoints = Object.keys(ALL_SCREEN_SIZES)

export const useUiStore = defineStore("ui", {
  state: (): UiState => ({
    instructionsSnackbarState: "not_shown",
    innerFilterVisible: false,
    isFilterDismissed: false,
    isDesktopLayout: false,
    deviceWidth: -1,
    deviceHeight: -1,
    breakpoint: "sm",
    isMobileUa: true,
    dismissedBanners: [],
  }),

  getters: {
    areInstructionsVisible(state): boolean {
      return state.instructionsSnackbarState === "visible"
    },

    /**
     * On desktop, we only hide the filters sidebar if it was
     * specifically dismissed on the desktop layout.
     *
     * The filters state could diverge if the layout changed from desktop to mobile:
     * closing the filters on mobile sets `isFilterVisible` to false, but does not
     * save the `isFilterDismissed` because it only applies on the desktop layout.
     *
     * This getter correct the state if it diverged, and then returns the visibility state.
     */
    isFilterVisible(state: UiState): boolean {
      if (
        state.isDesktopLayout &&
        !state.isFilterDismissed &&
        !state.innerFilterVisible
      ) {
        state.innerFilterVisible = true
      }
      return state.innerFilterVisible
    },
    /**
     * The locale object of the current locale.
     */
    currentLocale(): LocaleObject {
      return this.$nuxt.i18n.localeProperties
    },
    /**
     * The id used in the translation banner and the cookies for dismissed banners.
     * @example 'translation-ru'
     */
    translationBannerId(): TranslationBannerId {
      return `translation-${this.currentLocale.code as LocaleObject["code"]}`
    },
    /**
     * The translation banner is shown if the translated percentage is below 90%,
     * and the banner for the current locale was not dismissed (status from cookies).
     */
    shouldShowTranslationBanner(): boolean {
      return (
        !this.dismissedBanners.includes(this.translationBannerId) &&
        needsTranslationBanner(this.currentLocale)
      )
    },
    /**
     * The migration banner is shown if the user is referred from CC Search,
     * and hasn't dismissed it yet.
     */
    shouldShowMigrationBanner(): boolean {
      const navigationStore = useNavigationStore()
      return (
        !this.dismissedBanners.includes("cc-referral") &&
        navigationStore.isReferredFromCc
      )
    },
  },

  actions: {
    showInstructionsSnackbar() {
      if (this.instructionsSnackbarState === "not_shown") {
        this.instructionsSnackbarState = "visible"
      }
    },

    hideInstructionsSnackbar() {
      this.instructionsSnackbarState = "dismissed"
    },

    /**
     * Given a list of key value pairs of UI state parameters and their states,
     * populate the store state to match the cookie.
     *
     * @param cookies - mapping of UI state parameters and their states.
     */
    initFromCookies(cookies: OpenverseCookieState) {
      this.updateBreakpoint(
        cookies.uiDeviceWidth ?? this.deviceWidth,
        cookies.uiDeviceHeight ?? this.deviceHeight,
        cookies.uiBreakpoint ?? this.breakpoint
      )
      this.isFilterDismissed = cookies.uiIsFilterDismissed ?? false
      this.isMobileUa = cookies.uiIsMobileUa ?? false
      this.innerFilterVisible = this.isDesktopLayout
        ? !this.isFilterDismissed
        : false
      this.dismissedBanners = cookies.uiDismissedBanners ?? []
      this.updateCookies()
    },

    updateCookies() {
      const opts = { ...cookieOptions }

      this.$nuxt.$cookies.setAll([
        {
          name: "uiInstructionsSnackbarState",
          value: this.instructionsSnackbarState,
          opts,
        },
        { name: "uiIsFilterDismissed", value: this.isFilterDismissed, opts },
        { name: "uiDeviceWidth", value: this.deviceWidth, opts },
        { name: "uiDeviceHeight", value: this.deviceHeight, opts },
        { name: "uiBreakpoint", value: this.breakpoint, opts },
        { name: "uiIsMobileUa", value: this.isMobileUa, opts },
        { name: "uiDismissedBanners", value: this.dismissedBanners, opts },
      ])
    },

    /**
     * If the width, height or breakpoint is different from the state, updates the state, and saves it into app cookies.
     *
     * @param deviceWidth - the updated device width
     * @param deviceHeight - the updated device height
     * @param breakpoint - the `min-width` tailwind breakpoint for the screen width.
     */
    updateBreakpoint(
      deviceWidth: number,
      deviceHeight: number,
      breakpoint: Breakpoint
    ) {
      if (
        this.deviceWidth === deviceWidth &&
        this.deviceHeight === deviceHeight &&
        this.breakpoint === breakpoint
      ) {
        return
      }

      this.deviceWidth = deviceWidth
      this.deviceHeight = deviceHeight
      this.breakpoint = breakpoint

      this.$nuxt.$cookies.set("uiDeviceWidth", this.deviceWidth, {
        ...cookieOptions,
      })
      this.$nuxt.$cookies.set("uiDeviceHeight", this.deviceHeight, {
        ...cookieOptions,
      })
      this.$nuxt.$cookies.set("uiBreakpoint", this.breakpoint, {
        ...cookieOptions,
      })
      this.isDesktopLayout = desktopBreakpoints.includes(breakpoint)
    },

    /**
     * Sets the filter state based on the `visible` parameter.
     * If the filter state is changed on desktop, updates the `isFilterDismissed`
     * 'ui' cookie value.
     *
     * @param visible - whether the filters should be visible.
     */
    setFiltersState(visible: boolean) {
      this.innerFilterVisible = visible
      if (this.isDesktopLayout) {
        this.isFilterDismissed = !visible

        this.$nuxt.$cookies.set("uiIsFilterDismissed", this.isFilterDismissed, {
          ...cookieOptions,
        })
      }
    },

    /**
     * Toggles filter state and saves the new state in a cookie.
     */
    toggleFilters() {
      this.setFiltersState(!this.isFilterVisible)
    },
    /**
     * If the banner wasn't dismissed before, dismisses it and saves the new state in a cookie.
     * @param bannerId - the id of the banner to dismiss.
     */
    dismissBanner(bannerId: BannerId) {
      if (this.dismissedBanners.includes(bannerId)) {
        return
      }

      this.dismissedBanners.push(bannerId)

      this.$nuxt.$cookies.set("uiDismissedBanners", this.dismissedBanners, {
        ...cookieOptions,
      })
    },
    isBannerDismissed(bannerId: BannerId) {
      return this.dismissedBanners.includes(bannerId)
    },
    /**
     * Similar to CSS `@media` queries, this function returns a boolean
     * indicating whether the current breakpoint is greater than or equal to
     * the breakpoint passed as a parameter.
     */
    isBreakpoint(breakpoint: Breakpoint): boolean {
      return (
        breakpoints.indexOf(breakpoint) >= breakpoints.indexOf(this.breakpoint)
      )
    },
  },
})
