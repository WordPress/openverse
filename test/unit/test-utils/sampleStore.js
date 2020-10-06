import SearchStore from '~/store-modules/search-store'
import ImageProviderStore from '~/store-modules/image-provider-store'

const store = {
  state: Object.assign(SearchStore.state, ImageProviderStore.state),
}

export default store
