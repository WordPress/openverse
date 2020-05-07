<template>
  <div>
    <span class="is-block padding-horizontal-big margin-top-large has-text-centered">
      Please fill out this
      <a :href="dmcaFormUrl" target="_blank" rel="noopener">DMCA form</a>
      to report copyright infringement.
    </span>
    <span class="is-block padding-horizontal-big margin-top-small has-text-centered">
      We recommend doing the same at the source,
      <a :href="imageURL" target="_blank" rel="noopener">{{ providerName }}</a>.
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
