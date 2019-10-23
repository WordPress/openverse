<template>
  <div>
    <div v-if="sourceURL" class="verify-source">
      <span>Verify at the source:</span>
      <div class="provider-container">
        <a :href="sourceURL"
            target="blank"
            rel="noopener noreferrer">
          <img class="provider-logo"
              :alt="source"
              :src="getProviderLogo(sourceProviderCode)" />
          <span>{{source}}</span>
        </a>
      </div>
    </div>

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

  .verify-source {
    font-weight: 600;
    font-size: 1.1em;
  }
</style>
