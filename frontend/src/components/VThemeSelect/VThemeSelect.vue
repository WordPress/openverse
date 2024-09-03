<!--
Present users with a way to change the app theme between three options:
light, dark and system.
-->

<script setup lang="ts">
import { useI18n, useDarkMode } from "#imports"

import { computed, type ComputedRef } from "vue"

import { useUiStore } from "~/stores/ui"

import VIcon from "~/components/VIcon/VIcon.vue"
import VSelectField, {
  type Choice,
} from "~/components/VSelectField/VSelectField.vue"

const i18n = useI18n({ useScope: "global" })
const uiStore = useUiStore()

const THEME_ICON_NAME = Object.freeze({
  light: "sun",
  dark: "moon",
})

const THEME_TEXT = {
  light: i18n.t(`theme.choices.light`),
  dark: i18n.t(`theme.choices.dark`),
}

const colorMode = computed({
  get: () => uiStore.colorMode,
  set: (value) => {
    uiStore.setColorMode(value)
  },
})

const darkMode = useDarkMode()

/**
 * The icon always reflects the actual theme applied to the site.
 * Therefore, it must be based on the value of `effectiveColorMode`.
 */
const currentThemeIcon = computed(
  () => THEME_ICON_NAME[darkMode.effectiveColorMode.value]
)

/**
 * The choices are computed because the text for the color mode choice
 * "system" is dynamic and reflects the user's preferred color scheme at
 * the OS-level.
 */
const choices: ComputedRef<Choice[]> = computed(() => {
  const systemText = `${i18n.t(`theme.choices.system`)} (${THEME_TEXT[darkMode.osColorMode.value]})`
  return [
    { key: "light", text: THEME_TEXT.light },
    { key: "dark", text: THEME_TEXT.dark },
    { key: "system", text: systemText },
  ]
})
</script>

<template>
  <VSelectField
    v-model="colorMode"
    field-id="theme"
    :choices="choices"
    :blank-text="$t('theme.theme')"
    :label-text="$t('theme.theme')"
    :show-selected="false"
  >
    <template #start>
      <VIcon :name="currentThemeIcon" />
    </template>
  </VSelectField>
</template>
