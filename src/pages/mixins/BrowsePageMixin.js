import { FETCH_IMAGES } from '@/store/action-types';
import { SET_QUERY } from '@/store/mutation-types';

const BrowsePage = {
  name: 'browse-page',
  computed: {
    query() {
      return this.$store.state.query;
    },
    isFilterVisible() {
      return this.$store.state.isFilterVisible;
    },
  },
  methods: {
    getImages(params) {
      this.$store.dispatch(FETCH_IMAGES, params);
    },
    onLoadMoreImages(searchParams) {
      this.getImages(searchParams);
    },
    onSearchFormSubmit(searchParams) {
      this.$store.commit(SET_QUERY, searchParams);
    },
  },
  mounted() {
    if (this.query.q && !this.$store.state.images.length) {
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

export default BrowsePage;
