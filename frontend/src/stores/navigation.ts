import { defineStore } from "pinia"

export interface NavigationState {
  isReferredFromCc: boolean
}

/**
 * Store information about navigation.
 */
export const useNavigationStore = defineStore("navigation", {
  state: (): NavigationState => ({
    isReferredFromCc: false,
  }),

  /* Actions */
  actions: {
    setIsReferredFromCc(isReferredFromCc = true) {
      this.isReferredFromCc = isReferredFromCc
    },
  },
})
