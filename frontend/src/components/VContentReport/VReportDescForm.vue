<template>
  <label class="other-form block" for="description">
    <span class="flex flex-row items-center justify-between">
      <span>{{ $t("mediaDetails.contentReport.form.other.note") }}</span>
      <span>{{
        $t(`mediaDetails.contentReport.form.${reason}.subLabel`)
      }}</span>
    </span>
    <textarea
      id="description"
      v-model="text"
      class="mt-2 h-20 w-full border border-dark-charcoal-20 p-2 placeholder-dark-charcoal-70"
      :placeholder="
        $t(`mediaDetails.contentReport.form.${reason}.placeholder`).toString()
      "
      :required="isRequired"
      :minlength="isRequired ? 20 : 0"
      maxlength="500"
    />
  </label>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import { reasons, OTHER, ReportReason } from "~/constants/content-report"
import { defineEvent } from "~/types/emits"

export default defineComponent({
  name: "VReportDescForm",
  model: {
    prop: "content",
    event: "input",
  },
  props: {
    /**
     * the contents of the textarea
     */
    content: {
      type: String,
      default: "",
    },
    /**
     * the reason selected for reporting the content
     */
    reason: {
      type: String as PropType<ReportReason>,
      validator: (val: ReportReason) => reasons.includes(val),
    },
  },
  emits: {
    input: defineEvent<[string]>(),
  },
  setup(props, { emit }) {
    const text = computed({
      get: () => props.content,
      set: (val) => emit("input", val),
    })

    const isRequired = computed(() => props.reason === OTHER)

    return {
      isRequired,
      text,
    }
  },
})
</script>
