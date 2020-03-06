<template>
  <form role="search"
        method="post"
        @submit.prevent="onSubmit"
        class="search-form margin-vertical-normal margin-horizontal-normal">
    <div class="is-flex">
      <input :placeholder="searchBoxPlaceholder"
              required="required"
              autofocus="true"
              class="input is-large search-form_input"
              type="search"
              autocapitalize="none"
              id="searchInput"
              v-model="searchTermsModel"
              ref="search"
              @keyup.enter="onSubmit">
      <ul class="search-form_toolbar menu icons icon-top" role="menubar">
        <li class="menu-button search-form_search-button" role="menuitem">
          <button class="button is-primary medium" @click.prevent="onSubmit">
            Search
          </button>
        </li>
        <li :class="{'menu-button': true,
                      'search-form_filter-button': true,
                      isActive: isFilterVisible }"
            role="menuitem">
          <a href="#" @click.prevent="onToggleSearchGridFilter()">
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
            <span class="menu-button_text">Filter</span>
          </a>
        </li>
      </ul>
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
  .search-filter {
    position: absolute;
    top: 82px !important;
    left: auto !important;
    right: 0 !important;
    border: 1px solid #e8e8e8;
  }

  .search-form {
    width: 100%;
    top: 0;
    position: sticky;
  }

  .search-filter:after,
  .search-filter:before {
    bottom: 100%;
    right: 30px;
    border: solid transparent;
    content: " ";
    height: 0;
    width: 0;
    position: absolute;
    pointer-events: none;
  }

  .search-filter:after {
    border-color: rgba(255, 255, 255, 0);
    border-bottom-color: #fff;
    border-width: 8px;
    margin-left: -8px;
    z-index: 100;
  }

  .search-filter:before {
    border-color: rgba(232, 232, 232, 0);
    border-bottom-color: #e8e8e8;
    border-width: 10px;
    margin-left: 0px;
    right: 28px;
  }

  .search-form_search-button {

    .menu-button_text {
      color: #35495e;
    }
  }

  .search-form_filter-button {
    position: relative;

    .menu-button_text {
      color: #35495e;
    }
  }

  .isActive {
    background-color: #fafafa;
  }

  .search-form_input {
    width: 45%;

    @media (max-width: 49em) {
      width: 100%;
    }
  }

  .search-form_toolbar {
    flex-wrap: nowrap;

    li {
      border-left: 1px solid #E6EAEA;
      border-right: 1px solid #E6EAEA;

      &:last-of-type {
        border-left: none;
      }
    }
  }

  @media screen and (max-width: 600px) {
    .search-form_input {
      font-size: 18px;
    }
  }
</style>
