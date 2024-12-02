<!--
Present users with a way to change the app theme between three options:
light, dark and system.
-->

<script setup lang="ts">
import { useI18n, useDarkMode } from "#imports"

import { computed, ref, onMounted, watch, type Ref } from "vue"

import { useUiStore, type ColorMode } from "~/stores/ui"

import VIcon from "~/components/VIcon/VIcon.vue"
import VSelectField, {
  type Choice,
} from "~/components/VSelectField/VSelectField.vue"

const i18n = useI18n({ useScope: "global" })
const uiStore = useUiStore()

const THEME_ICON_NAME = Object.freeze({
  light: "sun",
  dark: "moon",
  system: "duotone",
})

const THEME_TEXT = {
  light: i18n.t(`theme.choices.light`),
  dark: i18n.t(`theme.choices.dark`),
  system: i18n.t(`theme.choices.system`),
}

const colorMode: Ref<ColorMode> = ref(uiStore.colorMode)
const handleUpdateModelValue = (value: string) => {
  uiStore.setColorMode(value as ColorMode)
}

const isDarkModeSeen = computed(() => uiStore.isDarkModeSeen)
const setIsDarkModeSeen = () => {
  uiStore.setIsDarkModeSeen(true)
}

const darkMode = useDarkMode()

const currentThemeIcon: Ref<"sun" | "moon" | "duotone"> = ref(
  THEME_ICON_NAME[darkMode.colorMode.value]
)

/**
 * The choices are computed because the text for the color mode choice
 * "system" is dynamic and reflects the user's preferred color scheme at
 * the OS-level.
 */
const choices: Ref<Choice[]> = ref([
  { key: "light", text: THEME_TEXT.light },
  { key: "dark", text: THEME_TEXT.dark },
  { key: "system", text: THEME_TEXT.system },
])

const updateRefs = () => {
  colorMode.value = uiStore.colorMode
  currentThemeIcon.value = THEME_ICON_NAME[darkMode.colorMode.value]
  choices.value[2].text = `${THEME_TEXT.system} (${THEME_TEXT[darkMode.osColorMode.value]})`
}

onMounted(updateRefs)
watch(() => [darkMode.colorMode.value, darkMode.osColorMode.value], updateRefs)
</script>

<template>
  <VSelectField
    :model-value="colorMode"
    field-id="theme"
    :choices="choices"
    :blank-text="$t('theme.theme')"
    :label-text="$t('theme.theme')"
    :show-selected="false"
    :show-new-highlight="!isDarkModeSeen"
    @click="setIsDarkModeSeen"
    @update:model-value="handleUpdateModelValue"
  >
    <template #start>
      <VIcon :name="currentThemeIcon" />
    </template>
  </VSelectField>
</template>
