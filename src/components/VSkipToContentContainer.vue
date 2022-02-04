<template>
  <div ref="containerNode">
    <slot />
    <VTeleport to="skip-to-content">
      <VButton
        class="focus:fixed focus:absolute ms-2 mt-2 z-50"
        :class="$style.skipButton"
        @click="skipToContent"
        >{{ $t('skip-to-content') }}</VButton
      >
    </VTeleport>
  </div>
</template>

<script>
import { defineComponent, ref } from '@nuxtjs/composition-api'

import { getFirstTabbableIn } from 'reakit-utils/tabbable'
import { ensureFocus } from 'reakit-utils/ensureFocus'

import VTeleport from '~/components/VTeleport/VTeleport.vue'
import VButton from '~/components/VButton.vue'

/**
 * Demarcates the section that the "skip to content"
 * keyboard accessibility button should skip to.
 *
 * It also enables the button to appear on the page. If
 * this component isn't rendered on the page then the
 * button will not render.
 */
export default defineComponent({
  name: 'VSkipToContentContainer',
  components: { VTeleport, VButton },
  props: {
    initialFocusNode: {
      type: process.server ? Object : HTMLElement,
      required: false,
    },
  },
  setup(props) {
    const containerNode = ref()

    const skipToContent = () => {
      if (!(containerNode.value || props.initialFocusNode)) return
      const tabbable =
        props.initialFocusNode || getFirstTabbableIn(containerNode.value, true)
      ensureFocus(tabbable)
    }

    return { containerNode, skipToContent }
  },
})
</script>

<style module>
.skipButton:not(:focus) {
  @apply sr-only;
}
</style>
