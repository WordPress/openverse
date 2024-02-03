<template>
  <VButton
    :id="id"
    type="button"
    variant="filled-dark"
    size="small"
    class="label-bold flex-shrink-0"
    :disabled="!doneHydrating"
    :data-clipboard-target="el"
  >
    <span v-if="!success">
      {{ t("mediaDetails.reuse.copyLicense.copyText") }}
    </span>
    <span v-else>
      {{ t("mediaDetails.reuse.copyLicense.copied") }}
    </span>
  </VButton>
</template>

<script setup lang="ts">
import { useNuxtApp } from "#imports"

import Clipboard from "clipboard"

import { onBeforeUnmount, onMounted, ref } from "vue"

import { useHydrating } from "~/composables/use-hydrating"

import VButton from "~/components/VButton.vue"

const props = defineProps<{
  el: string
  id: string
}>()

const emit = defineEmits<{
  copied: []
  "copy-failed": []
}>()

const {
  $i18n: { t },
} = useNuxtApp()

const clipboard = ref<Clipboard | null>(null)
const success = ref(false)

function setFocusOnButton(): void {
  const button = document.getElementById(props.id)
  if (button) {
    button.focus()
  }
}

const onCopySuccess = (e: Clipboard.Event) => {
  success.value = true
  emit("copied")

  setTimeout(() => {
    success.value = false
  }, 2000)

  e.clearSelection()

  /* Set the focus back on the button */
  setFocusOnButton()
}
const onCopyError = (e: Clipboard.Event) => {
  emit("copy-failed")
  e.clearSelection()

  /* Restore focus on the button */
  setFocusOnButton()
}

onMounted(() => {
  clipboard.value = new Clipboard(`#${props.id}`)
  clipboard.value.on("success", onCopySuccess)
  clipboard.value.on("error", onCopyError)
})

onBeforeUnmount(() => clipboard.value?.destroy())

const { doneHydrating } = useHydrating()
</script>
