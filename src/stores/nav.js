import { defineStore } from 'pinia'
import { reactive, readonly, toRefs } from '@nuxtjs/composition-api'

const NAV = 'nav'

/**
 * Store information about navigation.
 */
export const useNavStore = defineStore(NAV, () => {
  const state = reactive({
    isEmbedded: true,
    isReferredFromCc: false,
  })
  const { isEmbedded, isReferredFromCc } = toRefs(state)

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
