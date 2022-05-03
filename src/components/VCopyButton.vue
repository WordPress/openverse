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

<script lang="ts">
import Clipboard from 'clipboard'

import {
  defineComponent,
  onBeforeUnmount,
  onMounted,
  ref,
} from '@nuxtjs/composition-api'

import VButton from '~/components/VButton.vue'

export default defineComponent({
  name: 'VCopyButton',
  components: { VButton },
  props: {
    el: {
      type: String,
      required: true,
    },
    id: {
      type: String,
      required: true,
    },
  },
  emits: ['copied', 'copy-failed'],
  setup(props, { emit }) {
    const clipboard = ref<Clipboard | null>(null)
    const success = ref(false)

    const onCopySuccess = (e: Clipboard.Event) => {
      success.value = true
      emit('copied', { content: e.text })

      setTimeout(() => {
        success.value = false
      }, 2000)

      e.clearSelection()
    }
    const onCopyError = (e: Clipboard.Event) => {
      emit('copy-failed')
      e.clearSelection()
    }

    onMounted(() => {
      clipboard.value = new Clipboard(`#${props.id}`)
      clipboard.value.on('success', onCopySuccess)
      clipboard.value.on('error', onCopyError)
    })

    onBeforeUnmount(() => clipboard.value?.destroy())

    return {
      clipboard,
      success,
    }
  },
})
</script>
