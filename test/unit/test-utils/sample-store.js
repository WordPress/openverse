import SearchStore from '~/store/search'
import MediaProviderStore from '~/store/provider'

const store = {
  state: Object.assign(SearchStore.state, MediaProviderStore.state),
  dispatch: jest.fn(),
  commit: jest.fn(),
}

export default store
