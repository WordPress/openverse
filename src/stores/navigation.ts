import { defineStore } from 'pinia'

export interface NavigationState {
  isEmbedded: boolean
  isReferredFromCc: boolean
}

/**
 * Store information about navigation.
 */
export const useNavigationStore = defineStore('navigation', {
  state: (): NavigationState => ({
    isEmbedded: true,
    isReferredFromCc: false,
  }),

  /* Actions */
  actions: {
    setIsEmbedded(isEmbedded = true) {
      this.isEmbedded = isEmbedded
    },
    setIsReferredFromCc(isReferredFromCc = true) {
      this.isReferredFromCc = isReferredFromCc
    },
  },
})
