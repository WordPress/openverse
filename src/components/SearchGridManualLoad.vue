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
      <div
        v-if="isFetchingImagesError"
        class="search-grid_notification callout alert"
      >
        <h5>
          {{
            $t('browse-page.fetching-error', {
              type: $t('browse-page.search-form.audio'),
            })
          }}
          {{ _errorMessage }}
        </h5>
      </div>
      <div class="pb-6">
        <div v-if="!isFetchingImagesError && !isFinished" class="load-more">
          <button
            v-show="!isFetchingImages && includeAnalytics"
            class="button"
            @click="onLoadMoreImages"
            @keyup.enter="onLoadMoreImages"
          >
            <span>{{ $t('browse-page.load') }}</span>
          </button>
          <LoadingIcon v-show="isFetchingImages" />
        </div>
        <MetaSearchForm
          type="image"
          :noresult="storeImagesCount === 0"
          :supported="true"
        />
      </div>
    </div>
  </section>
</template>

<script>
import { FETCH_MEDIA } from '~/constants/action-types'
import { SET_MEDIA } from '~/constants/mutation-types'
import { IMAGE } from '~/constants/media'
import { mapActions, mapMutations, mapState } from 'vuex'

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
  async fetch() {
    if (!this.storeImages.length) {
      await this.fetchMedia({
        ...this.$store.state.query,
        mediaType: IMAGE,
      })
    }
  },
  computed: {
    ...mapState({
      isFetchingImages: 'isFetching.images',
      isFetchingImagesError: 'isFetchingError.images',
      storeImages: 'images',
      storeImagesCount: 'imagesCount',
      currentPage: 'imagePage',
      _errorMessage: 'errorMessage',
    }),
    _images() {
      return this.useInfiniteScroll ? this.storeImages : this.images
    },
    _imagesCount() {
      const count = this.useInfiniteScroll
        ? this.storeImagesCount
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
    isFinished() {
      return this.currentPage >= this.$store.state.pageCount.images
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
    ...mapMutations({
      setMedia: SET_MEDIA,
    }),
    ...mapActions({
      fetchMedia: FETCH_MEDIA,
    }),
    searchChanged() {
      this.setMedia({ media: [], page: 1 })
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
