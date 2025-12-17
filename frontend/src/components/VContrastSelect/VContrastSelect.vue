<!--
Present users with a way to change the app contrast between three options:
normal, high, and system.
-->

<script setup lang="ts">
import { useI18n } from "#imports"
import { ref, onMounted, watch, type Ref } from "vue"

import { useUiStore, type ContrastMode } from "~/stores/ui"
import { useHighContrast } from "~/composables/use-high-contrast"

import VIcon from "~/components/VIcon/VIcon.vue"
import VSelectField, {
  type Choice,
} from "~/components/VSelectField/VSelectField.vue"

const i18n = useI18n({ useScope: "global" })
const uiStore = useUiStore()

const CONTRAST_ICON_NAME = Object.freeze({
  normal: "eye-open",
  high: "filter",
  system: "duotone",
})

const CONTRAST_TEXT = {
  normal: i18n.t(`contrast.choices.normal`),
  high: i18n.t(`contrast.choices.high`),
  system: i18n.t(`contrast.choices.system`),
}

const contrastMode: Ref<ContrastMode> = ref(uiStore.contrastMode)
const handleUpdateModelValue = (value: string) => {
  uiStore.setContrastMode(value as ContrastMode)
}

const highContrast = useHighContrast()

const currentContrastIcon: Ref<"eye-open" | "filter" | "duotone"> = ref(
  CONTRAST_ICON_NAME[highContrast.contrastMode.value]
)

/**
 * The choices are computed because the text for the contrast mode choice
 * "system" is dynamic and reflects the user's preferred contrast setting at
 * the OS-level.
 */
const choices: Ref<Choice[]> = ref([
  { key: "normal", text: CONTRAST_TEXT.normal },
  { key: "high", text: CONTRAST_TEXT.high },
  { key: "system", text: CONTRAST_TEXT.system },
])

const updateRefs = () => {
  contrastMode.value = uiStore.contrastMode
  currentContrastIcon.value = CONTRAST_ICON_NAME[highContrast.contrastMode.value]
  const effectiveText = highContrast.effectiveContrastMode.value === "high" 
    ? CONTRAST_TEXT.high 
    : CONTRAST_TEXT.normal
  choices.value[2].text = `${CONTRAST_TEXT.system} (${effectiveText})`
}

onMounted(updateRefs)
watch([highContrast.contrastMode, highContrast.osHighContrast], updateRefs)
</script>

<template>
  <VSelectField
    :model-value="contrastMode"
    field-id="contrast"
    :choices="choices"
    :blank-text="$t('contrast.contrast')"
    :label-text="$t('contrast.contrast')"
    :show-selected="false"
    @update:model-value="handleUpdateModelValue"
  >
    <template #start>
      <VIcon :name="currentContrastIcon" />
    </template>
  </VSelectField>
</template>
