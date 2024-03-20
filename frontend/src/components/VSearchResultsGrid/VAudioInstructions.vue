<template>
  <VSnackbar size="large" :is-visible="isSnackbarVisible">
    <i18n :path="`${i18nPrefix}.text`" tag="p">
      <template v-for="keyboardKey in keyboardKeys" #[keyboardKey]>
        <kbd :key="keyboardKey" class="font-sans">{{
          $t(`${i18nPrefix}.${keyboardKey}`)
        }}</kbd>
      </template>
    </i18n>
  </VSnackbar>
</template>
<script lang="ts">
import { computed, defineComponent, type PropType } from "vue"

import { useAudioSnackbar } from "~/composables/use-audio-snackbar"

import VSnackbar from "~/components/VSnackbar.vue"

export default defineComponent({
  name: "VAudioInstructions",
  components: { VSnackbar },
  props: {
    kind: {
      type: String as PropType<"all" | "audio">,
      required: true,
    },
  },
  setup(props) {
    const { isVisible: isSnackbarVisible } = useAudioSnackbar()

    const keyboardKeys = computed(() =>
      props.kind === "all" ? ["spacebar"] : ["spacebar", "left", "right"]
    )

    const i18nPrefix = computed(() => {
      return props.kind === "all"
        ? "allResults.snackbar"
        : "audioResults.snackbar"
    })

    return {
      keyboardKeys,
      isSnackbarVisible,
      i18nPrefix,
    }
  },
})
</script>
