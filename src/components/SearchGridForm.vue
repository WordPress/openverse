<template>
  <form role="search"
        method="post"
        @submit.prevent="onSubmit"
        class="search-form margin-vertical-normal margin-horizontal-normal">
    <div class="is-flex">
      <button class="button toggle-filter"  @click.prevent="onToggleSearchGridFilter()">
        <i class="fi-list">
          <img v-if="!isFilterApplied"
                width="24"
                height="24"
                src="../assets/filter_icon_new.svg" />

          <img v-else
                width="24"
                height="24"
                src="../assets/filter_icon_new_applied.svg" />
        </i>
      </button>
      <input :placeholder="searchBoxPlaceholder"
              required="required"
              autofocus="true"
              class="input is-medium search-form_input margin-left-small"
              type="search"
              autocapitalize="none"
              id="searchInput"
              v-model="searchTermsModel"
              ref="search"
              @keyup.enter="onSubmit">
      <button class="button is-primary" @click.prevent="onSubmit">
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

  .search-form {
    width: 100%;
    top: 0;
    position: sticky;
  }

  .search-form_input {
    width: 45%;

    @media (max-width: 49em) {
      width: 100%;
    }
  }

  @media screen and (max-width: 600px) {
    .search-form_input {
      font-size: 18px;
    }
  }
</style>
