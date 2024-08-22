<script setup lang="ts">
import { computed } from "vue"

import { useAudioSnackbar } from "~/composables/use-audio-snackbar"

import VSnackbar from "~/components/VSnackbar.vue"

const props = defineProps<{ kind: "all" | "audio" }>()

const { isVisible: isSnackbarVisible } = useAudioSnackbar()

const keyboardKeys = computed(() =>
  props.kind === "all" ? ["spacebar"] : ["spacebar", "left", "right"]
)

const i18nPrefix = computed(() => {
  return props.kind === "all" ? "allResults.snackbar" : "audioResults.snackbar"
})
</script>

<template>
  <VSnackbar size="large" :is-visible="isSnackbarVisible">
    <i18n-t scope="global" :keypath="`${i18nPrefix}.text`" tag="p">
      <template
        v-for="keyboardKey in keyboardKeys"
        #[keyboardKey]
        :key="keyboardKey"
      >
        <kbd class="font-sans">{{ $t(`${i18nPrefix}.${keyboardKey}`) }}</kbd>
      </template>
    </i18n-t>
  </VSnackbar>
</template>
