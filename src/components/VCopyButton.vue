<template>
  <VButton
    :id="id"
    type="button"
    variant="secondary"
    size="disabled"
    class="py-2 px-3 text-sr"
    :data-clipboard-target="el"
  >
    <span v-if="!success">
      {{ $t('media-details.reuse.copy-license.copy-text') }}
    </span>
    <span v-else>
      {{ $t('media-details.reuse.copy-license.copied') }}
    </span>
  </VButton>
</template>

<script>
import Clipboard from 'clipboard'

import VButton from '~/components/VButton.vue'

export default {
  name: 'VCopyButton',
  components: { VButton },
  props: {
    el: {
      required: true,
    },
    id: {
      required: true,
    },
  },
  data: () => ({
    success: false,
    clipboard: null,
  }),
  mounted() {
    this.clipboard = new Clipboard(`#${this.$props.id}`)
    this.clipboard.on('success', this.onCopySuccess)
    this.clipboard.on('error', this.onCopyError)
  },
  destroyed() {
    this.clipboard.destroy()
  },
  methods: {
    onCopySuccess(e) {
      this.success = true
      this.$emit('copied', { content: e.text })

      setTimeout(() => {
        this.success = false
      }, 2000)

      e.clearSelection()
    },
    onCopyError(e) {
      this.$emit('copyFailed')
      e.clearSelection()
    },
  },
}
</script>
