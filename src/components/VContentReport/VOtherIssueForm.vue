<template>
  <form class="other-form">
    <h4 class="b-header">
      {{ $t('photo-details.content-report.title') }}
    </h4>
    <label for="description" class="mb-2">
      {{ $t('photo-details.content-report.issue-description') }}
      <textarea
        id="description"
        v-model="description"
        class="reason p-2 font-semibold border border-dark-charcoal w-full h-24 text-sm"
        :placeholder="$t('photo-details.content-report.placeholder')"
      />
    </label>

    <div class="flex flex-row justify-between align-end mt-4">
      <VButton
        type="button"
        variant="action-button"
        size="small"
        @click="onBackClick"
      >
        <VIcon :icon-path="chevronLeftIcon" class="me-2" />
        {{ $t('photo-details.content-report.back') }}
      </VButton>

      <VButton
        :disabled="!isValid"
        variant="secondary"
        class="float-right bg-trans-blue"
        @click="sendContentReport"
      >
        {{ $t('photo-details.content-report.submit') }}
      </VButton>
    </div>
  </form>
</template>

<script>
import { computed, defineComponent, ref } from '@nuxtjs/composition-api'
import chevronLeftIcon from '~/assets/icons/chevron-left.svg'
import VButton from '~/components/VButton.vue'
import VIcon from '~/components/VIcon/VIcon.vue'

export default defineComponent({
  name: 'OtherIssueForm',
  components: {
    VButton,
    VIcon,
  },
  setup(_, { emit }) {
    const onBackClick = () => {
      emit('back-click')
    }
    const description = ref('')
    const descriptionHasMoreThan20Chars = computed(
      () => description.value.length >= 20
    )

    const sendContentReport = () =>
      emit('send-report', { description: description.value })
    return {
      chevronLeftIcon,
      description,
      isValid: descriptionHasMoreThan20Chars,

      onBackClick,
      sendContentReport,
    }
  },
})
</script>
