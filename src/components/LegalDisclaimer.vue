<template>
  <div>
    <a :href="sourceURL">Verify at source - {{ source }}</a>
    <p class="legal-disclaimer">
      CC Search aggregates data from publicly available repositories of open content.
      CC does not host the content and does not verify that the content is properly CC-licensed
      or that the attribution information is accurate or complete. Please follow the link to the
      source of the content to independently verify before reuse.
    </p>
  </div>
</template>

<script>
import Tooltip from '@/components/Tooltip';

export default {
  name: 'legal-disclaimer',
  props: ['source', 'sourceURL'],
  components: {
    Tooltip,
  },
};
</script>

<style lang="scss" scoped>
  @import '../styles/photodetails.scss';
</style>
