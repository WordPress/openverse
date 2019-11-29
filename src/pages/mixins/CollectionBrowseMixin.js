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
    isFilterVisible() {
      return this.$store.state.isFilterVisible;
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
    if (this.query.provider) {
      this.getImages(this.query);
    }
  },
  watch: {
    query(newQuery) {
      if (newQuery) {
        this.getImages(newQuery);
      }
    },
  },
};

export default CollectionBrowsePage;
