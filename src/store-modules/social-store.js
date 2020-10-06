import { SocialMediaShare } from '~/analytics/events'
import { SOCIAL_MEDIA_SHARE } from './action-types'

const actions = (GoogleAnalytics) => ({
  // eslint-disable-next-line no-unused-vars
  [SOCIAL_MEDIA_SHARE]({ commit }, params) {
    const event = SocialMediaShare(params.site)
    GoogleAnalytics().sendEvent(event)
  },
})

export default {
  actions,
}
