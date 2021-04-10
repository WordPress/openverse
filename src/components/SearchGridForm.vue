<template>
  <!-- eslint-disable vuejs-accessibility/no-autofocus -->
  <form
    role="search"
    method="post"
    class="search-form padding-normal"
    @submit.prevent="onSubmit"
  >
    <div class="is-flex">
      <button
        v-if="!isFilterVisible"
        class="button filter-toggle"
        type="button"
        @click.prevent="onToggleSearchGridFilter()"
        @keyup.enter.prevent="onToggleSearchGridFilter()"
      >
        {{ $t('filters.title') }}
      </button>
      <div class="field has-addons search-input">
        <div class="control search-control has-icons-left margin-left-small">
          <label for="searchInput">
            <input
              id="searchInput"
              ref="search"
              :aria-label="$t('browse-page.aria.search')"
              required="required"
              autofocus="true"
              class="search-input__input input"
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
        </div>
        <div class="control">
          <input
            type="submit"
            class="button is-primary"
            :value="$t('browse-page.search-form.button')"
            @click.prevent="onSubmit"
            @keyup.enter.prevent="onSubmit"
          />
        </div>
      </div>
    </div>
  </form>
  <!-- eslint-enable -->
</template>

<script>
import { SET_FILTER_IS_VISIBLE } from '~/store-modules/mutation-types'

export default {
  name: 'SearchGridForm',
  data: () => ({ searchTermsModel: null }),
  computed: {
    activeTab() {
      return this.$route.path.split('search/')[1] || 'image'
    },
    searchTerms() {
      return this.$store.state.query.q
    },
    isFilterVisible() {
      return this.$store.state.isFilterVisible
    },
    isFilterApplied() {
      return this.$store.state.isFilterApplied
    },
    searchBoxPlaceholder() {
      const type = this.$route.path.split('search/')[1] || 'image'
      return `Search all ${type}s`
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

      if (this.activeTab === 'video' || this.activeTab === 'audio') {
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
    onSearchFilterChanged(query) {
      this.$emit('onSearchFormSubmit', query)
    },
    setFormInput() {
      this.searchTermsModel = this.searchTerms
    },
  },
}
</script>

<style lang="scss" scoped>
@import 'bulma/sass/utilities/_all.sass';

.filter-toggle {
  text-transform: none;
  font-size: 1rem;
  border-color: #d8d8d8;
  padding: 0.5rem;
  height: 2.5rem;
  &:focus:not(:active) {
    box-shadow: 0 0 0 0.125em rgba(0, 0, 0, 0.25);
  }
  @include desktop {
    height: 3.875rem;
    padding: 1rem 1.5rem;
  }
}

.search-form {
  width: 100%;
  top: 0;
  position: sticky;
  background-color: #f5f5f5;
  z-index: 10;
}

.search-input__input {
  font-size: 1rem;
  height: 2.5rem;
  @include desktop {
    font-size: 1.43rem;
    height: 3.875rem;
  }
}
.search-input {
  width: 100%;
  @include desktop {
    width: 70%;
  }
}

span.icon {
  margin-top: auto;
  margin-bottom: auto;
  bottom: 0;
  @include desktop {
    margin-left: 0.5rem;
  }
}
.icon.search {
  padding: 0.8rem;
  @include desktop {
    padding: 1.2rem;
    max-height: 2.5rem;
    max-width: 2.5rem;
    font-size: 1.12rem;
  }
}

.control:first-child {
  width: 100%;
}
input.button {
  font-size: 1rem;
  padding: 0.5rem calc(1rem + 0.2rem);
  @include desktop {
    font-size: 1.43rem;
    padding: calc(2rem - 0.187rem) 2.5rem;
  }
}
</style>
