import { createLogger } from 'vuex'
import { FETCH_MEDIA_PROVIDERS } from '~/constants/action-types'
import { PROVIDER } from '~/constants/store-modules'

export const plugins = [createLogger()]

export const actions = {
  async nuxtServerInit({ dispatch }) {
    try {
      await dispatch(`${PROVIDER}/${FETCH_MEDIA_PROVIDERS}`)
    } catch (error) {
      console.warn("Couldn't fetch media providers")
    }
  },
}
