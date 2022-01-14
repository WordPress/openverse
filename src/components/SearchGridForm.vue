<template>
  <!-- eslint-disable vuejs-accessibility/no-autofocus -->
  <form
    role="search"
    method="post"
    class="search-form p-4 z-30"
    @submit.prevent="onSubmit"
  >
    <div class="search-field field has-addons control search-control">
      <label for="searchInput" class="search-field__label control label">
        <input
          id="searchInput"
          ref="search"
          :aria-label="$t('browse-page.aria.search')"
          required="required"
          autofocus="true"
          class="search-input input"
          type="search"
          :placeholder="searchBoxPlaceholder"
          :value="searchTermsModel"
          @input="onInput"
          @keyup.enter="onSubmit"
        />
      </label>
      <span class="search-icon">
        <svg
          viewBox="0 0 30 30"
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
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
      />
    </div>
  </form>
  <!-- eslint-enable -->
</template>

<script>
import { SET_FILTER_IS_VISIBLE } from '~/constants/mutation-types'
import { queryStringToSearchType } from '~/utils/search-query-transform'
import { VIDEO } from '~/constants/media'
import { SEARCH } from '~/constants/store-modules'
import { mapMutations, mapState } from 'vuex'

export default {
  name: 'SearchGridForm',
  data: () => ({ searchTermsModel: null }),
  computed: {
    ...mapState(SEARCH, ['query']),
    searchTerms() {
      return this.query.q
    },
    activeTab() {
      return queryStringToSearchType(this.$route.path)
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
    ...mapMutations(SEARCH, { setFilterIsVisible: SET_FILTER_IS_VISIBLE }),
    onSubmit(e) {
      e.preventDefault()
      if (this.searchTermsModel) {
        this.$emit('onSearchFormSubmit', {
          q: this.searchTermsModel,
        })
        this.$refs.search.blur()
      }
    },
    onInput(e) {
      this.searchTermsModel = e.target.value
      if (this.activeTab === VIDEO) {
        this.$emit('onSearchFormSubmit', {
          q: this.searchTermsModel,
        })
      }
    },
    setFormInput() {
      this.searchTermsModel = this.searchTerms
    },
  },
}
</script>

<style lang="scss" scoped>
.search-icon {
  @apply start-0 text-light-gray w-10 h-10 absolute items-center inline-flex justify-center pointer-events-none;
}
.search-input {
  @apply w-full max-w-full h-10 relative appearance-none items-center justify-start ps-10;
  @apply placeholder-dark-charcoal-50 placeholder-opacity-50;
  @apply text-2xl text-start font-semibold placeholder-dark-charcoal-50;
  @apply border border-light-gray hover:border-gray rounded rounded-e-none focus:outline-none focus:border-gray;
  @apply lg:text-lgr lg:h-14;
}
.search-form {
  @apply w-full top-0 sticky bg-white flex;
}

.search-field {
  @apply flex w-full relative text-start clear-both;
  .label {
    @apply mb-0 flex-1;
  }

  .button {
    @apply py-2 px-5 h-10 lg:h-14 lg:px-10 rounded rounded-s-none text-2xl lg:text-lgr;
  }
}
.search-icon {
  top: calc(50% - 1.25em);
  // On hover, the icon without z-index disappears
  z-index: 5;
}
</style>
