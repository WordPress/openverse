<script setup lang="ts">
import { useI18n } from "#imports"
import { computed } from "vue"

import VIcon from "~/components/VIcon/VIcon.vue"
import VSelectField, {
  type Choice,
} from "~/components/VSelectField/VSelectField.vue"

import type { LocaleObject } from "@nuxtjs/i18n"

/**
 * Presents a way for the users to change the app locale and use a translated
 * version of the app.
 */

const i18n = useI18n({ useScope: "global" })
const locale = computed({
  get: () => i18n.locale.value,
  set: (value) => {
    i18n.setLocale(value)
  },
})
const choices = computed<Choice[]>(() =>
  (i18n.locales.value as LocaleObject[])
    .map((locale: LocaleObject) => ({
      key: locale.code,
      text: locale.nativeName,
    }))
    .sort((a, b) => a.key.localeCompare(b.key))
)
</script>

<template>
  <VSelectField
    v-model="locale"
    field-id="language"
    :choices="choices"
    :blank-text="$t('language.language')"
    :label-text="$t('language.language')"
  >
    <template #start>
      <VIcon name="globe" />
    </template>
  </VSelectField>
</template>
