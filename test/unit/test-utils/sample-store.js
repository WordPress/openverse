import SearchStore from '~/store-modules/search-store'
import MediaProviderStore from '~/store/provider'

const store = {
  state: Object.assign(SearchStore.state, MediaProviderStore.state),
  dispatch: jest.fn(),
  commit: jest.fn(),
}

export default store
