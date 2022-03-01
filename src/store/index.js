import { FETCH_MEDIA_PROVIDERS } from '~/constants/action-types'
import { PROVIDER } from '~/constants/store-modules'

import { warn } from '~/utils/console'

export const actions = {
  async nuxtServerInit({ dispatch }) {
    try {
      await dispatch(`${PROVIDER}/${FETCH_MEDIA_PROVIDERS}`)
    } catch (error) {
      warn("Couldn't fetch media providers")
    }
  },
}
