import { FETCH_IMAGES } from '@/store/action-types';
import { SET_QUERY, CLEAR_FILTERS } from '@/store/mutation-types';

const HOME_PAGE_ROUTE = 'home-page';

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
  beforeRouteLeave(to, from, next) {
    const isLeavingToHomePage = to.name === HOME_PAGE_ROUTE;

    // We need to check whenever the user is leaving form the browse page
    // into home page in order to reset and clean previously applied filters
    // Fixes #896.
    if (isLeavingToHomePage) {
      this.$store.commit(CLEAR_FILTERS, {
        isCollectionsPage: false,
        provider: null,
        shouldNavigate: false,
      });
    }

    next();
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
