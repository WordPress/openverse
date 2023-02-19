<template>
  <Component :is="as" ref="containerNode">
    <slot />
    <VTeleport to="skip-to-content">
      <VButton
        class="z-50 mt-2 ms-2 focus:fixed focus:absolute"
        :class="$style.skipButton"
        @click="skipToContent"
        >{{ $t("skip-to-content") }}</VButton
      >
    </VTeleport>
  </Component>
</template>

<script lang="ts">
import { defineComponent, PropType, ref } from "@nuxtjs/composition-api"
import { Portal as VTeleport } from "portal-vue"

import { ensureFocus, getFirstTabbableIn } from "~/utils/reakit-utils/focus"

import VButton from "~/components/VButton.vue"

/**
 * Demarcates the section that the "skip to content"
 * keyboard accessibility button should skip to.
 *
 * It also enables the button to appear on the page. If
 * this component isn't rendered on the page then the
 * button will not render.
 */
export default defineComponent({
  name: "VSkipToContentContainer",
  components: { VTeleport, VButton },
  props: {
    initialFocusNode: {
      type: process.server ? Object : HTMLElement,
      required: false,
    },
    as: {
      type: String as PropType<"div" | "main">,
      default: "div",
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
