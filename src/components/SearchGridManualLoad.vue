<template>
  <section
    ref="searchGrid"
    :class="{
      'search-grid': true,
      'search-grid__contain-images': shouldContainImages,
    }"
  >
    <div ref="gridItems" class="search-grid_ctr">
      <div
        v-show="!fetchingState.isFetching && includeAnalytics"
        class="results-meta"
      >
        <span class="caption font-semibold">
          {{ _imagesCount }}
        </span>
        <div class="hidden lg:block lg:me-auto lg:ps-6">
          <SearchRating v-if="searchTerm" :search-term="searchTerm" />
        </div>
        <SaferBrowsing />
      </div>
      <div class="search-grid-cells">
        <SearchGridCell
          v-for="(image, index) in results.items"
          :key="index"
          :image="image"
        />
      </div>
      <div
        v-if="!!fetchingState.error"
        class="search-grid_notification callout alert"
      >
        <h5>
          {{
            $t('browse-page.fetching-error', {
              type: $t('browse-page.search-form.audio'),
            })
          }}
          {{ fetchingState.fetchingError }}
        </h5>
      </div>
      <div class="pb-6">
        <div
          v-if="!fetchingState.fetchingError && !isFinished"
          class="load-more"
        >
          <button
            v-show="!fetchingState.isFetching && includeAnalytics"
            class="button"
            @click="onLoadMoreImages"
            @keyup.enter="onLoadMoreImages"
          >
            <span>{{ $t('browse-page.load') }}</span>
          </button>
          <LoadingIcon v-show="fetchingState.isFetching" />
        </div>
        <MetaSearchForm
          type="image"
          :noresult="!fetchingState.isFetching && results.count === 0"
          :supported="true"
        />
      </div>
    </div>
  </section>
</template>

<script>
import { FETCH_MEDIA } from '~/constants/action-types'
import { RESET_MEDIA } from '~/constants/mutation-types'
import { IMAGE } from '~/constants/media'
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex'
import { MEDIA, SEARCH } from '~/constants/store-modules'

export default {
  name: 'SearchGridManualLoad',
  props: {
    useInfiniteScroll: {
      default: true,
    },
    includeAnalytics: {
      default: true,
    },
    includeAddToList: {
      default: true,
    },
    searchTerm: {
      default: '',
    },
  },
  data: () => ({
    isDataInitialized: false,
    shouldContainImages: false,
    showMetaImageSearch: false,
  }),
  computed: {
    ...mapState(SEARCH, ['query']),
    ...mapGetters(MEDIA, ['fetchingState', 'results', 'isFinished']),
    _imagesCount() {
      const count = this.results.count
      if (count === 0) {
        return this.$t('browse-page.image-no-results')
      }
      const localeCount = count.toLocaleString(this.$i18n.locale)
      const i18nKey =
        count >= 10000
          ? 'browse-page.image-result-count-more'
          : 'browse-page.image-result-count'
      return this.$tc(i18nKey, count, { localeCount })
    },
    _query() {
      return this.query
    },
  },
  watch: {
    _query: {
      handler() {
        this.searchChanged()
      },
      deep: true,
    },
  },
  methods: {
    ...mapMutations(MEDIA, { resetMedia: RESET_MEDIA }),
    ...mapActions(MEDIA, { fetchMedia: FETCH_MEDIA }),
    searchChanged() {
      this.resetMedia({ mediaType: IMAGE })
    },
    onLoadMoreImages() {
      const searchParams = {
        page: this.results.page + 1,
        shouldPersistMedia: true,
        ...this._query,
      }

      this.$emit('onLoadMoreImages', searchParams)
    },
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
.search-grid:after {
  content: '';
  display: block;
  clear: both;
}

.search-grid_notification {
  width: 50%;
  margin: auto;
  font-weight: 500;
  text-align: center;
}

.search-grid-cells {
  display: flex;
  flex-wrap: wrap;
  margin: 10px;

  @include tablet {
    &:after {
      content: '';
      flex-grow: 999999999;
    }
  }
}

label {
  color: #333333;
}

.load-more {
  text-align: center;

  button {
    color: #23282d;
    margin-top: 2rem;
    border: 1px solid rgba(35, 40, 45, 0.2);
    font-size: 1.2em;

    &:hover {
      color: white;
    }
    &:disabled {
      opacity: 1;
      &:hover {
        color: black;
      }
    }

    @include mobile {
      padding: 0.5rem;

      span {
        font-size: 0.9rem;
      }
    }
  }
}

.results-meta {
  @apply px-6 pt-2;

  @screen lg {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .button.is-text {
    font-size: 0.8rem;
  }
}
</style>
