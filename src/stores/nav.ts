import { defineStore } from 'pinia'
import { reactive, readonly, toRefs } from '@nuxtjs/composition-api'

export interface NavState {
  isEmbedded: boolean
  isReferredFromCc: boolean
}

const NAV = 'nav'

/**
 * Store information about navigation.
 */
export const useNavStore = defineStore(NAV, () => {
  /* State */

  const state: NavState = reactive({
    isEmbedded: true,
    isReferredFromCc: false,
  })
  const { isEmbedded, isReferredFromCc } = toRefs(state)

  /* Actions */

  function setIsEmbedded(isEmbedded = true) {
    state.isEmbedded = isEmbedded
  }
  function setIsReferredFromCc(isReferredFromCc = true) {
    state.isReferredFromCc = isReferredFromCc
  }

  return {
    isEmbedded: readonly(isEmbedded),
    isReferredFromCc: readonly(isReferredFromCc),

    setIsEmbedded,
    setIsReferredFromCc,
  }
})
