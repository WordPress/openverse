import { CopyAttribution } from '~/analytics/events'
import { COPY_ATTRIBUTION } from './action-types'

const actions = (GoogleAnalytics) => ({
  [COPY_ATTRIBUTION](_, params) {
    const event = CopyAttribution(params.type, params.content)
    GoogleAnalytics.sendEvent(event)
  },
})

export default { actions }
