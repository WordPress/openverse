<template>
  <form role="search"
        method="post"
        @submit.prevent="onSubmit"
        class="search-form padding-normal">
    <div class="is-flex is-hidden-touch">
      <button v-if="!isFilterVisible"
              class="button toggle-filter padding-vertical-normal padding-horizontal-big"
              type="button"
              @click.prevent="onToggleSearchGridFilter()">
        <i v-if="!isFilterApplied" class="icon sliders" />
        <i v-else class="icon sliders has-color-dark-slate-blue has-text-weight-semibold" />
      </button>
      <div class="control has-icons-left search-form_input margin-left-small">
        <input id="searchInput"
                required="required"
                class="input is-medium"
                type="search"
                ref="search"
                :placeholder="searchBoxPlaceholder"
                v-model="searchTermsModel"
                @keyup.enter="onSubmit" />
        <span class="icon is-medium is-left">
          <i class="icon search is-size-5"></i>
        </span>
      </div>
      <input type="submit" class="button is-primary" @click.prevent="onSubmit" value="Search" />
    </div>
    <div class="is-flex is-hidden-desktop">
      <button class="button small toggle-filter-small padding-small"
              type="button"
              @click.prevent="onToggleSearchGridFilter()">
        <i v-if="!isFilterApplied" class="icon sliders" />
        <i v-else class="icon sliders has-color-dark-slate-blue has-text-weight-semibold" />
      </button>
      <div class="control has-icons-left search-form_input margin-left-small">
        <input id="searchInput"
                required="required"
                class="input search-form_input"
                type="search"
                ref="search"
                :placeholder="searchBoxPlaceholder"
                v-model="searchTermsModel"
                @keyup.enter="onSubmit">
        <span class="icon is-left">
          <i class="icon search is-size-6"></i>
        </span>
      </div>
      <input type="submit" class="button is-primary small" value="Search" />
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
    height: 3.875rem;
  }

  .toggle-filter-small {
    width: 4rem;
    padding-top: 0.35rem !important;

    img {
      max-width: 1.5rem;
    }
  }

  .search-form {
    width: 100%;
    top: 0;
    position: sticky;
    background-color: #f5f5f5;
    z-index: 10;
  }

  .search-form_input {
    width: 45%;

    @media (max-width: 64em) {
      width: 100%;
    }
  }
  .button .icon {
    height: auto;
  }

  .icon .search {
    padding: 1.3rem;

    @media (max-width: 64em) {
      padding: .8rem;
    }
  }
</style>
