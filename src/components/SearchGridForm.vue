<template>
  <form role="search"
        method="post"
        @submit.prevent="onSubmit"
        class="search-form">
    <div class="search-form_ctr grid-x global-nav show-for-smedium">
        <div class="search-form_inner-ctr cell medium-12 large-10">
          <input :placeholder="searchBoxPlaceholder"
                 required="required"
                 autofocus="true"
                 class="search-form_input"
                 type="search"
                 autocapitalize="none"
                 id="searchInput"
                 v-model="searchTermsModel"
                 ref="search"
                 @keyup.enter="onSubmit">
          <ul class="search-form_toolbar menu icons icon-top" role="menubar">
            <li class="menu-button search-form_search-button" role="menuitem">
              <a href="#" @click.prevent="onSubmit">
                <i class="fi-list">
                    <svg width="24" height="24" version="1.1"
                         viewBox="0 0 50.000001 50.000001" xmlns="http://www.w3.org/2000/svg">
                     <rect width="24" height="24" fill-opacity="0"/>
                     <path d="m18.623 4.2559c-7.9132 0-14.367 6.454-14.367 14.367 0
                     7.9132 6.454 14.367 14.367 14.367 3.2414 0 6.2283-1.0954
                     8.6367-2.918a2.0002 2.0002 0 0 0 0.15039 0.16602l14.898
                     14.898a2.0002 2.0002 0 1 0 2.8281 -2.8281l-14.898-14.898a2.0002
                     2.0002 0 0 0 -0.16602 -0.15039c1.8225-2.4084 2.918-5.3953
                     2.918-8.6367 0-7.9132-6.454-14.367-14.367-14.367zm0 3.5898c5.9732
                     0 10.777 4.8042 10.777 10.777 0 5.9732-4.8042 10.777-10.777
                     10.777s-10.777-4.8042-10.777-10.777c2e-7 -5.9732 4.8042-10.777
                     10.777-10.777z" color="#35495e" color-rendering="auto" fill=" #35495e" />
                    </svg>
                </i>
                <span class="menu-button_text">Search</span>
              </a>
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
    background: #fff;
    border-bottom: 1px solid #E6EAEA;
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

  .search-form_ctr {
    position: relative;
  }

  .search-form_inner-ctr {
    height: inherit;
    display: flex;
  }

  .search-form_input {
    font-size: 24px;
    padding-left: 30px;
    margin-bottom: 0;
    width: 45%;
    height: 100%;
    outline: 0;
    border: none;
    box-shadow: none;
    min-width: 0;

    &:focus {
      border: none;
    }

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
