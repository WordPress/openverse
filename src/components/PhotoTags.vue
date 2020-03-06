<template>
  <div class="photo_tags" v-if="tags && tags.length">
    <header>
      <h2>Tags</h2>
    </header>
    <div class="photo_tags-ctr">
      <template v-for="(tag, index) in getValidTags()">
        <span class="photo_tag button hollow secondary"
              :key="index"
              @click="searchByTagName(tag.name)">
          <span class="photo_tag-label">
            <span>{{ tag.name }}</span>
          </span>
        </span>
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
