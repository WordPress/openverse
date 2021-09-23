import { SET_REFERRED } from '~/constants/mutation-types.js'
import { NAV } from '~/constants/store-modules'

/**
 * If the URL contains a referral parameter pointing containing
 * 'creativecommons.org' the migration notice needs to be displayed. This
 * plugin checks the presence of the param and updates the store.
 */
export default function ({ query, store }) {
  if (query.referrer) {
    const isReferredFromCc = query.referrer.includes('creativecommons.org')
    store.commit(`${NAV}/${SET_REFERRED}`, { isReferredFromCc })
  }
}
