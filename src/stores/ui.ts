import { defineStore } from 'pinia'

import { computed } from '@nuxtjs/composition-api'

import type { OpenverseCookieState, SnackbarState } from '~/types/cookies'
import type { Breakpoint } from '~/constants/screens'
import { ALL_SCREEN_SIZES } from '~/constants/screens'
import { useFeatureFlagStore } from '~/stores/feature-flag'
import { cookieOptions } from '~/utils/cookies'

const desktopBreakpoints: Breakpoint[] = ['2xl', 'xl', 'lg']

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
   * the screen's max-width breakpoint.
   */
  breakpoint: Breakpoint
  /**
   * whether the request user agent is mobile or not.
   */
  isMobileUa: boolean
}

export const breakpoints = Object.keys(ALL_SCREEN_SIZES)

export const useUiStore = defineStore('ui', {
  state: (): UiState => ({
    instructionsSnackbarState: 'not_shown',
    innerFilterVisible: false,
    isFilterDismissed: false,
    isDesktopLayout: false,
    breakpoint: 'sm',
    isMobileUa: true,
  }),

  getters: {
    areInstructionsVisible(state): boolean {
      return state.instructionsSnackbarState === 'visible'
    },
    desktopBreakpoints(): Breakpoint[] {
      const featureFlagStore = useFeatureFlagStore()
      const isNewHeaderEnabled = computed(() =>
        featureFlagStore.isOn('new_header')
      )
      return isNewHeaderEnabled.value
        ? desktopBreakpoints
        : [...desktopBreakpoints, 'md']
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
  },

  actions: {
    showInstructionsSnackbar() {
      if (this.instructionsSnackbarState === 'not_shown') {
        this.instructionsSnackbarState = 'visible'
      }
    },

    hideInstructionsSnackbar() {
      this.instructionsSnackbarState = 'dismissed'
    },

    /**
     * Given a list of key value pairs of UI state parameters and their states,
     * populate the store state to match the cookie.
     *
     * @param cookies - mapping of UI state parameters and their states.
     */
    initFromCookies(cookies: OpenverseCookieState) {
      this.updateBreakpoint(cookies.uiBreakpoint ?? this.breakpoint)
      this.isFilterDismissed = cookies.uiIsFilterDismissed ?? false
      this.isMobileUa = cookies.uiIsMobileUa ?? false
      this.innerFilterVisible = this.isDesktopLayout
        ? !this.isFilterDismissed
        : false
      this.updateCookies()
    },

    updateCookies() {
      const opts = cookieOptions
      this.$nuxt.$cookies.setAll([
        {
          name: 'uiInstructionsSnackbarState',
          value: this.instructionsSnackbarState,
          opts,
        },
        { name: 'uiIsFilterDismissed', value: this.isFilterDismissed, opts },
        { name: 'uiBreakpoint', value: this.breakpoint, opts },
        { name: 'uiIsMobileUa', value: this.isMobileUa, opts },
      ])
    },

    /**
     * If the breakpoint is different from the state, updates the state, and saves it into app cookies.
     *
     * @param breakpoint - the `min-width` tailwind breakpoint for the screen width.
     */
    updateBreakpoint(breakpoint: Breakpoint) {
      if (this.breakpoint === breakpoint) {
        return
      }

      this.breakpoint = breakpoint
      this.$nuxt.$cookies.set('uiBreakpoint', this.breakpoint, cookieOptions)
      this.isDesktopLayout = this.desktopBreakpoints.includes(breakpoint)
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
        this.$nuxt.$cookies.set(
          'uiIsFilterDismissed',
          this.isFilterDismissed,
          cookieOptions
        )
      }
    },

    /**
     * Toggles filter state and saves the new state in a cookie.
     */
    toggleFilters() {
      this.setFiltersState(!this.isFilterVisible)
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
