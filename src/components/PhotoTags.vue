<template>
  <div v-if="tags && tags.length" class="photo_tags">
    <h3 v-if="showHeader" class="b-header">
      {{ $t('photo-details.information.tags') }}
    </h3>
    <div class="mt-4">
      <template v-for="(tag, index) in getValidTags()">
        <button
          :key="index"
          class="button tag m-1"
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
import { SET_Q } from '~/constants/mutation-types'
import { SEARCH } from '~/constants/store-modules'
import { mapMutations } from 'vuex'

export default {
  name: 'PhotoTags',
  props: ['tags', 'showHeader'],
  computed: {
    hasClarifaiTags() {
      return this.$props.tags.some((tag) => tag.provider === 'clarifai')
    },
  },
  methods: {
    ...mapMutations(SEARCH, { setSearchTerm: SET_Q }),
    isClarifaiTag(provider) {
      return provider === 'clarifai'
    },
    searchByTagName(query) {
      this.setSearchTerm({ q: query })
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
