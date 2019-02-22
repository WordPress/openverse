<template>
  <button type="button"
          class="button photo_copy-btn">
    <slot v-if="!success" default />
    <template v-else>Copied!</template>
  </button>
</template>

<script>
import Clipboard from 'clipboard';
import { COPY_ATTRIBUTION } from '@/store/action-types';

export default {
  data: () => ({
    clipboard: null,
    success: false,
  }),
  props: {
    toCopy: {
      required: true,
    },
    contentType: {
      required: true,
    },
  },
  mounted() {
    this.clipboard = new Clipboard(this.$el, {
      text: () => this.toCopy().replace(/\s\s/g, ''),
    });

    this.clipboard.on('success', (e) => {
      this.success = true;
      this.$store.dispatch(COPY_ATTRIBUTION, {
        contentType: this.$props.contentType,
        content: e.text,
      });
      setTimeout(() => {
        this.success = false;
      }, 2000);
    });
  },
  destroyed() {
    // unattach our clipboard instance when component is destroyed
    this.clipboard.destroy();
    this.clipboard = null;
  },
};
</script>

<style scoped>
  .photo_copy-btn {
    border-radius: 3px;
    width: 49%;
    background: #4a69ca;
  }
</style>
