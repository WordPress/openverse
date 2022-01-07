<template>
  <div>
    <span class="block px-6 mt-10 text-center">
      {{ $t('photo-details.content-report.submission-error') }}
    </span>
    <button class="button is-text tiny mt-4" type="button" @click="onBackClick">
      <VIcon :icon-path="chevronLeftIcon" class="me-2" />
      {{ $t('photo-details.content-report.back') }}
    </button>
  </div>
</template>

<script>
import { defineComponent } from '@nuxtjs/composition-api'
import VIcon from '~/components/VIcon/VIcon.vue'
import chevronLeftIcon from '~/assets/icons/chevron-left.svg'

export default defineComponent({
  name: 'VReportError',
  components: { VIcon },
  setup(_, { emit }) {
    const onBackClick = () => emit('back-click')
    return { chevronLeftIcon, onBackClick }
  },
})
</script>
