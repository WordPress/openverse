import { CopyAttribution, EmbedAttribution } from '../analytics/events'
import { COPY_ATTRIBUTION, EMBED_ATTRIBUTION } from './action-types'

const actions = (GoogleAnalytics) => ({
  // eslint-disable-next-line no-unused-vars
  [COPY_ATTRIBUTION]({ commit }, params) {
    const event = CopyAttribution(params.content)
    GoogleAnalytics().sendEvent(event)
  },
  [EMBED_ATTRIBUTION]() {
    const event = EmbedAttribution()
    GoogleAnalytics().sendEvent(event)
  },
})

export default {
  actions,
}
