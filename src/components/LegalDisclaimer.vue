<template>
  <div>
    <span>Verify at source - Flickr</span>
    <p class="legal-disclaimer">
      CC Search aggregates data from publicly available repositories of open content.
      CC does not host the content and is not able to determine whether the content was
      properly placed under a CC license or whether the attribution information about the
      content is correct. Please follow the link to the source of the content to independently
      verify before reuse.
    </p>
  </div>
</template>

<script>
import Tooltip from '@/components/Tooltip';

export default {
  name: 'legal-disclaimer',
  components: {
    Tooltip,
  },
};
</script>

<style lang="scss" scoped>
  @import '../styles/photodetails.scss';
</style>
