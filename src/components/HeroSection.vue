<template>
  <!-- eslint-disable vuejs-accessibility/no-autofocus -->
  <div class="hero">
    <div class="text-center mt-16">
      <h1 class="text-5xl pb-4">
        {{ $t('hero.title') }}
      </h1>
      <h2 class="text-2xl font-medium">
        {{ $t('hero.subtitle') }}
      </h2>
      <form
        class="relative w-full px-2 mt-12"
        role="search"
        method="get"
        action="/search"
        @submit.prevent="onSubmit"
      >
        <div class="flex justify-center">
          <input
            id="searchTerm"
            v-model.lazy="form.searchTerm"
            required="required"
            class="hero-search__input input rounded rounded-e-none -me-px text-start lg:px-10 w-full max-w-full"
            :aria-label="$t('hero.aria.search')"
            autofocus
            type="search"
            name="q"
            :placeholder="$t('hero.search.placeholder')"
            autocapitalize="none"
          />
          <button
            class="hero-search__button button is-primary rounded rounded-s-none"
            title="Search"
          >
            {{ $t('hero.search.button') }}
          </button>
        </div>

        <div v-if="showSearchType" class="flex flex-col items-center">
          <p class="py-2">{{ $t('hero.search-type.prompt') }}</p>
          <SearchTypeToggle v-model.lazy="form.searchType" />
        </div>

        <div class="text-sm mt-6 font-medium">
          <i18n path="hero.caption.content" tag="p">
            <template #link>
              <a
                href="https://creativecommons.org/share-your-work/licensing-examples/"
                target="_blank"
                :aria-label="$t('hero.aria.caption')"
                rel="noopener"
              >
                {{ $t('hero.caption.link') }}
              </a>
            </template>
          </i18n>
        </div>
        <HomeLicenseFilter :filters="filters" @toggle="toggleFilter" />
      </form>
    </div>
    <img
      class="logo-cloud"
      src="~/assets/logo-cloud.png"
      alt="Logos from sources of Openverse licensed images"
    />
  </div>
  <!-- eslint-enable -->
</template>

<script>
import { UPDATE_QUERY, TOGGLE_FILTER } from '~/constants/action-types'
import { SEARCH } from '~/constants/store-modules'
import { mapActions, mapGetters } from 'vuex'
import HomeLicenseFilter from '~/components/HomeLicenseFilter'
import SearchTypeToggle from '~/components/SearchTypeToggle'

export default {
  name: 'HeroSection',
  components: { HomeLicenseFilter, SearchTypeToggle },
  /**
   * @return {{ form: { searchTerm: string, searchType: 'image' | 'audio' }, showSearchType: boolean }}
   */
  data: () => ({
    form: { searchTerm: '', searchType: 'image' },
    filters: { commercial: false, modification: false },
    showSearchType: process.env.enableAudio || false,
  }),
  computed: {
    ...mapGetters(SEARCH, ['searchQueryParams']),
  },
  mounted() {
    if (document.querySelector('#searchTerm')) {
      document.querySelector('#searchTerm').focus()
    }
  },
  methods: {
    ...mapActions(SEARCH, {
      setSearchTerm: UPDATE_QUERY,
      checkFilter: TOGGLE_FILTER,
    }),
    getPath() {
      if (!process.env.enableAudio) return '/search/image'
      return `/search/${this.form.searchType}`
    },
    getMediaType() {
      return this.form.searchType
    },
    toggleFilter({ code, checked }) {
      this.filters[code] = checked
    },
    onSubmit() {
      const newQuery = { q: this.form.searchTerm }

      Object.entries(this.filters).forEach(([filterCode, isChecked]) => {
        if (isChecked) {
          this.checkFilter({ filterType: 'licenseTypes', code: filterCode })
        }
      })

      if (process.env.enableAudio) {
        newQuery.searchType = this.form.searchType
      }
      this.setSearchTerm(newQuery)
      const newPath = this.localePath({
        path: this.getPath(),
        query: this.searchQueryParams,
      })
      this.$router.push(newPath)
    },
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
$hero-height-desktop: 85vh;
$hero-height: 55vh;

.hero {
  background: #fff;
  position: relative;
  background-size: cover;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  min-height: $hero-height;
  @include tablet() {
    min-height: $hero-height-desktop;
  }
}
.hero-search {
  &__input {
    @screen lg {
      width: 570px;
      font-size: 1.75rem;
      height: 5.063rem;
    }
  }
  &__button {
    font-size: 1rem;
    padding: 0.5rem 1.2rem;
    @screen lg {
      font-size: 1.75rem;
      padding-left: var(--button-padding-horizontal);
      padding-right: var(--button-padding-horizontal);
      height: 5.063rem;
    }
  }
}

.logo-cloud {
  z-index: 0;
  margin-top: auto;
  width: 100%;
  padding-left: 1rem;
  height: 120px;
  object-fit: cover;
  object-position: left center;

  @screen lg {
    object-fit: initial;
    height: auto;
    padding: 0;
    margin-top: 4rem;
    margin-left: auto;
    margin-right: auto;
    width: calc(100% - 1rem);
    max-width: 1400px;
  }
}
</style>
