<template>
  <label class="other-form block" for="description">
    <span class="flex flex-row items-center justify-between">
      <span>{{ t("mediaDetails.contentReport.form.other.note") }}</span>
      <span>{{ t(`mediaDetails.contentReport.form.${reason}.subLabel`) }}</span>
    </span>
    <textarea
      id="description"
      v-model="text"
      class="mt-2 h-20 w-full border border-dark-charcoal-20 p-2 placeholder-dark-charcoal-70"
      :placeholder="t(`mediaDetails.contentReport.form.${reason}.placeholder`)"
      :required="isRequired"
      :minlength="isRequired ? 20 : 0"
      maxlength="500"
    />
  </label>
</template>

<script setup lang="ts">
import { useNuxtApp } from "#imports"

import { computed } from "vue"

import { OTHER, ReportReason } from "~/constants/content-report"

const {
  $i18n: { t },
} = useNuxtApp()

const props = withDefaults(
  defineProps<{
    /**
     * the contents of the textarea
     */
    content?: string
    /**
     * the reason selected for reporting the content
     */
    reason: ReportReason
  }>(),
  {
    content: "",
  }
)

const emit = defineEmits<{
  /**
   * emits the updated content of the textarea
   */
  "update:content": [string]
}>()

const text = computed({
  get: () => props.content,
  set: (val) => emit("update:content", val),
})

const isRequired = computed(() => props.reason === OTHER)
</script>
