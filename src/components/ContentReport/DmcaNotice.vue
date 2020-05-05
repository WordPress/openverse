<template>
  <div>
    <span class="is-block padding-horizontal-big margin-top-large">
      Please fill out
      <a :href="dmcaFormUrl" target="_blank" rel="noopener">this DMCA form</a>
      to report dmca infringement.
    </span>
    <span class="is-block padding-horizontal-big margin-top-small">
      We recommend doing the same
      <a :href="imageURL" target="_blank" rel="noopener">at the source {{ providerName }}</a>.
    </span>

    <button class="button is-text tiny margin-top-normal is-shadowless has-text-grey"
            @click="onBackClick()">
      <span><i class="icon chevron-left margin-right-small"></i> Back</span>
    </button>
  </div>
</template>

<script>
import { BACK_TO_REPORT_START } from '@/store/mutation-types';

export default {
  name: 'dmca-notice',
  props: ['dmcaFormUrl', 'imageURL', 'providerName'],
  methods: {
    onBackClick() {
      this.$store.commit(BACK_TO_REPORT_START);
    },
  },
};
</script>
