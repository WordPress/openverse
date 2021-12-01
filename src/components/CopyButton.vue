<template>
  <button
    :id="id"
    type="button"
    class="button tiny donate"
    :data-clipboard-target="el"
  >
    <span v-if="!success">
      {{ $t('photo-details.copy.copy') }}
    </span>
    <span v-else>
      {{ $t('photo-details.copy.copied') }}
    </span>
  </button>
</template>

<script>
import Clipboard from 'clipboard'

export default {
  name: 'CopyButton',
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

<style lang="scss" scoped>
.button {
  @apply py-0 px-3 mt-4;
  font-size: 15px;
}
</style>
