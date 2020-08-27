<template>
  <div class="photo_tags" v-if="tags && tags.length">
    <h3 class="b-header" v-if="showHeader">
      {{ $t('photo-details.information.tags') }}
    </h3>
    <div class="margin-top-normal">
      <template v-for="(tag, index) in getValidTags()">
        <button
          class="button tag margin-smaller"
          :key="index"
          @click="searchByTagName(tag.name)"
          v-on:keyup.enter="searchByTagName(tag.name)"
        >
          {{ tag.name }}
        </button>
      </template>
    </div>
  </div>
</template>

<script>
import { SET_QUERY } from '../store/mutation-types'

export default {
  name: 'photo-tags',
  props: ['tags', 'showHeader'],
  computed: {
    hasClarifaiTags() {
      return this.$props.tags.some((tag) => tag.provider === 'clarifai')
    },
  },
  methods: {
    isClarifaiTag(provider) {
      return provider === 'clarifai'
    },
    searchByTagName(query) {
      this.$store.commit(SET_QUERY, {
        query: { q: query },
        shouldNavigate: true,
      })
    },
    getValidTags() {
      return this.$props.tags.filter((tag) => !!tag.name)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '../styles/photodetails.scss';
</style>
