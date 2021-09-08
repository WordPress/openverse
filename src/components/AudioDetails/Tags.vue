<template>
  <div v-if="tags && tags.length" class="media_tags">
    <h3 v-if="showHeader" class="b-header">
      {{ header }}
    </h3>
    <div>
      <MediaTag
        v-for="(tag, index) in getValidTags()"
        :key="index"
        class="mr-4"
      >
        {{ tag.name }}
      </MediaTag>
    </div>
  </div>
</template>

<script>
import { SET_QUERY } from '~/store-modules/mutation-types'

export default {
  name: 'AudioTags',
  props: ['tags', 'header'],
  computed: {
    showHeader() {
      return this.$props.header !== ''
    },
  },
  methods: {
    isClarifaiTag(provider) {
      return provider === 'clarifai'
    },
    searchByTagName(query) {
      this.$store.commit(SET_QUERY, { query: { q: query } })
    },
    getValidTags() {
      return this.$props.tags.filter((tag) => !!tag.name)
    },
  },
}
</script>
