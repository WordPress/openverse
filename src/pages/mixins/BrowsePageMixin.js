import { FETCH_IMAGES } from '@/store/action-types';
import { SET_QUERY } from '@/store/mutation-types';

const BrowsePage = {
  name: 'browse-page',
  computed: {
    query() {
      return this.$store.state.query;
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
    this.ticking = false;
    if (this.query.q) {
      this.getImages(this.query);
    }
  },
};

export default BrowsePage;
