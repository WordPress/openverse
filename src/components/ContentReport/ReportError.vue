<template>
  <div>
    <span class="is-block">
      There was an error with the report submission. Please try again.
    </span>
    <button class="button is-text tiny margin-top-normal is-shadowless"
            @click="onBackClick()">
      <span><i class="icon chevron-left margin-right-small"></i> Back</span>
    </button>
  </div>
</template>

<script>
import { BACK_TO_REPORT_START } from '@/store/mutation-types';

export default {
  name: 'report-error',
  methods: {
    onBackClick() {
      this.$store.commit(BACK_TO_REPORT_START);
    },
  },
};
</script>
