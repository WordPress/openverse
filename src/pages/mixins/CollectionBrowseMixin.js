import { FETCH_COLLECTION_IMAGES } from '@/store/action-types';
import { SET_COLLECTION_QUERY } from '@/store/mutation-types';
import getProviderName from '@/utils/getProviderName';

const CollectionBrowsePage = {
  name: 'collection-browse-page',
  props: ['provider'],
  computed: {
    query() {
      return {
        ...this.$store.state.query,
        provider: this.$props.provider,
      };
    },
    providerName() {
      return getProviderName(this.$store.state.imageProviders, this.$props.provider);
    },
  },
  methods: {
    getImages(params) {
      this.$store.dispatch(FETCH_COLLECTION_IMAGES, params);
    },
    onLoadMoreImages(searchParams) {
      this.getImages(searchParams);
    },
    onSearchFormSubmit(searchParams) {
      this.$store.commit(SET_COLLECTION_QUERY, {
        ...searchParams,
        provider: this.$props.provider,
      });
    },
  },
  created() {
    this.ticking = false;
    if (this.query.provider) {
      this.getImages(this.query);
    }
  },
};

export default CollectionBrowsePage;
