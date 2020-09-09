<template>
  <div v-if="tags && tags.length" class="photo_tags">
    <h3 v-if="showHeader" class="b-header">
      {{ $t('photo-details.information.tags') }}
    </h3>
    <div class="margin-top-normal">
      <template v-for="(tag, index) in getValidTags()">
        <button
          :key="index"
          class="button tag margin-smaller"
          @click="searchByTagName(tag.name)"
          @keyup.enter="searchByTagName(tag.name)"
        >
          {{ tag.name }}
        </button>
      </template>
    </div>
  </div>
</template>

<script>
import { SET_QUERY } from '~/store-modules/mutation-types'

export default {
  name: 'PhotoTags',
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
@import '~/styles/photodetails.scss';
</style>
