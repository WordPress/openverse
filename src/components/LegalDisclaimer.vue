<template>
  <div v-if="sourceURL" class="provider-container">
    <span>Verify at the source:</span>
    <div>
      <a :href="sourceURL"
          target="blank"
          rel="noopener noreferrer">
        <img class="provider-logo"
            :alt="source"
            :src="getProviderLogo(sourceProviderCode)" />
      </a>
      <p class="legal-disclaimer">
        CC Search aggregates data from publicly available repositories of open content.<br />
        CC does not host the content and does not verify that the content is properly CC-licensed
        or that the attribution information is accurate or complete.<br />
        Please follow the link to the source of the content to independently verify before reuse.
      </p>
    </div>
  </div>
</template>

<script>
import Tooltip from '@/components/Tooltip';
import getProviderLogo from '@/utils/getProviderLogo';

export default {
  name: 'legal-disclaimer',
  props: ['source', 'sourceProviderCode', 'sourceURL'],
  components: {
    Tooltip,
  },
  methods: {
    getProviderLogo(providerName) {
      return getProviderLogo(providerName);
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../styles/photodetails.scss';
</style>
