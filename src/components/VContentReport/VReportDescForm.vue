<template>
  <label class="other-form block" for="description">
    <span class="flex flex-row justify-between items-center">
      <span>{{ $t('media-details.content-report.form.other.note') }}</span>
      <span>{{
        $t(`media-details.content-report.form.${reason}.sub-label`)
      }}</span>
    </span>
    <textarea
      id="description"
      v-model="text"
      class="h-20 w-full border border-dark-charcoal-20 placeholder-dark-charcoal-70 mt-2 p-2"
      :placeholder="
        $t(`media-details.content-report.form.${reason}.placeholder`)
      "
      :required="isRequired"
      :minlength="isRequired ? 20 : 0"
      maxlength="500"
    />
  </label>
</template>

<script>
import { computed, defineComponent } from '@nuxtjs/composition-api'

import { reasons } from '~/constants/content-report'

export default defineComponent({
  name: 'VReportDescForm',
  model: {
    prop: 'content',
    event: 'input',
  },
  props: {
    /**
     * the contents of the textarea
     */
    content: {
      type: String,
      default: '',
    },
    /**
     * the reason selected for reporting the content
     */
    reason: {
      type: String,
      validator: (val) => Object.values(reasons).includes(val),
    },
  },
  setup(props, { emit }) {
    const text = computed({
      get: () => props.content,
      set: (val) => emit('input', val),
    })

    const isRequired = computed(() => props.reason === reasons.OTHER)

    return {
      isRequired,
      text,
    }
  },
})
</script>
