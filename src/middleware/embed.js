import { SET_EMBEDDED } from '~/store-modules/mutation-types'

export default function ({ store, query }) {
  if ('embedded' in query) {
    const isEmbedded = query.embedded === 'true'
    store.commit(SET_EMBEDDED, { isEmbedded })
  }
}
