<template>
  <div class="photo-detail-page grid-x">
    <div class="cell">
      <header-section showNavSearch="true" fixedNav="true"></header-section>
    </div>
    <photo-details :image="image"
                   :breadCrumbURL="breadCrumbURL"
                   :shouldShowBreadcrumb="shouldShowBreadcrumb"
                   :query="query"
                   :imageWidth="imageWidth"
                   :imageHeight="imageHeight"
                   @onImageLoaded="onImageLoaded" />
    <share-list></share-list>
    <photo-tags :tags="tags" />
    <related-images :relatedImages="relatedImages"
                    :imagesCount="imagesCount"
                    :query="query"
                    :filter="filter"
                    :isPrimaryImageLoaded="isPrimaryImageLoaded" />
    <footer-section></footer-section>
  </div>
</template>

<script>
import PhotoDetails from '@/components/PhotoDetails';
import PhotoTags from '@/components/PhotoTags';
import RelatedImages from '@/components/RelatedImages';
import HeaderSection from '@/components/HeaderSection';
import FooterSection from '@/components/FooterSection';
import ShareList from '@/components/ShareList';
import { FETCH_IMAGE, FETCH_RELATED_IMAGES } from '@/store/action-types';
import { SET_IMAGE } from '@/store/mutation-types';

const PhotoDetailPage = {
  name: 'photo-detail-page',
  components: {
    HeaderSection,
    RelatedImages,
    FooterSection,
    PhotoDetails,
    PhotoTags,
    ShareList
  },
  props: {
    id: '',
  },
  data: () => ({
    breadCrumbURL: '',
    hasClarifaiTags: false,
    imagecountseparator: 'of',
    isPrimaryImageLoaded: false,
    shouldShowBreadcrumb: false,
    imageWidth: 0,
    imageHeight: 0,
  }),
  computed: {
    filter() {
      return this.$store.state.query.filter;
    },
    images() {
      return this.$store.state.images;
    },
    imagesCount() {
      return this.$store.state.imagesCount;
    },
    query() {
      return this.$store.state.query.q;
    },
    relatedImages() {
      return this.$store.state.relatedImages;
    },
    tags() {
      return this.$store.state.image.tags;
    },
    image() {
      return this.$store.state.image;
    },
  },
  watch: {
    tags: function tags(value) {
      this.getRelatedImages(value, this.queryParam);
    },
  },
  beforeRouteUpdate(to, from, next) {
    this.imageHeight = 0;
    this.imageWidth = 0;
    this.$store.commit(SET_IMAGE, { image: {} });
    this.loadImage(to.params.id);
    next();
  },
  beforeRouteEnter(to, previousPage, nextPage) {
    nextPage((_this) => {
      if (previousPage.name === 'browse-page') {
        _this.shouldShowBreadcrumb = true; // eslint-disable-line no-param-reassign
        _this.breadCrumbURL = `/search?q=${previousPage.query.q}`; // eslint-disable-line no-param-reassign
      }
    });
  },
  methods: {
    onImageLoaded(event) {
      this.imageWidth = event.target.naturalWidth;
      this.imageHeight = event.target.naturalHeight;
      this.isPrimaryImageLoaded = true;
    },
    getRelatedImages(tags, query) {
      let queryParam = query;
      const tagsParam = (tags || []).slice();

      if (tagsParam.length > 0) {
        queryParam = tagsParam.slice(0, 1).map(tag => tag.name).join(', ');
      }

      if (queryParam) {
        this.$store.dispatch(FETCH_RELATED_IMAGES, { q: queryParam, pagesize: 8 });
      }
    },
    loadImage(id) {
      if (id) {
        this.$store.dispatch(FETCH_IMAGE, { id });
      }
    },
  },
  created() {
    this.loadImage(this.$route.params.id);
  },
};

export default PhotoDetailPage;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>

</style>
