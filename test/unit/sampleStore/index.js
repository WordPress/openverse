import SearchStore from '@/store/search-store';
import ListStore from '@/store/share-list-store';
import ImageProviderStore from '@/store/image-provider-store';

const store = {
  state: Object.assign(
    SearchStore.state('?q=nature'),
    ListStore.state,
    ImageProviderStore.state,
  ),
};

export default store;
