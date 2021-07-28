<template>
  <div>
    <span class="block px-6 mt-10 text-center">
      {{ $t('photo-details.content-report.dmca.error') }}
    </span>
    <button
      class="button is-text tiny mt-4"
      @click="onBackClick()"
      @keyup.enter="onBackClick()"
    >
      <span>
        <i class="icon chevron-left mr-2" />
        {{ $t('photo-details.content-report.back') }}
      </span>
    </button>
  </div>
</template>

<script>
import { BACK_TO_REPORT_START } from '~/store-modules/mutation-types'

export default {
  name: 'ReportError',
  methods: {
    onBackClick() {
      this.$store.commit(BACK_TO_REPORT_START)
    },
  },
}
</script>
