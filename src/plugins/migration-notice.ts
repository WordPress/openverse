import { useNavigationStore } from '~/stores/navigation'

import type { Plugin } from '@nuxt/types'

/**
 * If the URL contains a referral parameter pointing containing
 * 'creativecommons.org' the migration notice needs to be displayed. This
 * plugin checks the presence of the param and updates the store.
 */
const migrationNoticePlugin: Plugin = ({ query }) => {
  if (query.referrer) {
    useNavigationStore().setIsReferredFromCc(
      query.referrer.includes('creativecommons.org')
    )
  }
}

export default migrationNoticePlugin
