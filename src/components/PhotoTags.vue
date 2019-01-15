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
  .photo_related-images,
  .photo_tags {
    margin: 30px;
    border-top: 1px solid #e7e8e9;
    width: 100%;

    header h2 {
      margin-bottom: 1.07142857em;
      width: 100%;
      font-size: 1em;
      font-weight: 600;
      letter-spacing: 1px;
      line-height: 1.25;
      text-transform: uppercase;
      display: inline-block;
      padding-top: .28571429em;
      border-top: 5px solid rgba(29, 31, 39, 0.8);
      margin-top: -3px;
    }

    /* Small only */
    @media screen and (max-width: 39.9375em) {
      margin: 15px;
    }
  }

  .photo_tag {
    margin-right: 15px;
    border-radius: 3px;
    padding: 10px 10px;
  }

  .photo_tag-label {
    font-weight: 500;
  }

  .photo_tag-provider-badge {
    width: 16px;
    margin-left: 5px;
  }

  .photo_tags-clarifai-badge {
    margin-top: 30px;
  }

  .photo_tags-clarifai-badge-image {
    height: 20px;
  }
</style>

