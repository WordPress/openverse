<template>
  <div class="photo-detail-page grid-x">
    <div class="cell">
      <header-section showNavSearch="true" />
    </div>
    <div class="container cell large-11">
      <photo-details :image="image"
                    :breadCrumbURL="breadCrumbURL"
                    :shouldShowBreadcrumb="shouldShowBreadcrumb"
                    :query="query"
                    :imageWidth="imageWidth"
                    :imageHeight="imageHeight"
                    :watermarkEnabled="watermarkEnabled"
                    :socialSharingEnabled="socialSharingEnabled"
                    @onImageLoaded="onImageLoaded" />
      <photo-tags :tags="tags" />
      <related-images :relatedImages="relatedImages"
                      :imagesCount="imagesCount"
                      :query="query"
                      :filter="filter"
                      :isPrimaryImageLoaded="isPrimaryImageLoaded" />
    </div>
    <footer-section></footer-section>
  </div>
</template>

<script>
import PhotoDetails from '@/components/PhotoDetails';
import PhotoTags from '@/components/PhotoTags';
import RelatedImages from '@/components/RelatedImages';
import HeaderSection from '@/components/HeaderSection';
import FooterSection from '@/components/FooterSection';
import PhotoDetailMixin from '@/pages/mixins/PhotoDetailMixin';

const PhotoDetailPage = {
  components: {
    HeaderSection,
    RelatedImages,
    FooterSection,
    PhotoDetails,
    PhotoTags,
  },
  mixins: [PhotoDetailMixin],
};

export default PhotoDetailPage;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  .container {
    margin-left: 4vw;
    @media screen and (max-width: 1050px) {
      margin-left: 0;
    }
  }
</style>
