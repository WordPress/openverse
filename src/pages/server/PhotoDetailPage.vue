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
      <photo-tags :tags="tags" />
    </div>
    <footer-section></footer-section>
  </div>
</template>

<script>
import PhotoDetails from '@/components/ImageDetails/PhotoDetails';
import PhotoTags from '@/components/PhotoTags';
import HeaderSection from '@/components/HeaderSection';
import FooterSection from '@/components/FooterSection';
import PhotoDetailMixin from '@/pages/mixins/PhotoDetailMixin';

const PhotoDetailPage = {
  components: {
    HeaderSection,
    FooterSection,
    PhotoDetails,
    PhotoTags,
  },
  mixins: [PhotoDetailMixin],
};

export default PhotoDetailPage;
</script>
