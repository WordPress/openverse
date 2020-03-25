<template>
  <div v-if="sourceURL" class="legal-disclaimer margin-top-normal">
    <h4 class="b-header">Verify at the source</h4>
    <div class="margin-top-normal">
      <ul>
        <li class="caption margin-bottom-normal">
          CC Search aggregates data from publicly available repositories of open content.
        </li>
        <li class="caption margin-bottom-normal">
          CC does not host the content and does not verify that the content is properly
          CC-licensed or that the attribution information is accurate or complete.
        </li>
        <li class="caption margin-bottom-normal">
          Please follow the link to the source of the content to independently verify before reuse.
        </li>
      </ul>
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
<style>
  li:before{
    content: "\2022";
    color: #CCC;
    font-weight: bold;
    display: inline-block;
    width: 1em;
    margin-left: 1em;
  }
</style>
