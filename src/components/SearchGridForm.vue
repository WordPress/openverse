<template>
  <form role="search"
        method="post"
        @submit.prevent="onSubmit"
        class="search-form padding-normal">
    <div class="is-flex is-hidden-touch">
      <button class="button toggle-filter"  @click.prevent="onToggleSearchGridFilter()">
        <img v-if="!isFilterApplied" width="24" src="../assets/filter_icon_new.svg" />
        <img v-else width="24" src="../assets/filter_icon_new_applied.svg" />
      </button>
      <input id="searchInput"
              required="required"
              class="input is-medium search-form_input margin-left-small"
              type="search"
              ref="search"
              :placeholder="searchBoxPlaceholder"
              v-model="searchTermsModel"
              @keyup.enter="onSubmit">
      <button class="button is-primary" @click.prevent="onSubmit">
        Search
      </button>
    </div>
    <div class="is-flex is-hidden-desktop">
      <button class="button small toggle-filter-small"  @click.prevent="onToggleSearchGridFilter()">
        <img v-if="!isFilterApplied" width="64" src="../assets/filter_icon_new.svg" />
        <img v-else width="64" src="../assets/filter_icon_new_applied.svg" />
      </button>
      <input id="searchInput"
              required="required"
              class="input search-form_input margin-left-small"
              type="search"
              ref="search"
              :placeholder="searchBoxPlaceholder"
              v-model="searchTermsModel"
              @keyup.enter="onSubmit">
      <button class="button is-primary small" @click.prevent="onSubmit">
        Search
      </button>
    </div>
  </form>
</template>

<script>
import SearchGridFilter from '@/components/SearchGridFilter';
import { SET_FILTER_IS_VISIBLE } from '@/store/mutation-types';

export default {
  name: 'search-grid-form',
  props: {
    searchBoxPlaceholder: {
      default: 'Search all images',
    },
  },
  data: () => ({ searchTermsModel: null }),
  components: {
    SearchGridFilter,
  },
  computed: {
    searchTerms() {
      return this.$store.state.query.q;
    },
    isFilterVisible() {
      return this.$store.state.isFilterVisible;
    },
    isFilterApplied() {
      return this.$store.state.isFilterApplied;
    },
  },
  methods: {
    onSubmit(e) {
      e.preventDefault();
      if (this.searchTermsModel) {
        this.$emit('onSearchFormSubmit', { query: { q: this.searchTermsModel }, shouldNavigate: true });
        this.$refs.search.blur();
      }
    },
    onToggleSearchGridFilter() {
      this.$store.commit(
        SET_FILTER_IS_VISIBLE,
        { isFilterVisible: !this.isFilterVisible },
      );
    },
    onSearchFilterChanged(query) {
      this.$emit('onSearchFormSubmit', query);
    },
    setFormInput() {
      this.searchTermsModel = this.searchTerms;
    },
  },
  watch: {
    searchTerms: function handler() {
      this.setFormInput();
    },
  },
  mounted: function handler() {
    this.setFormInput();
  },
};
</script>

<style lang="scss" scoped>
  .toggle-filter {
    padding: 1rem;
    height: 3.875rem;
  }

  .toggle-filter-small {
    width: 4rem;
    padding: 0.5rem;
    padding-top: 0.3rem;

    img {
      max-width: 1.5rem;
    }
  }

  .search-form {
    width: 100%;
    top: 0;
    position: sticky;
    background-color: #e9ebee;
    z-index: 10;
  }

  .search-form_input {
    width: 45%;

    @media (max-width: 48em) {
      width: 100%;
    }
  }
</style>
