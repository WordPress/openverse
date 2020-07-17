import SearchStore from '@/store/search-store'
import ImageProviderStore from '@/store/image-provider-store'

const store = {
  state: Object.assign(
    SearchStore.state('?q=nature'),
    ImageProviderStore.state
  ),
}

export default store
