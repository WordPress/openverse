<template>
  <section
    ref="searchGrid"
    :class="{
      'search-grid': true,
      'search-grid__contain-images': shouldContainImages,
    }"
  >
    <div ref="gridItems" class="search-grid_ctr">
      <div v-show="!isFetchingImages && includeAnalytics" class="results-meta">
        <span class="caption font-semibold">
          {{ _imagesCount }}
        </span>
        <div class="hidden desk:block mr-auto pl-6">
          <SearchRating v-if="_query.q" :search-term="_query.q" />
        </div>
        <div class="desk:hidden">
          <SearchRating v-if="_query.q" :search-term="searchTerm" />
        </div>
        <SaferBrowsing />
      </div>
      <div class="search-grid-cells">
        <SearchGridCell
          v-for="(image, index) in _images"
          :key="index"
          :image="image"
        />
      </div>
      <div class="pb-6">
        <div class="load-more">
          <button
            v-show="!isFetchingImages && includeAnalytics"
            class="button"
            :disabled="isFinished"
            @click="onLoadMoreImages"
            @keyup.enter="onLoadMoreImages"
          >
            <span v-if="isFinished">{{ $t('browse-page.no-more') }}</span>
            <span v-else>{{ $t('browse-page.load') }}</span>
          </button>
          <LoadingIcon v-show="isFetchingImages" />
        </div>
        <MetaSearchForm type="image" :query="query" :supported="true" />
      </div>
      <div
        v-if="isFetchingImagesError"
        class="search-grid_notification callout alert"
      >
        <h5>{{ $t('browse-page.fetching-error') }} {{ _errorMessage }}</h5>
      </div>
    </div>
  </section>
</template>

<script>
import { SET_MEDIA } from '~/store-modules/mutation-types'

const DEFAULT_PAGE_SIZE = 20

export default {
  name: 'SearchGridManualLoad',
  props: {
    imagesCount: {
      default: 0,
    },
    images: {
      default: () => [],
    },
    query: {},
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
    imagePage() {
      return this.$store.state.imagePage
    },
    isFetchingImagesError() {
      return this.$store.state.isFetchingError.images
    },
    isFetchingImages() {
      return this.$store.state.isFetching.images
    },
    _images() {
      return this.useInfiniteScroll ? this.$store.state.images : this.images
    },
    currentPage() {
      return this.$store.state.imagePage
    },
    _imagesCount() {
      const count = this.useInfiniteScroll
        ? this.$store.state.count.images
        : this.imagesCount
      if (count === 0) {
        return this.$t('browse-page.image-no-results')
      }
      return count >= 10000
        ? this.$tc('browse-page.image-result-count-more', count, {
            localeCount: count.toLocaleString(this.$i18n.locale),
          })
        : this.$tc('browse-page.image-result-count', count, {
            localeCount: count.toLocaleString(this.$i18n.locale),
          })
    },
    _query() {
      return this.$props.query
    },
    _errorMessage() {
      return this.$store.state.errorMessage
    },
    isFinished() {
      return this.currentPage >= this.$store.state.pageCount
    },
  },
  watch: {
    _images: {
      handler() {
        if (this.$state) {
          this.$state.loaded()
          if (this._imagesCount < this.currentPage * DEFAULT_PAGE_SIZE) {
            this.$state.complete()
          }
        }
        this.isDataInitialized = true
      },
    },
    _query: {
      handler() {
        this.searchChanged()
      },
      deep: true,
    },
  },
  methods: {
    searchChanged() {
      this.$store.commit(SET_MEDIA, { media: [], page: 1 })
    },
    onLoadMoreImages() {
      const searchParams = {
        page: this.currentPage + 1,
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
.button[disabled] {
  opacity: 1;
}

.search-grid_layout-control h5 {
  padding-top: 1.36vh;
  font-size: 1rem;
  display: inline-block;
}

.search-grid_layout-control h5 {
  margin-right: 10px;
}

.search-grid_layout-control {
  text-align: right;

  fieldset {
    display: inline;
    margin-right: 5px;
  }
}

.infinite-loading-container {
  margin-top: 30px;
  width: 100%;
}

.search-grid_ctr {
  .item {
    width: 320px;
    margin-bottom: 20px;
  }
}

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

    @include mobile {
      padding: 0.5rem;

      span {
        font-size: 0.9rem;
      }
    }
  }
}

.results-meta {
  padding-top: 0.6rem;
  padding-left: 1.3rem;
  padding-right: 1.3rem;

  @include desktop {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .button.is-text {
    font-size: 0.8rem;
  }
}
</style>
