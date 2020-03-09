<template>
  <button :id="id"
          type="button"
          class="button is-info is-block margin-top-small"
          :data-clipboard-target="el">
    <slot v-if="!success" default />
    <template v-else>Copied!</template>
  </button>
</template>

<script>
import Clipboard from 'clipboard';

export default {
  data: () => ({
    success: false,
    clipboard: null,
  }),
  props: {
    el: {
      required: true,
    },
    id: {
      required: true,
    },
  },
  methods: {
    onCopySuccess(e) {
      this.success = true;
      this.$emit('copied', { content: e.text });

      setTimeout(() => {
        this.success = false;
      }, 2000);

      e.clearSelection();
    },
    onCopyError(e) {
      this.$emit('copyFailed');
      e.clearSelection();
    },
  },
  mounted() {
    this.clipboard = new Clipboard(`#${this.$props.id}`);
    this.clipboard.on('success', this.onCopySuccess);
    this.clipboard.on('error', this.onCopyError);
  },
  destroyed() {
    this.clipboard.destroy();
  },
};
</script>

