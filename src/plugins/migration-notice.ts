import { useNavStore } from '~/stores/nav'

import type { Plugin } from '@nuxt/types'

/**
 * If the URL contains a referral parameter pointing containing
 * 'creativecommons.org' the migration notice needs to be displayed. This
 * plugin checks the presence of the param and updates the store.
 */
const migrationNoticePlugin: Plugin = ({ query }) => {
  if (query.referrer) {
    useNavStore().setIsReferredFromCc(
      query.referrer.includes('creativecommons.org')
    )
  }
}

export default migrationNoticePlugin
