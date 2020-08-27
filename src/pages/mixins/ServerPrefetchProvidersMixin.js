import { FETCH_IMAGE_PROVIDERS } from '../store/action-types'

export default {
  serverPrefetch() {
    return this.$store.dispatch(FETCH_IMAGE_PROVIDERS)
  },
}
