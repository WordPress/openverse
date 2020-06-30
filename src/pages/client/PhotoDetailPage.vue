<template>
  <div class="photo-detail-page">
    <header-section showNavSearch="true" />
    <div>
      <photo-details :image="image"
                    :breadCrumbURL="breadCrumbURL"
                    :shouldShowBreadcrumb="shouldShowBreadcrumb"
                    :query="query"
                    :imageWidth="imageWidth"
                    :imageHeight="imageHeight"
                    :socialSharingEnabled="socialSharingEnabled"
                    @onImageLoaded="onImageLoaded" />
      <div class="padding-normal margin-vertical-big">
        <photo-tags :tags="tags" :showHeader="true" />
      </div>
      <div class="padding-normal margin-vertical-big">
        <related-images :relatedImages="relatedImages"
                        :imagesCount="imagesCount"
                        :query="query"
                        :filter="filter"
                        :isPrimaryImageLoaded="isPrimaryImageLoaded" />
      </div>
    </div>
    <footer-section></footer-section>
  </div>
</template>

<script>
import PhotoDetails from '@/components/ImageDetails/PhotoDetails';
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
  metaInfo() {
    return {
      meta: [
        {
          vmid: 'monetization',
          content: null,
        },
      ],
    };
  },
};

export default PhotoDetailPage;
</script>
