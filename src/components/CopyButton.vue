<template>
  <button type="button"
          class="button photo_copy-btn">
    <slot v-if="!success" default />
    <template v-if="success">Copied!</template>
  </button>
</template>

<script>
import Clipboard from 'clipboard';

export default {
  data: () => ({
    clipboard: null,
    success: false,
  }),
  props: {
    toCopy: {
      required: true,
    },
  },
  mounted() {
    this.clipboard = new Clipboard(this.$el, {
      // eslint-disable-line no-new
      text: () => this.toCopy.replace(/\s\s/g, ''),
    });

    this.clipboard.on('success', () => {
      this.success = true;
      setTimeout(() => {
        this.success = false;
      }, 2000);
    });
  },
  destroyed() {
    // unattach our clipboard instance when component is destroyed
    this.clipboard.destroy();
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
