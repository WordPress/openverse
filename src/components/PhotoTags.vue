<template>
  <div class="photo_tags margin-normal" v-if="tags && tags.length">
    <h3>Tags</h3>
    <div class="margin-top-normal">
      <template v-for="(tag, index) in getValidTags()">
        <button class="button tag margin-left-small"
              :key="index"
              @click="searchByTagName(tag.name)">
          {{ tag.name }}
        </button>
      </template>
    </div>
  </div>
</template>

<script>
import { SET_QUERY } from '@/store/mutation-types';

export default {
  name: 'photo-tags',
  props: ['tags'],
  computed: {
    hasClarifaiTags() {
      return this.$props.tags.some(tag => tag.provider === 'clarifai');
    },
  },
  methods: {
    isClarifaiTag(provider) {
      return provider === 'clarifai';
    },
    searchByTagName(query) {
      this.$store.commit(SET_QUERY, { query: { q: query }, shouldNavigate: true });
    },
    getValidTags() {
      return this.$props.tags.filter(tag => !!tag.name);
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../styles/photodetails.scss';
</style>
