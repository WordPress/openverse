<template>
  <button type="button"
          class="button photo_copy-btn">
    <slot v-if="!success" default />
    <template v-else>Copied!</template>
  </button>
</template>

<script>
import { COPY_ATTRIBUTION } from '@/store/action-types';

export default {
  data: () => ({
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
  methods: {
    listener(clickEvent) {
      // Prepare the content to copy into the clipboard
      const content = this.toCopy().replace(/\s\s/g, '');

      // Load the content into the clipboard
      const copier = (event) => {
        // If the content type is RTF, paste as rich text into the clipboard
        if (this.contentType === 'rtf') {
          event.clipboardData.setData('text/html', content);
        }
        // Paste as plain text into the clipboard
        event.clipboardData.setData('text/plain', content);
        // Prevent the default action
        event.preventDefault();
      };
      document.addEventListener('copy', copier);
      document.execCommand('copy');
      document.removeEventListener('copy', copier);

      // Set the success flag and log the copy action for Analytics
      this.success = true;
      this.$store.dispatch(COPY_ATTRIBUTION, {
        contentType: this.$props.contentType,
        content,
      });

      // Set a timeout for the success flag to be reset
      setTimeout(() => {
        this.success = false;
      }, 2000);

      // Prevent the default action
      clickEvent.preventDefault();
    },
  },
  mounted() {
    this.$el.addEventListener('click', this.listener);
  },
  destroyed() {
    this.$el.removeEventListener('click', this.listener);
  },
};
</script>

<style scoped>
  .photo_copy-btn {
    border-radius: 3px;
    width: 32%;
    background: #4a69ca;
  }
</style>
