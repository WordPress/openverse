<template>
  <div v-show="!isError" class="load-more pb-6">
    <button
      v-show="!isFetching"
      class="button"
      :disabled="isFinished"
      @click="onLoadMore"
      @keyup.enter="onLoadMore"
    >
      <span>{{ buttonLabel }}</span>
    </button>
    <LoadingIcon v-show="isFetching" />
  </div>
</template>
<script>
import LoadingIcon from '~/components/LoadingIcon'

export default {
  name: 'LoadMoreButton',
  components: { LoadingIcon },
  props: {
    isFetching: {
      type: Boolean,
      default: true,
    },
    isFinished: {
      type: Boolean,
      default: false,
    },
    isError: {
      type: Boolean,
      default: false,
    },
    mediaType: {
      type: String,
      default: 'image',
    },
  },
  computed: {
    finishedLabel() {
      const type = this.$t(`browse-page.search-form.${this.mediaType}`)
      return this.$t('browse-page.no-more', { type })
    },
    buttonLabel() {
      return this.isFinished ? this.finishedLabel : this.$t('browse-page.load')
    },
  },
  methods: {
    onLoadMore() {
      this.$emit('onLoadMore')
    },
  },
}
</script>
<style lang="scss" scoped>
.load-more {
  display: flex;
  justify-content: center;
}
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
</style>
