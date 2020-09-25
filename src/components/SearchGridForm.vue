<template>
  <form
    role="search"
    method="post"
    @submit.prevent="onSubmit"
    class="search-form padding-normal"
  >
    <div class="is-flex is-hidden-touch">
      <button
        v-if="!isFilterVisible"
        class="button toggle-filter padding-vertical-normal padding-horizontal-big"
        type="button"
        @click.prevent="onToggleSearchGridFilter()"
        v-on:keyup.enter.prevent="onToggleSearchGridFilter()"
      >
        {{ $t('filters.title') }}
      </button>
      <div class="field has-addons search-input">
        <div class="control has-icons-left margin-left-small">
          <label for="searchInput">
            <input
              :aria-label="$t('browse-page.aria.search')"
              id="searchInput"
              required="required"
              autofocus="true"
              class="input is-medium"
              type="search"
              ref="search"
              :placeholder="searchBoxPlaceholder"
              :value="searchTermsModel"
              @input="onInput"
              @keyup.enter="onSubmit"
            />
          </label>
          <span class="icon is-medium is-left margin-left-small">
            <i class="icon search is-size-5"></i>
          </span>
        </div>
        <div class="control">
          <input
            type="submit"
            class="button is-primary"
            @click.prevent="onSubmit"
            v-on:keyup.enter.prevent="onSubmit"
            :value="$t('browse-page.search-form.button')"
          />
        </div>
      </div>
    </div>
    <div class="is-flex is-hidden-desktop">
      <button
        v-if="!isFilterVisible"
        class="button small toggle-filter padding-small"
        type="button"
        @click.prevent="onToggleSearchGridFilter()"
        v-on:keyup.enter.prevent="onToggleSearchGridFilter()"
      >
        {{ $t('filters.title') }}
      </button>
      <div class="field has-addons search-input">
        <div class="control has-icons-left margin-left-small">
          <label for="searchInputMobile">
            <input
              :aria-label="$t('browse-page.aria.search')"
              id="searchInputMobile"
              required="required"
              autofocus="true"
              class="input"
              type="search"
              ref="search"
              :placeholder="searchBoxPlaceholder"
              v-model="searchTermsModel"
              @keyup.enter="onSubmit"
            />
          </label>
          <span class="icon is-left">
            <i class="icon search is-size-6"></i>
          </span>
        </div>
        <div class="control">
          <input
            type="submit"
            class="button is-primary small"
            :value="$t('browse-page.search-form.button')"
          />
        </div>
      </div>
    </div>
  </form>
</template>

<script>
import { SET_FILTER_IS_VISIBLE } from '@/store/mutation-types'

export default {
  name: 'search-grid-form',
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
      const type = this.$route.path.split('search/')[1] || 'image' // fall back to images
      return `Search all ${type}s`
    },
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
    /**
     * If we're on the audio or video tab, we want to set the search query on change
     * rather than on submit, so the meta search buttons update live witout the user
     * having to manually submit a new search term.
     */
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
  watch: {
    searchTerms: function handler() {
      this.setFormInput()
    },
  },
  mounted: function handler() {
    this.setFormInput()
  },
}
</script>

<style lang="scss" scoped>
@import 'bulma/sass/utilities/_all.sass';

.toggle-filter {
  height: 3.875rem;
  text-transform: none;
  font-size: 13px;
  border: 2px solid #d8d8d8;
  box-sizing: border-box;
  border-radius: 4px;
  width: 68px;

  &.small {
    height: 2.5rem;
  }
}

.search-form {
  width: 100%;
  top: 0;
  position: sticky;
  background-color: #f5f5f5;
  z-index: 10;
}

.search-input {
  width: 70%;

  @include touch {
    width: 100%;
  }

  .control:first-child {
    width: 100%;
  }
}

.button .icon {
  height: auto;
}

.icon {
  margin-top: auto;
  margin-bottom: auto;
  bottom: 0;
  .search {
    padding: 1.2rem;
    max-height: 2.5rem;
    max-width: 2.5rem;

    @include touch {
      padding: 0.8rem;
    }
  }
}
</style>
