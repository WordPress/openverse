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
        <span class="caption has-text-weight-semibold">
          {{ _imagesCount }}
        </span>
        <div class="is-hidden-touch mr-auto padding-left-big">
          <SearchRating v-if="_query.q" :search-term="_query.q" />
        </div>
        <div class="is-hidden-desktop is-block">
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
      <div class="padding-bottom-big">
        <div class="load-more">
          <button
            v-show="!isFetchingImages && includeAnalytics"
            class="button margin-bottom-big"
            :disabled="isFinished"
            @click="onLoadMoreImages"
            @keyup.enter="onLoadMoreImages"
          >
            <span v-if="isFinished">{{ $t('browse-page.no-more') }}</span>
            <span v-else>{{ $t('browse-page.load') }}</span>
          </button>
          <LoadingIcon v-show="isFetchingImages" />
        </div>
        <button
          type="button"
          class="meta-popup-trigger has-color-tomato text-center caption padding-normal"
          @click="showMetaImageSearch = true"
          @keyup.enter="showMetaImageSearch = true"
        >
          {{ $t('browse-page.other-source') }}
        </button>
      </div>
      <div
        v-if="isFetchingImagesError"
        class="search-grid_notification callout alert"
      >
        <h5>{{ $t('browse-page.error') }} {{ _errorMessage }}</h5>
      </div>
    </div>

    <AppModal
      v-if="showMetaImageSearch"
      :title="'Search Images from Other Sources'"
      @close="showMetaImageSearch = false"
    >
      <MetaSearchCard
        type="image"
        :query="query"
        @close="showMetaImageSearch = false"
      />
    </AppModal>
  </section>
</template>

<script>
import { SET_IMAGES } from '~/store-modules/mutation-types'

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
      return this.$store.state.isFetchingImagesError
    },
    isFetchingImages() {
      return this.$store.state.isFetchingImages
    },
    _images() {
      return this.useInfiniteScroll ? this.$store.state.images : this.images
    },
    currentPage() {
      return this.$store.state.imagePage
    },
    _imagesCount() {
      const count = this.useInfiniteScroll
        ? this.$store.state.imagesCount
        : this.imagesCount
      return count >= 10000
        ? this.$t('browse-page.result-count-more', {
            count: count.toLocaleString(this.$i18n.locale),
          })
        : this.$t('browse-page.result-count', {
            count: count.toLocaleString(this.$i18n.locale),
          })
    },
    _query() {
      return this.$props.query
    },
    _errorMessage() {
      return this.$store.state.errorMsg
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
    handleScalingChange() {
      setTimeout(() => {
        this.$redrawVueMasonry()
      }, 100)
    },
    searchChanged() {
      this.$store.commit(SET_IMAGES, { images: [], page: 1 })
    },
    onLoadMoreImages() {
      const searchParams = {
        page: this.currentPage + 1,
        shouldPersistImages: true,
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
  .masonry-layout {
    margin: auto;
    margin-top: 1rem;
  }

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
    font-size: 1.2em;

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

.mr-auto {
  margin-right: auto;
}

.meta-popup-trigger {
  appearance: none;
  border: none;
  background-color: transparent;
  text-align: center;
  display: block;
  margin: 0 auto;
  cursor: pointer;

  &:hover {
    text-decoration: underline;
  }
}
</style>
