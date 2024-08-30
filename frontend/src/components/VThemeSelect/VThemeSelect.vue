<!--
Present users with a way to change the app theme between three options:
light, dark and system.
-->

<script setup lang="ts">
import { useI18n } from "#imports"

import { computed, type ComputedRef } from "vue"
import { usePreferredColorScheme } from "@vueuse/core"

import { useUiStore } from "~/stores/ui"

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

/**
 * Get the user's preferred color scheme at the OS level. If the user
 * has not set an OS level preference, we fall back to light mode.
 */
const preferredColorScheme: ComputedRef<ActualColorMode> = computed(() => {
  const pref = usePreferredColorScheme()
  return pref.value === "no-preference" ? "light" : pref.value
})

/**
 * Get the user's preferred color scheme at the app level. If the user
 * has set the color mode to "system", we fall back to the OS level
 * preference.
 */
const actualColorMode: ComputedRef<ActualColorMode> = computed(() =>
  colorMode.value === "system" ? preferredColorScheme.value : colorMode.value
)

/**
 * The icon always reflects the actual theme applied to the site.
 * Therefore, it must be based on the value of `actualColorMode`.
 */
const currentThemeIcon = computed(() => THEME_ICON_NAME[actualColorMode.value])

/**
 * The choices are computed because the text for the color mode choice
 * "system" is dynamic and reflects the user's preferred color scheme at
 * the OS-level.
 */
const choices: ComputedRef<Choice[]> = computed(() => {
  const systemText = `${i18n.t(`theme.choices.system`)} (${THEME_TEXT[preferredColorScheme.value]})`
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
