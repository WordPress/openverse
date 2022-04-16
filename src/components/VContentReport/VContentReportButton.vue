<template>
  <VButton
    variant="plain"
    class="report-button font-semibold text-dark-charcoal-70"
  >
    <span class="text-sr md:text-base md:hidden">{{
      $t('media-details.content-report.short')
    }}</span>
    <span class="text-sr md:text-base hidden md:inline">{{
      $t('media-details.content-report.long')
    }}</span>
    <VIcon :icon-path="icons.flag" class="ms-2" />
  </VButton>
</template>

<script>
import { defineComponent } from '@nuxtjs/composition-api'

import VIcon from '~/components/VIcon/VIcon.vue'
import VButton from '~/components/VButton.vue'

import flagIcon from '~/assets/icons/flag.svg'

export default defineComponent({
  name: 'VContentReportButton',
  components: { VButton, VIcon },
  setup() {
    return {
      icons: {
        flag: flagIcon,
      },
    }
  },
})
</script>

<style scoped>
.report-button {
  @apply px-0;
}
</style>
