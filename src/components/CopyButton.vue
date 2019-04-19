<template>
  <button type="button"
          class="button photo_copy-btn"
          :data-clipboard-target="el">
    <slot v-if="!success" default />
    <template v-else>Copied!</template>
  </button>
</template>

<script>
import Clipboard from 'clipboard';
import { COPY_ATTRIBUTION } from '@/store/action-types';

let clipboard = null;

export default {
  data: () => ({
    success: false,
  }),
  props: {
    el: {
      required: true,
    },
  },
  methods: {
    onCopySuccess(e) {
      this.success = true;
      this.$store.dispatch(COPY_ATTRIBUTION, {
        contentType: 'rtf',
        content: e.text,
      });

      setTimeout(() => {
        this.success = false;
      }, 2000);

      e.clearSelection();
    },
    onCopyError(e) {
      e.clearSelection();
    },
  },
  mounted() {
    clipboard = new Clipboard('.photo_copy-btn');
    clipboard.on('success', this.onCopySuccess);
    clipboard.on('error', this.onCopyError);
  },
  destroyed() {
    clipboard.destroy();
  },
};
</script>

<style scoped>
  .photo_copy-btn {
    border-radius: 3px;
    width: 10rem;
    background: #4a69ca;
  }
</style>
