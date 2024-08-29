<!--
Present users with a way to change the app theme between three options:
light, dark and system.
-->

<script setup lang="ts">
import { useI18n } from "#imports"

import { computed, type ComputedRef } from "vue"

import VIcon from "~/components/VIcon/VIcon.vue"
import VSelectField, {
  type Choice,
} from "~/components/VSelectField/VSelectField.vue"

/**
 * `ActualColorMode` is the evaluated form of `ColorMode`.
 *
 * It's value is the same as `ColorMode` for light and dark color modes
 * but for the system color mode, it evaluates to either depending on
 * the user's system theme.
 */
type ActualColorMode = "light" | "dark"

const THEME_ICON_NAME = Object.freeze({
  light: "sun",
  dark: "moon",
})

const colorMode = computed({
  get: () => {
    // TODO: Get the value from the UI store.
    return "light"
  },
  set: (value) => {
    // TODO: Set the value to the UI store.
    console.log(value)
  },
})
const actualColorMode: ComputedRef<ActualColorMode> = computed(() => {
  // TODO: Evaluate the actual color mode.
  // This should update when the user changes the system theme.
  return "light"
})
const currentThemeIcon = computed(() => THEME_ICON_NAME[actualColorMode.value])

const i18n = useI18n({ useScope: "global" })
const choices: Choice[] = [
  { key: "dark", text: i18n.t("theme.choices.dark") },
  { key: "light", text: i18n.t("theme.choices.light") },
  { key: "system", text: i18n.t("theme.choices.system") },
]
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
