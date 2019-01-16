<template>
  <div class="photo_tags grid-x full" v-if="tags && tags.length">
    <header>
      <h2>Tags</h2>
    </header>
    <div class="photo_tags-ctr cell large-12">
      <template v-for="(tag, index) in getValidTags()">
        <span class="photo_tag button hollow secondary"
              :key="index"
              @click="searchByTagName(tag.name)">
          <span class="photo_tag-label">
            <span>{{ tag.name }}</span>
          </span>
          <img class="photo_tag-provider-badge"
                src="@/assets/clarifai_logo.png"
                v-if="isClarifaiTag(tag.provider)">
        </span>
      </template>
      <p class="photo_tags-clarifai-badge" v-if="hasClarifaiTags">
        <span>Tag by</span>
        <a href="https://clarifai.com/">
          <img class="photo_tags-clarifai-badge-image" src="../assets/clarifai.svg" >
        </a>
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'photo-tags',
  props: ['tags'],
  methods: {
    isClarifaiTag(provider) {
      let isClarifaiTag = false;

      if (provider === 'clarifai') {
        isClarifaiTag = true;
        this.hasClarifaiTags = true;
      }

      return isClarifaiTag;
    },
    searchByTagName(query) {
      this.$router.push({ name: 'browse-page', query: { q: query } });
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

