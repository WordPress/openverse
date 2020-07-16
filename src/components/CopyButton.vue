<template>
  <button
    :id="id"
    type="button"
    class="button tiny donate is-paddingless margin-top-normal padding-horizontal-normal"
    :data-clipboard-target="el"
  >
    <span v-if="!success">
      <i class="icon cc-share margin-right-small"></i>
      {{ $t('photo-details.copy.copy') }}
    </span>
    <span v-else>
      <i class="icon cc-share margin-right-small"></i>
      {{ $t('photo-details.copy.copied') }}
    </span>
  </button>
</template>

<script>
import Clipboard from 'clipboard'

export default {
  name: 'copy-button',
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
  mounted() {
    this.clipboard = new Clipboard(`#${this.$props.id}`)
    this.clipboard.on('success', this.onCopySuccess)
    this.clipboard.on('error', this.onCopyError)
  },
  destroyed() {
    this.clipboard.destroy()
  },
}
</script>
