<template>
  <!-- eslint-disable vuejs-accessibility/no-autofocus -->
  <form
    role="search"
    method="post"
    class="search-form p-4 z-30"
    @submit.prevent="onSubmit"
  >
    <button
      v-if="!isFilterVisible"
      class="button filter-toggle"
      type="button"
      @click.prevent="onToggleSearchGridFilter()"
      @keyup.enter.prevent="onToggleSearchGridFilter()"
    >
      {{ $t('filters.title') }}
    </button>
    <div
      class="search-field field has-addons control search-control has-icons-left ml-2"
    >
      <label for="searchInput" class="search-field__label control label">
        <input
          id="searchInput"
          ref="search"
          :aria-label="$t('browse-page.aria.search')"
          required="required"
          autofocus="true"
          class="search-field__input input"
          type="search"
          :placeholder="searchBoxPlaceholder"
          :value="searchTermsModel"
          @input="onInput"
          @keyup.enter="onSubmit"
        />
      </label>
      <span class="icon is-left">
        <svg
          viewBox="0 0 30 30"
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          class="icon__svg"
        >
          <path
            d="M29.59 25.94l-5.842-5.842a1.405 1.405 0 00-.996-.41h-.955a12.128 12.128 0 002.578-7.5C24.375 5.455 18.92 0 12.187 0 5.455 0 0 5.455 0 12.188c0 6.732 5.455 12.187 12.188 12.187 2.83 0 5.431-.96 7.5-2.578v.955c0 .375.146.732.41.996l5.841 5.842a1.4 1.4 0 001.987 0l1.658-1.658c.55-.551.55-1.442.006-1.992zm-17.402-6.253a7.496 7.496 0 01-7.5-7.5c0-4.142 3.351-7.5 7.5-7.5 4.142 0 7.5 3.352 7.5 7.5 0 4.143-3.352 7.5-7.5 7.5z"
            fill="currentColor"
          />
        </svg>
      </span>
      <input
        type="submit"
        class="control button is-primary"
        :value="$t('browse-page.search-form.button')"
        @click.prevent="onSubmit"
        @keyup.enter.prevent="onSubmit"
      />
    </div>
  </form>
  <!-- eslint-enable -->
</template>

<script>
import { SET_FILTER_IS_VISIBLE } from '~/constants/mutation-types'
import { queryStringToSearchType } from '~/utils/search-query-transform'
import { VIDEO } from '~/constants/media'

export default {
  name: 'SearchGridForm',
  data: () => ({ searchTermsModel: null }),
  computed: {
    activeTab() {
      return queryStringToSearchType(this.$route.path)
    },
    searchTerms() {
      return this.$store.state.query.q
    },
    isFilterVisible() {
      return this.$store.state.isFilterVisible
    },
    searchBoxPlaceholder() {
      return this.$t('browse-page.search-form.placeholder', {
        type: this.$t(`browse-page.search-form.${this.activeTab}`),
      })
    },
  },
  watch: {
    searchTerms: function handler() {
      this.setFormInput()
    },
  },
  mounted: function handler() {
    this.setFormInput()
  },
  methods: {
    onSubmit(e) {
      e.preventDefault()
      if (this.searchTermsModel) {
        this.$emit('onSearchFormSubmit', {
          query: { q: this.searchTermsModel },
        })
        this.$refs.search.blur()
      }
    },
    onInput(e) {
      this.searchTermsModel = e.target.value
      if (this.activeTab === VIDEO) {
        this.$emit('onSearchFormSubmit', {
          query: { q: this.searchTermsModel },
        })
      }
    },
    onToggleSearchGridFilter() {
      this.$store.commit(SET_FILTER_IS_VISIBLE, {
        isFilterVisible: !this.isFilterVisible,
      })
    },
    setFormInput() {
      this.searchTermsModel = this.searchTerms
    },
  },
}
</script>

<style lang="scss" scoped>
.filter-toggle {
  text-transform: none;
  font-size: 1rem;
  border-color: $color-light-gray;
  padding: 0.5rem;
  height: 2.5rem;
  &:hover {
    border-color: transparent;
  }
  @include desktop {
    height: 3.875rem;
  }
}

.search-form {
  width: 100%;
  top: 0;
  position: sticky;
  background-color: white;
  display: flex;
}

.has-addons {
  .control:first-child:not(:only-child),
  .control:first-child:not(:only-child) .input {
    border-bottom-right-radius: 0;
    border-top-right-radius: 0;
    margin-right: -1px;
  }
  .button {
    border-bottom-left-radius: 0;
    border-top-left-radius: 0;
  }
}
.search-field {
  display: flex;
  width: 100%;
  clear: both;
  position: relative;
  text-align: left;
  @include desktop {
    width: 100%;
  }
  .label {
    flex: 1;
    margin-bottom: 0;
  }
  .input {
    font-size: 1rem;
    height: 2.5rem;
    @include desktop {
      font-size: 1.43rem;
      height: 3.875rem;
    }
  }
  .icon {
    top: calc(50% - 1.25em);
  }
  .button {
    font-size: 1rem;
    padding: 0.5rem calc(1rem + 0.2rem);
    @include desktop {
      font-size: 1.43rem;
      padding-left: var(--button-padding-horizontal);
      padding-right: var(--button-padding-horizontal);
      height: 3.875rem;
    }
  }
}
</style>
